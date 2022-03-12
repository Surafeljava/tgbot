import os
import telebot
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY')
bot = telebot.TeleBot(API_KEY)


@bot.message_handler(commands=['Hello'])
def greet(message):
    bot.send_message(
        message.chat.id, "Hello There, This is a bot designed for the purpose of . . . ")


@bot.message_handler(commands=['?'])
def help(message):
    bot.reply_to(message, "Help is here . . .")


@bot.message_handler(commands=['hi'])
def hi(message):
    bot.reply_to(message, "Hii How are you doing? ")


print("Bot running . . .")


bot.polling()
