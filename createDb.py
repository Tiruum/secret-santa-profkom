import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType;
import requests
from vk_api.longpoll import VkLongPoll, VkEventType
import random
import pandas as pd

token = "699dc8e890b683d8ad1b1f10c3ef5bd1611ca18f5dab744ab633c33011ba94d5b8ad16e9b89eea2e5726d"
session = requests.Session()
vk_session = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk_session)
vk = vk_session.get_api()

# Читает табличку и превращает ссылки в айдишники, который может съесть вк
df = pd.read_excel('secretSantaReg.xlsx')

for i in range(len(df['Ссылка на страничку VK:'])):
	 href = vk.users.get(user_ids=((df['Ссылка на страничку VK:'][i]).split('/')[-1]))
	 print(df['Ссылка на страничку VK:'][i], end=" -> ")
	 try:
		 df.at[i, 'Ссылка на страничку VK:'] = href[0]['id']
	 except:
		 df.at[i, 'Ссылка на страничку VK:'] = 'еблан неправильно указал ссылку'
	 print(df['Ссылка на страничку VK:'][i], end="\n")
df.to_excel('secretSantaRegComputed.xlsx', index=False)

userList = []
df = pd.read_excel('secretSantaRegComputed.xlsx')
idList = list(df['Ссылка на страничку VK:'])
for i in range(len(df)):
	userList.append({'santa': left_pair(idList, idList[i]), 'ward': idList[i], 'text': f'Имя подопечного: @id{idList[i]}({df.loc[i, :][2]})\nЖивет в {df.loc[i, :][4]}, {df.loc[i, :][5]}\nПожелания: {df.loc[i, :][6]}'})

for user in userList:
	vk.messages.send(user_id=user['santa'], message='Подарки можно принести подопечному домой, передать через знакомых или оставить подарок в 224 ГК. Также там можно красиво упаковать подарки. И помни: подарок нужно подарить до 29 декабря!', random_id=random.randint(-2147483648, +2147483648))


# df = pd.read_excel('secretSantaRegComputed.xlsx')
# idList = list(df['Ссылка на страничку VK:'])
# print(idList)

# print(f'to_whom: {right_pair(idList, userId)}')