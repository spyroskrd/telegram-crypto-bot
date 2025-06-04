import requests
import pycountry #πληροφοριες για νομισματα ονοματα και κωδικους
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os
from dotenv import load_dotenv

load_dotenv()


#συναρτηση που παιρνει απο το api ολες τις currencies, και με το pycountry παιιρνουμε τα ονοματα ολων, χρησιμοποοιοοντας μονο τοο 3ψηφιο ISO code,  αντι να τα γραφουμε ολα χειροκινητα ενα ενα
def currencies():
    url = f"https://api.coingecko.com/api/v3/simple/supported_vs_currencies"
    response= requests.get(url)

    #αν το api μασ απαντησει 200=οκ:
    if response.status_code == 200:
        currencycodes = response.json() #μετετρεψε το .json σε python list
        result = [] #αδεια προσωρινα λιστα, οπου θα μπουν τα αποτελεσματα.

        #η λουπα for παίρνει κάθε στοιχείο της λίστας currencycodes, ένα-ένα, και το αποθηκεύει προσωρινά στη μεταβλητή code.
        for code in currencycodes:
            code_upper = code.upper() #μετατρέπει πχ το 'usd' σε 'USD' (κεφαλαία γράμματα)
            currency = pycountry.currencies.get(alpha_3=code_upper) #προσπαθούμε να βρούμε το νόμισμα πχ με κωδικό 'USD'
            if currency: #αν το currency πηρε καποια τιμη:
                name = currency.name #Αν το βρήκαμε, παίρνουμε το πλήρες όνομα καλοντας το με το .name (π.χ. "US Dollar")
            else: #αν το currency ΔΕΝ πηρε καποια τιμη και εμεινε αδειο: 
                name = "Unknown" #Αν δεν βρήκαμε το νόμισμα, βάζουμε "Unknown"
            result.append(f"{code.upper()} - {name}") #το code.upper ειναι πχ USD , βαζειι παυλα - , και τοο name ειναι οτι βρηκε. Τα παιρνει ολα αυτα τα κανει string και τα βαζει στη λιστα result.
        return "\n".join(result) #επιστρεφειι τη λιστα με ολα τα νομισματα καιι τα ονοματα τους. με τη χρηση του .join μετατρεπουμε την λιστα σε string, για να αποφυγουμε τα "" και []
    
    else: #αν το api δεν απαντησει με 200:
        return ["Error fetching currencies."]

#συναρτηση με 2 παραμετρους, με το id του κρυπτο και με το νομισμα που συγκρινεται. (bitocoin και usd ειναι οι default επιλογες που εβαλα)
def getcoinprice(crypto_id='bitcoin', vs_currency='usd'):
    url = f"https://api.coingecko.com/api/v3/simple/price" #το url του api
    params = {    #ενα λεξικο που μεταφραζει τισ παραμετρους της συναρτησης
        'ids': crypto_id,
        'vs_currencies': vs_currency
    }

    response = requests.get(url, params=params) #αιτημα GET στο url του api , με τις παραμετρους που ορισαμε. η απαντηση αποθηκευεται στη μεταβλητη response
    
    if response.status_code == 200: #αν η απαντηση του  server ειναι οκ (200=οκ)
        try:
            data = response.json() #απο json κανοουμε την απαντηση σε λεξικο.
            price = data[crypto_id][vs_currency] #μπαινει στο λεξικο του crypto_id, μετα στο λεξικο του vs_currency (που ειναι μεσα στο crypto_id) και παιρνει τη τιμη του νομισματος. Η τιμη αποθηκευεται στη μεταβλητη price.
            return f"The price of {crypto_id.capitalize()} is {price} {vs_currency.upper()}." #επιστρεφει ενα μηνυμα
        except KeyError:
            return "Invalid coin or currency."
    else:
        return "Error fetching price." #εαν η απαντηση ΔΕΝ ειναι 200.
    
def gettopcoins(vs_currency='eur'):
    try:
        api = f"https://api.coingecko.com/api/v3/coins/markets"
        parameters = {
            "vs_currency": vs_currency,
            "order": "market_cap_desc",
            "per_page": 100,
            "page": 1,
            "price_change_percentage": "24h"
        }
        response = requests.get(api, params=parameters)
        
        data = response.json()
        sortedcoins = sorted(data, key=lambda x:['price_change_percentage_24h'] or 0, reverse=True)
        top5 = sortedcoins[:5]
        message = "Top 5 Current Crypto Coins in the last 24 hours:\n\n"
        for coin in top5:
            name = coin['name']
            symbol = coin['symbol'].upper()
            change = coin['price_change_percentage_24h']
            price = coin['current_price']
            message +=f"{name} ({symbol}): {change:.2f}% - {price} {vs_currency.upper()}\n"
        
        return message

    except Exception as errorcode:
        print("Error in /top", errorcode)
    except KeyError:
        return "Wrong currency"
    
#η συναρτηση που τρεχει οταν γραφουμε την εντολη /coin
async def coincommand(update, context):
    args = context.args #αυτο ειναιι η λιστα με τισ λεξεισ που γραφει ο χρηστης ΜΕΤΑ το /coin ...
    
    if len(args)==0: #αν μετα το /coin ο χρηστης δεν εχει γραψει κκατι τοτε βγγαλε αυτοο το μηνυμα.
        await update.message.reply_text("Please provide a coin and a currency, (/coin bitcoin eur)")
        return
    
    crypto_id = args[0] #δηλωνουμε τη θεση οποου θελουμε να γραφει οο χρηστης το ονομα του νομισματος ΠΧ /coin bitcoin. Το crypto_id αντιστοιχει στο argument 0, δηλαδη στη λεξη ακριβως μετα το /coin
    vs_currency = args[1] #το νομισμα, αντιστοοιχει στο argument 1,  δηλαδη στη δευτερη λεξη μετα το /coin. (/coin arg0 arg1) πχ (/coin bitcoin eur)..
    
    #η μεταβλητη result ειναι η συναρτηση που παιρνει τις τιμες των νομισματων.
    result = getcoinprice(crypto_id, vs_currency)

    #καλουμε την μεταβλητη που εχει την συναρτηση που παιρνει τις τιμεσ των νομισματων
    await update.message.reply_text(result)

#συναρτηση ποου τρεχει αν γραψουμε /help
async def helpcommand(update, context):
    await update.message.reply_text("Use /coin <crypto> <currency>\nUse /top <currency> to view the top 5 crypto in the last 24 hours\nUse /currencylist to view currencies.")

#συναρτηση ποου τρεχει αν γραψουμε /currencylist
async def currencylistcommand(update, context):
    await update.message.reply_text(currencies())#καλει την συνναρτηση currencies

async def topcommand(update, context):
    args = context.args #αυτο ειναιι η λιστα με τισ λεξεισ που γραφει ο χρηστης ΜΕΤΑ το /top ...
    
    if len(args)==0: #αν μετα το /top ο χρηστης δεν εχει γραψει κκατι τοτε βγγαλε αυτοο το μηνυμα.
        await update.message.reply_text("Please provide a currency, /top (currency)")
        return
    
    vs_currency = args[0]

    result = gettopcoins(vs_currency)

    await update.message.reply_text(result)
    

#το τοκεν του μποτ
token = os.getenv("TOKEN")

#ασυγχροονη συναρτηση start. η παραμετρος update περιεχει πληροφοριες για το ποιος εστειλε μηνυμα, τι εστειλε, ποτε κτλ. το context ειναι οι πληροφοριες του μποτ, ποτε φτιαχτηκε, τι λογισμικο τρεχει κττλ.
async def start(update, context):

    username = update.message.from_user.first_name #απο το update.message, παιρνει στοιοχεια του χρηστη, στην συγκεκριμενη περιπτωση το ονομα.
    await update.message.reply_text(f"Hello, {username}! Use /help to see all availale commands.") #εδω απανταει στον χρηστη (reply_text). χρησιμοποιω await ωστε να περιμενει την ολοκληρωση τησ αποστολης τοου μηνυματος χωρις να παγωνει ολο το προογραμα εδω, και να μποορει το προγραμμα να εκτελει και αλλεσ γραμμες κωδικα μεχρι να σταλθει το μηνυμα.

app = ApplicationBuilder().token(token).build() #χτιζουμε την εφαρμογη (build), με το τοκεν που δηλωσαμε για να συνδεθουμε στο μποτ.
app.add_handler(CommandHandler("start", start)) #βαζουμε εναν handler,  εναν διαχειριστη εντολων, ετσι ωστε οταν του γραφεις "start", να τρεχειι την μεταβλητη start.
app.add_handler(CommandHandler("coin", coincommand)) #αν γραψει /coin .... τρεχα την συναρτηση coincommand
app.add_handler(CommandHandler("help", helpcommand)) #αν γραψει /help τρεχει την συναρτησση helpcommand.
app.add_handler(CommandHandler("currencylist", currencylistcommand)) #αν γραψει /currencylist τρεχει τη συναρτηση currencylistcommand.
app.add_handler(CommandHandler("top", topcommand))
app.run_polling() #κανει RUN  to bot.


