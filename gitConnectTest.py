from dotenv import load_dotenv
import os
import dropbox

import pandas as pd

load_dotenv()

API_KEY = os.getenv('API_KEY')
DROPBOX_TOKEN = os.getenv('DROPBOX_TOKEN')

dbx = dropbox.Dropbox(DROPBOX_TOKEN)
filename = '/Amhbot/users.csv'
# f, r = dbx.files_download(filename)
url = dbx.files_get_temporary_link(filename)

df = pd.read_csv(url.link)

print(df.head())
