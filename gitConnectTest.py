from github import Github
import pandas as pd

github = Github('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')
repository = github.get_user().get_repo('amhbotdata')

df = pd.read_csv('./data/users.csv')

# print(type(df))
# print(df.to_string(index=False))

# df.to_csv('./data/users.csv', encoding='utf-8', index=False)
# path in the repository
# filename = 'test.csv'
# # create with commit message
# f = repository.create_file(
#     filename, "create_file via PyGithub", df.to_csv(sep=',', index=False))


# path in the repository
filename = 'test.csv'
file = repository.get_contents(filename)
udf = pd.read_csv(file.download_url)

print(file.decoded_content.decode())
