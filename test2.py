import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

# add credentials to the account
creds = ServiceAccountCredentials.from_json_keyfile_name(
    'amh-bot-data-ba5ef1f539fe.json', scope)

# authorize the clientsheet
client = gspread.authorize(creds)

# get the instance of the Spreadsheet
sheet = client.open('answers')

# get the first sheet of the Spreadsheet
sheet_instance = sheet.get_worksheet(0)

print(sheet_instance.row_count)

records_data = sheet_instance.get_all_records()

# print(records_data)

records_df = pd.DataFrame.from_dict(records_data)

# view the top records
# print(records_df.head())


print(records_df.columns.get_loc("2"))

# sheet_instance.update_cell(2, 2, "0 1 0")
# sheet_instance.insert_cols([[4, 2]], 3)

print(records_df.size)
print(len(records_df.columns))

sheet_instance.update_cell(3, 2, 'Abebe')
