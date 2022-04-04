import pandas as pd

fileName = "./data/users.csv"

udf = pd.read_csv(fileName)

userChecked = []

userName = "surafel"

val = '1 አንድ ትውልድ መርዝ ሲረጩ ኖረዋል ፡፡'

txt = ' '.join(val.split()[1:])

print(txt)

if userName in udf.columns:
    userChecked = udf[userName][0].split()
    # add new row to this column
    print(userChecked)
    userChecked.append("1")
    udf[userName] = ' '.join(userChecked)

    # udf[userChecked] = userChecked.append(pd.Series(10, index=[3]))
    udf.to_csv(fileName, encoding='utf-8', index=False)
else:
    # lets add the username
    udf[userName] = [8, 7]
    udf.to_csv(fileName, encoding='utf-8', index=False)

print(userChecked)

print(len(userChecked))

# print(udf)
# print(udf['abebe'])
# print(len(udf['abebe']))
