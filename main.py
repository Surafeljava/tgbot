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


def updateTheAnswers(num, question, answer):
    ansFileName = './data/answers.csv'

    df = pd.read_csv(ansFileName)

    print(question)

    if num in df.columns:
        ans = df[num]
        all = ans.split()
        all.append(answer)
        df[num] = ' '.join(all)

        # save to csv file (updating the existing file)
        df.to_csv(ansFileName, encoding='utf-8', index=False)
    else:
        df[num] = answer

        # save to csv file (updating the existing file)
        df.to_csv(ansFileName, encoding='utf-8', index=False)


def updateTheUsers(userName, num):

    userFileName = './data/users.csv'

    udf = pd.read_csv(userFileName)

    if userName in udf.columns:
        userChecked = udf[userName][0].split()

        # add new value to this cell
        userChecked.append(num)
        udf[userName] = ' '.join(userChecked)

        # save to csv file (updating the existing file)
        udf.to_csv(userFileName, encoding='utf-8', index=False)
    else:
        # lets add the username
        udf[userName] = [num]

        # save to csv file (updating the existing file)
        udf.to_csv(userFileName, encoding='utf-8', index=False)


def query_handler(update, context):
    query = update.callback_query.data
    update.callback_query.answer()

    userFileName = './data/users.csv'
    dataFileName = './data/data.csv'

    user = update.callback_query.from_user
    userName = user['username']
    message = update.callback_query.message
    question = ' '.join(message['text'].split()[1:])
    num = message['text'].split()[0]

    udf = pd.read_csv(userFileName)

    df = pd.read_csv(dataFileName)
    data = df["sentence"]
    choosen = ''

    if("hate" in query):
        choosen = '1'
    else:
        choosen = '0'

    # update the questions here
    updateTheAnswers(num, question, choosen)

    # update the user contribution list here
    updateTheUsers(userName, num)

    context.bot.send_message(
        chat_id=update.effective_chat.id, text="""
        Do you want to continue?\nYes -> /continue\nNo -> /exit
        """)


def exit(update, context):
    update.message.reply_text(
        """Thank you for your kind contribution.""")


def checkIfInList(d, l):
    for i in l:
        if i == d:
            return True

    return False


def checkIfQuestionFullyAnnotated(num):

    ansFileName = './data/answers.csv'

    df = pd.read_csv(ansFileName)

    if num in df.columns:
        # check if full
        ans = df[num][0].split()
        if len(ans) < 5:
            return False
        else:
            return True
    else:
        return False


def hate_speech(update, context):
    user = update.message.from_user
    userName = user['username']
    udf = pd.read_csv("./data/users.csv")

    # print(udf.head())

    userChecked = []

    if userName in udf.columns:
        userChecked = udf[userName][0].split()

    df = pd.read_csv("./data/data.csv")
    data = df["sentence"]

    nxt = random.randint(0, len(data)-1)

    while(checkIfInList(str(nxt), userChecked) or checkIfQuestionFullyAnnotated(str(nxt))):
        nxt = random.randint(0, len(data)-1)

    buttons = [[InlineKeyboardButton("Hate Speech", callback_data="hate")], [
        InlineKeyboardButton("Not Hate Speech", callback_data="not_hate")]]

    context.bot.send_message(
        chat_id=update.effective_chat.id, reply_markup=InlineKeyboardMarkup(buttons), text=str(nxt) + ' ' + data[nxt],)


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

    updater.start_webhook(listen="0.0.0.0", port=PORT,
                          url_path=API_KEY, webhook_url=APP_NAME + API_KEY)
    updater.idle()


if __name__ == '__main__':
    main()
