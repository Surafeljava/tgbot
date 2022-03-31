from cgitb import text
import os
import telebot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, PollHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, Poll, ReplyKeyboardMarkup, Update
from dotenv import load_dotenv
import pandas as pd
import random

import os
PORT = int(os.environ.get('PORT', 80))

load_dotenv()

API_KEY = os.getenv('API_KEY')


def get_chat_id(update, context):
    chat_id = -1
    if update.message is not None:
        chat_id = update.message.chat.id
    elif update.callback_query is not None:
        chat_id = update.callback_query.message.chat.id
    elif update.poll is not None:
        chat_id = context.bot_data[update.poll.id]

    return chat_id


def start(update, context):
    update.message.reply_text(
        """Hello! This is Amharic Senetiment Analysis servery bot.\n/continue
        """)


def help(update, context):
    update.message.reply_text("""
                              Use the following commands: 
                              
                              /start -> Welcome Message
                              /help -> To get instructions
                              /content -> To get contents
                              /hate -> To Classify hate speeches
                              """)


def is_answer_correct(update):
    answers = update.poll.options

    ret = False
    counter = 0

    for answer in answers:
        if answer.voter_count == 1 and \
                update.poll.correct_option_id == counter:
            ret = True
            break

        counter = counter + 1
    return ret


# def poll(update, context):
#     c_id = get_chat_id(update, context)
#     q = 'What is the capital of Italy?'
#     answers = ['Rome', 'London', 'Amsterdam']
#     message = context.bot.send_poll(
#         chat_id=c_id, question=q, options=answers, type=Poll.QUIZ, correct_option_id=0,
#         explanation='Well, honestly that depends on what you eat', explanation_parse_mode=telegram.ParseMode.MARKDOWN_V2,
#         open_period=15)


def content(update, context):
    c_id = get_chat_id(update, context)

    q = 'What is the capital of Italy?'
    answers = ['Rome', 'London', 'Amsterdam']
    message = context.bot.send_poll(
        chat_id=c_id, question=q, options=answers, type=Poll.QUIZ, correct_option_id=0)
    # update.message.reply_text("This is content information")


def handle_user_msg(update, context):
    update.message.reply_text(f"Your message is {update.message.text}.")


def hate_speech_classify(update, context):
    buttons = [[KeyboardButton("Next")], [KeyboardButton("Exit")]]
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="አንድ ትውልድ መርዝ ሲረጩ ኖረዋል ፡፡", reply_markup=ReplyKeyboardMarkup(buttons))


def query_handler(update, context):
    query = update.callback_query.data
    update.callback_query.answer()

    df = pd.read_csv("./data/data.csv")
    data = df["0"]
    # Write to the data here

    if("hate" in query):
        print("Hate Chosen")
    else:
        print("Not Hate Chosen")

    context.bot.send_message(
        chat_id=update.effective_chat.id, text="""
        Do you want to continue?\nYes -> /continue\nNo -> /exit
        """)


def exit(update, context):
    update.message.reply_text(
        """Thank you for your kind contribution.""")


def hate_speech(update, context):
    df = pd.read_csv("./data/data.csv")
    data = df["0"]

    nxt = random.randint(0, len(data)-1)

    buttons = [[InlineKeyboardButton("Hate Speech", callback_data="hate")], [
        InlineKeyboardButton("Not Hate Speech", callback_data="not_hate")]]

    context.bot.send_message(
        chat_id=update.effective_chat.id, reply_markup=InlineKeyboardMarkup(buttons), text=data[nxt],)


def main():
    """Starts the bot."""
    APP_NAME = 'https://amharic-tgbot.herokuapp.com/'  # Edit the heroku app-name

    updater = Updater(API_KEY, use_context=True)

    disp = updater.dispatcher

    disp.add_handler(CommandHandler("start", start))
    disp.add_handler(CommandHandler("help", help))
    # disp.add_handler(CommandHandler("poll", poll))
    disp.add_handler(CommandHandler("exit", exit))
    disp.add_handler(CommandHandler("continue", hate_speech))
    disp.add_handler(CallbackQueryHandler(query_handler))
    disp.add_handler(CommandHandler(
        "hate_classify", hate_speech_classify))
    disp.add_handler(PollHandler(
        content, pass_chat_data=True, pass_user_data=True))
    disp.add_handler(MessageHandler(
        Filters.text, handle_user_msg))

    # https: // amharic-tgbot.herokuapp.com/

    # updater.start_webhook(listen="0.0.0.0",
    #                       port=int(PORT),
    #                       url_path=API_KEY)
    # updater.bot.setWebhook('https://amharic-tgbot.herokuapp.com/' + API_KEY)

    # # updater.start_polling()
    # updater.idle()

    updater.start_webhook(listen="0.0.0.0", port=PORT,
                          url_path=API_KEY, webhook_url=APP_NAME + API_KEY)
    updater.idle()


if __name__ == '__main__':
    main()
