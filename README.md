#Telegram Crypto Bot

A simple telegram bot written in python, which gives back info about 
Cryptocurrencies.

## What is used?
- Python
- python-telegram-bot
- API requests
- Hosted on glitch.com

## How does it work?
- '/start' - A little welcoming message- prompts the user to use /help
- '/help' - List with all working commands
- '/coin <crypto> <currency'> - Tells the user how much a cryptocoin costs
- '/top <currency>' - Shows all top 5 cryptocoins in the last 24 hours, 
including price, precentage.
- '/currencylist' - Prints a full list of all available currencies.

## NOTE:
Inside the code, the token of the bot is not hard-coded, and is kept safe 
in a seperate file for security reasons. If you want to test this code on 
a bot of your OWN, insert its token inside the code.

After you connect the code with a bot, start by using the command:
python bot.py

PLEASE make sure you have the required libraries installed as listed in 
the requirements.txt file in order for the program to run


