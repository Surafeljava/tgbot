from oauth2client.service_account import ServiceAccountCredentials
import gspread
from cgitb import text
import os
import telebot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, PollHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, Poll, ReplyKeyboardMarkup, Update
from dotenv import load_dotenv
import pandas as pd
import random

from github import Github
import dropbox

import os

load_dotenv()

API_KEY = os.getenv('API_KEY')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
REPO_NAME = os.getenv('REPO_NAME')
DROPBOX_TOKEN = os.getenv('DROPBOX_TOKEN')

PORT = int(os.environ.get('PORT', 80))

##########################

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

# add credentials to the account
creds = ServiceAccountCredentials.from_json_keyfile_name(
    'amh-bot-data-ba5ef1f539fe.json', scope)

# authorize the clientsheet
client = gspread.authorize(creds)

########################


# github = Github(GITHUB_TOKEN)
# # github = Github("Surafeljava", "Surajava27",
# #                 'https://api.github.com/Surafeljava')

# # print(github)
# repository = github.get_user().get_repo(REPO_NAME)

# dbx = dropbox.Dropbox(DROPBOX_TOKEN)


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


def handle_user_msg(update, context):
    update.message.reply_text(f"Your message is {update.message.text}.")


def hate_speech_classify(update, context):
    buttons = [[KeyboardButton("Next")], [KeyboardButton("Exit")]]
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="አንድ ትውልድ መርዝ ሲረጩ ኖረዋል ፡፡", reply_markup=ReplyKeyboardMarkup(buttons))


def updateTheAnswers(num, question, answer):
    # ansFileName = './data/answers.csv'
    ansFileName = 'answers.csv'

    # df = pd.read_csv(ansFileName)
    # file = repository.get_contents(ansFileName)
    # df = pd.read_csv(file.download_url)

    sheet = client.open('answers')
    sheet_instance = sheet.get_worksheet(0)
    records_data = sheet_instance.get_all_records()
    df = pd.DataFrame.from_dict(records_data)

    if num in df.columns:
        ans = df[num]
        all = str(ans).split(' ')
        all.append(answer)
        df[num] = ' '.join(all)

        # save to csv file (updating the existing file)
        # df.to_csv(ansFileName, encoding='utf-8', index=False)
        # repository.update_file(
        #     ansFileName, "Updating Answer", df.to_csv(sep=',', index=False))

        cl = df.columns.get_loc(num)
        sheet_instance.update_cell(2, cl, ' '.join(all))

    else:
        df[num] = answer

        # save to csv file (updating the existing file)
        # df.to_csv(ansFileName, encoding='utf-8', index=False)
        # repository.update_file(
        #     ansFileName, "Updating Answer", df.to_csv(sep=',', index=False))

        # cl = df.columns.get_loc(num)
        sheet_instance.insert_cols([[num, answer]], len(df.columns))
        # sheet_instance.update_cell(cl, 2, ' '.join(all))


def updateTheUsers(userName, num):

    # userFileName = './data/users.csv'
    userFileName = 'users.csv'

    # udf = pd.read_csv(userFileName)
    # file = repository.get_contents(userFileName)
    # udf = pd.read_csv(file.download_url)

    sheet = client.open('users')
    sheet_instance = sheet.get_worksheet(0)
    records_data = sheet_instance.get_all_records()
    udf = pd.DataFrame.from_dict(records_data)

    if userName in udf.columns:
        userChecked = str(udf[userName][0]).split(' ')

        # add new value to this cell
        userChecked.append(num)
        udf[userName] = ' '.join(userChecked)

        d = ' '.join(userChecked)

        # save to csv file (updating the existing file)
        # udf.to_csv(userFileName, encoding='utf-8', index=False)
        # repository.update_file(
        #     userFileName, "Updating User", udf.to_csv(sep=',', index=False))

        print(d)

        vals = udf.columns.values.tolist()

        ind = vals.index(userName) + 1

        print(vals)
        print(ind)

        cl = udf.columns.get_loc(userName)
        sheet_instance.update_cell(2, ind, d)
    else:
        # lets add the username
        udf[userName] = [num]

        # save to csv file (updating the existing file)
        # udf.to_csv(userFileName, encoding='utf-8', index=False)
        # repository.update_file(
        #     userFileName, "Updating User", udf.to_csv(sep=',', index=False))

        sheet_instance.insert_cols(
            [[userName, num]], len(udf.columns))


def query_handler(update, context):
    query = update.callback_query.data
    update.callback_query.answer()

    user = update.callback_query.from_user
    userName = user['username']
    message = update.callback_query.message
    question = ' '.join(message['text'].split()[1:])
    num = message['text'].split()[0]

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

    # ansFileName = './data/answers.csv'
    ansFileName = 'answers.csv'

    # df = pd.read_csv(ansFileName)
    # file = repository.get_contents(ansFileName)
    # df = pd.read_csv(file.download_url)

    sheet = client.open('data')
    sheet_instance = sheet.get_worksheet(0)
    records_data = sheet_instance.get_all_records()
    df = pd.DataFrame.from_dict(records_data)

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

    # userFileName = './data/users.csv'
    # dataFileName = './data/data.csv'

    # userFileName = 'users.csv'
    # file = repository.get_contents(userFileName)
    # udf = pd.read_csv(file.download_url)
    sheet = client.open('users')
    sheet_instance = sheet.get_worksheet(0)
    records_data = sheet_instance.get_all_records()
    udf = pd.DataFrame.from_dict(records_data)

    # dataFileName = 'data.csv'
    # file = repository.get_contents(dataFileName)
    # df = pd.read_csv(file.download_url)

    sheet_data = client.open('data')
    sheet_instance_data = sheet_data.get_worksheet(0)
    records_data2 = sheet_instance_data.get_all_records()
    df = pd.DataFrame.from_dict(records_data2)

    # udf = pd.read_csv("./data/users.csv")

    # print(udf.head())

    userChecked = []

    print(userName)

    if userName in udf.columns:
        userChecked = str(udf[userName][0]).split(' ')

    # df = pd.read_csv("./data/data.csv")
    data = df["sentence"]

    nxt = random.randint(0, len(data)-1)

    while(checkIfInList(str(nxt), userChecked) or checkIfQuestionFullyAnnotated(str(nxt))):
        nxt = random.randint(0, len(data)-1)

    buttons = [[InlineKeyboardButton("Hate Speech", callback_data="hate")], [
        InlineKeyboardButton("Not Hate Speech", callback_data="not")]]

    context.bot.send_message(
        chat_id=update.effective_chat.id, reply_markup=InlineKeyboardMarkup(buttons), text=str(nxt) + ' ' + data[nxt],)


def main():
    """Starts the bot."""
    APP_NAME = 'https://amharic-tgbot.herokuapp.com/'  # Edit the heroku app-name

    updater = Updater(API_KEY, use_context=True)

    disp = updater.dispatcher

    disp.add_handler(CommandHandler("start", start))
    disp.add_handler(CommandHandler("help", help))
    disp.add_handler(CommandHandler("exit", exit))
    disp.add_handler(CommandHandler("continue", hate_speech))
    disp.add_handler(CallbackQueryHandler(query_handler))
    disp.add_handler(CommandHandler(
        "hate_classify", hate_speech_classify))
    disp.add_handler(MessageHandler(
        Filters.text, handle_user_msg))

    updater.start_webhook(listen="0.0.0.0", port=PORT,
                          url_path=API_KEY, webhook_url=APP_NAME + API_KEY)
    updater.idle()


if __name__ == '__main__':
    main()
