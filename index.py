from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import random
from datetime import datetime
import pandas as pd
import json

token = '699dc8e890b683d8ad1b1f10c3ef5bd1611ca18f5dab744ab633c33011ba94d5b8ad16e9b89eea2e5726d'
user_token = "abae8d0a4a0b919c6c21edc6b9116e8ee43c3aa491abefd920bd9ee4e8e82ccd0468f506bac995ab19f3b"

def right_pair(users_list, user):
	'''
	Функция для нахождения пары для данного пользователя. Из списка всех пользователей выбирается следующий.
	Если на вход подается последний, то функция возвращает первого пользователя.
	'''
	index = users_list.index(user) + 1
	if index > len(users_list)-1:
		index = 0
	try:
		return users_list[index]
	except ValueError:
		return 'Такой пользователь не найден'

def left_pair(users_list, user):
	'''
	Функция для нахождения пары для данного пользователя. Из списка всех пользователей выбирается следующий.
	Если на вход подается последний, то функция возвращает первого пользователя.
	'''
	index = users_list.index(user) - 1
	if index < 0:
		index = len(users_list)-1
	try:
		return users_list[index]
	except ValueError:
		return 'Такой пользователь не найден'

def send_keyboard(user_id, text):
	keyboard = VkKeyboard(one_time=False)
	keyboard.add_callback_button(label='Написать тайному Санте', color=VkKeyboardColor.POSITIVE, payload={"type": "санте"})
	keyboard.add_callback_button(label='Написать подопечному', color=VkKeyboardColor.PRIMARY, payload={'type': 'подопечному'})
	keyboard.add_line()
	keyboard.add_callback_button(label='Подарки', color=VkKeyboardColor.SECONDARY, payload={'type': 'узнать про подарки'})
	keyboard.add_callback_button(label='Написать модератору', color=VkKeyboardColor.NEGATIVE, payload={'type': 'модератору'})
	vk.messages.send(user_id=user_id, message=text, random_id=random.randint(
		-2147483648, +2147483648), keyboard=keyboard.get_keyboard())

def send_gift_keyboard(user_id, text):
	keyboard = VkKeyboard(one_time=False)
	keyboard.add_callback_button(label='Я подарил', color=VkKeyboardColor.POSITIVE, payload={"type": "подарил подарок"})
	keyboard.add_callback_button(label='Я получил', color=VkKeyboardColor.PRIMARY, payload={'type': 'получил подарок'})
	keyboard.add_line()
	keyboard.add_callback_button(label='Назад', color=VkKeyboardColor.SECONDARY, payload={'type': 'назад к основной клавиатуре'})
	vk.messages.send(user_id=user_id, message=text, random_id=random.randint(
		-2147483648, +2147483648), keyboard=keyboard.get_keyboard())

def createDb():
	'''
	Читает табличку и превращает ссылки в айдишники, который может съесть вк, разсылает всем сообщения о том, кто их тайный Санта
	'''
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

	res = input('Вы перемешали пользователей в secretSantaRegComputed.xlsx? Да | Нет: ')
	if res.lower() == 'да':
		userList = []
		df = pd.read_excel('secretSantaRegComputed.xlsx')
		idList = list(df['Ссылка на страничку VK:'])
		for i in range(len(df)):
			userList.append({'santa': left_pair(idList, idList[i]), 'ward': idList[i], 'text': f'Привет! Я узнал кому тебе дарить подарок!\nИмя подопечного: @id{idList[i]}({df.loc[i, :][2]})\nЖивет в {df.loc[i, :][4]}, {df.loc[i, :][5]}\nПожелания: {df.loc[i, :][6]}\n\nПодарки можно принести подопечному домой, передать через знакомых или оставить подарок в 224 ГК. Также там можно красиво упаковать подарки. И помни: подарок нужно подарить до 29 декабря!'})

		for user in userList:
			vk.messages.send(user_id=user['santa'], message=user['text'], random_id=random.randint(-2147483648, +2147483648))
	else:
		print('Перемешайте и перезапустите')

def echo(users, text, exceptlist=[]):
	'''
	Функция для написания всем пользователям какого-либо сообщения
	'''
	vk_n = vk_session
	for user_id in users:
		if user_id not in exceptlist:
			addressee = right_pair(users, user_id)
			userdata = vk_n.method("users.get", {"user_ids": addressee})
			addressee_name = userdata[0]['first_name'] + ' ' + userdata[0]['last_name']
			vk.messages.send(user_id=user_id, message=text,
							 random_id=random.randint(-2147483648, +2147483648))

def create_to_whom_dict(users):
	'''
	ОХУЕННАЯ ШТУКА
	
	Функция для создания переменной состояния для каждого пользователя. Для быстроты работы это захардкожено,
	но можно и использовать как функцию. Переменная состояния может быть 'empty', 'санте', 'подопечному'.
	Большой словарь был создан из-за того, что пока первый чел выбрал написать Санте и долго печатал или ждал, а второй чел выбрал написать подопечному,
	после чего первый отправил свое сообщение, то оно пойдет не Санте, а его подопечному.
	'''
	df = {}
	for user in users:
		df[user] = 'empty'
	return df

def create_list_of_who_gifted(users):
	'''
	По списке айдишников создает табличку с именем в вк, айди, ссылкой, и отметками подарил ли и получил ли пользователь подарок
	'''
	vk_for_getting_names = vk_session
	to_df = {}
	names = []
	ids1 = []
	hrefs = []
	gifts1 = []
	gifts2 = []
	for user in users:
		userdata = vk_for_getting_names.method("users.get", {"user_ids": user})
		names.append(userdata[0]['first_name'] + ' ' + userdata[0]['last_name'])
		ids1.append(user)
		hrefs.append(f'vk.com/id{user}')
		gifts1.append('нет')
		gifts2.append('нет')
	to_df['Имя'] = names
	to_df['ID'] = ids1
	to_df['Ссылка'] = hrefs
	to_df['Подарил'] = gifts1
	to_df['Получил'] = gifts2
	df = pd.DataFrame(to_df)
	print(df)
	df.to_excel('results.xlsx', index=False)

def tag_who_gift(dataframe, user_id, what):
	df = dataframe
	if what == 'подарил':
		df.loc[df['ID'] == user_id, 'Подарил'] = 'да'
	elif what == 'получил':
		df.loc[df['ID'] == user_id, 'Получил'] = 'да'
	elif what == 'не подарил':
		df.loc[df['ID'] == user_id, 'Подарил'] = 'нет'
	elif what == 'не получил':
		df.loc[df['ID'] == user_id, 'Получил'] = 'нет'
	return df

# session = requests.Session()
vk_session = VkApi(token=token)

longpoll = VkBotLongPoll(vk_session, group_id=201148024)
vk = vk_session.get_api()

def writeLogs(log):
	with open('logs.txt', 'a', encoding='utf-8') as f:
		f.write(log)

def main(users):
	logs = []
	'''
	Основная функция. Если пользователь пишет в группу, то Тайный Санта находит его пару функцией right_pair и отсылает ему сообщение пользователя и выводится сообщение об отправке.
	В терминале отображается история сообщений.
	'''
	print(str(datetime.now()) + ': Spam machine launched\n')
	vk_for_getting_names = vk_session
	# to_whom = {401054068: 'empty', 226609103: 'empty', 186100526: 'empty', 52042889: 'empty', 305096077: 'empty', 171963468: 'empty', 171907622: 'empty', 145634704: 'empty', 270929713: 'empty', 371029241: 'empty', 173236758: 'empty', 15841068: 'empty', 271412430: 'empty', 281968824: 'empty', 291285225: 'empty', 367244648: 'empty', 110822802: 'empty', 363693140: 'empty', 215682424: 'empty', 178614856: 'empty', 170692187: 'empty', 191013113: 'empty', 322798073: 'empty', 322881656: 'empty', 382988110: 'empty', 183805243: 'empty', 156627961: 'empty', 178012491: 'empty', 114341839: 'empty', 188878796: 'empty', 185400320: 'empty', 332066040: 'empty', 290438365: 'empty', 167689869: 'empty', 179273507: 'empty', 342072350: 'empty', 56727315: 'empty', 53391658: 'empty', 223479143: 'empty', 268597737: 'empty', 238101151: 'empty', 246012674: 'empty', 384674948: 'empty', 268417040: 'empty', 192627346: 'empty', 382721103: 'empty', 271412130: 'empty', 190738309: 'empty', 147328219: 'empty', 149190250: 'empty', 559371702: 'empty', 172818601: 'empty', 235130909: 'empty', 177402682: 'empty', 407227340: 'empty', 246648758: 'empty', 111079435: 'empty', 346949112: 'empty', 124453843: 'empty', 53937947: 'empty', 266812162: 'empty', 125468847: 'empty', 138731510: 'empty', 383187323: 'empty', 240828179: 'empty', 377933800: 'empty', 224047026: 'empty', 445507633: 'empty', 248402535: 'empty', 201193181: 'empty', 553602261: 'empty', 506826368: 'empty', 321371879: 'empty', 150674969: 'empty', 102847473: 'empty', 107613657: 'empty', 430390769: 'empty', 206645166: 'empty', 183567711: 'empty', 230990514: 'empty', 223118580: 'empty', 210061277: 'empty', 612609730: 'empty', 499902257: 'empty', 347734438: 'empty', 234539359: 'empty', 204643789: 'empty', 101244944: 'empty', 44549493: 'empty', 125413651: 'empty', 53032696: 'empty', 503153346: 'empty', 668892274: 'empty', 196460006: 'empty', 392890308: 'empty', 233794165: 'empty', 238270043: 'empty', 415375136: 'empty', 352205074: 'empty', 271464718: 'empty', 150260613: 'empty', 277165214: 'empty', 341114245: 'empty', 142867944: 'empty', 62720906: 'empty', 208137179: 'empty'}
	to_whom = create_to_whom_dict(users)
	for event in longpoll.listen():
		if event.type == VkBotEventType.MESSAGE_NEW:
			if event.obj.message['text'] != '':
				text = event.obj.message['text']
				user_id = event.obj.message['from_id']
				if event.from_user:
					try:
						if to_whom[user_id] == 'подопечному':
							# Если клиент пользователя не поддерживает callback-кнопки,
							# нажатие на них будет отправлять текстовые
							# сообщения. Т.е. они будут работать как обычные inline кнопки.

							addressee = right_pair(users, user_id)
							userdata = vk_for_getting_names.method("users.get", {"user_ids": addressee})
							addressee_name = userdata[0]['first_name'] + ' ' + userdata[0]['last_name']
							userdata = vk_for_getting_names.method("users.get", {"user_ids": user_id})
							addresser_name = userdata[0]['first_name'] + ' ' + userdata[0]['last_name']
							vk.messages.send(user_id=addressee, message="Хо-хо-хо! Сообщение от вашего тайного Санты:\n\n" + text, random_id=random.randint(-2147483648, +2147483648))
							send_keyboard(user_id, 'Я передал сообщение вашему подопечному')
							print(f'\n{str(datetime.now())}: {addresser_name} ({str(user_id)}) написал подопечному \"{str(text)}\" {addressee_name} ({str(addressee)})')
							# writeLogs(f'\n{str(datetime.now())}: {addresser_name} ({str(user_id)}) написал подопечному \"{str(text)}\" {addressee_name} ({str(addressee)})')

							to_whom[user_id] = 'empty'

						elif to_whom[user_id] == 'санте':
							addressee = left_pair(users, user_id)
							userdata = vk_for_getting_names.method("users.get", {"user_ids": addressee})
							addressee_name = userdata[0]['first_name'] + ' ' + userdata[0]['last_name']
							userdata = vk_for_getting_names.method("users.get", {"user_ids": user_id})
							addresser_name = userdata[0]['first_name'] + ' ' + userdata[0]['last_name']
							vk.messages.send(user_id=addressee, message="Хо-хо-хо! Сообщение от вашего подопечного:\n\n" + text, random_id=random.randint(-2147483648, +2147483648))
							send_keyboard(user_id, 'Я передал сообщение вашему тайному Санте')
							print(f'\n{str(datetime.now())}: {addresser_name} ({str(user_id)}) написал тайному Санте \"{str(text)}\" {addressee_name} ({str(addressee)})')
							# writeLogs(f'\n{str(datetime.now())}: {addresser_name} ({str(user_id)}) написал тайному Санте \"{str(text)}\" {addressee_name} ({str(addressee)})')

							to_whom[user_id] = 'empty'

						elif to_whom[user_id] == 'модератору':
							addressee = moderator_id
							userdata = vk_for_getting_names.method("users.get", {"user_ids": addressee})
							addressee_name = userdata[0]['first_name'] + ' ' + userdata[0]['last_name']
							userdata = vk_for_getting_names.method("users.get", {"user_ids": user_id})
							addresser_name = userdata[0]['first_name'] + ' ' + userdata[0]['last_name']
							vk.messages.send(user_id=moderator_id, message=f"Возникла проблема у {addresser_name}:\n\n {text}", random_id=random.randint(-2147483648, +2147483648))
							send_keyboard(user_id, 'Я передал сообщение модератору')
							print(f'\n{str(datetime.now())}: {addresser_name} ({str(user_id)}) написал модератору \"{str(text)}\" {addressee_name} ({str(addressee)})')
							# writeLogs(f'\n{str(datetime.now())}: {addresser_name} ({str(user_id)}) написал модератору \"{str(text)}\" {addressee_name} ({str(addressee)})')

							to_whom[user_id] = 'empty'

						else:
							send_keyboard(user_id, 'Выберите на панели внизу кому хотите отправить сообщение')
					except Exception as e:
						send_keyboard(user_id, 'Изините, что-то пошло не так, пожалуйста, попробуйте еще раз')
						print(f'{str(datetime.now())}: {e} ', end='')

			elif event.obj.message['attachments'] != []:
				user_id = event.obj.message['from_id']
				vk.messages.send(user_id=user_id, message="Извините, но из-за технических ограничений бот не может распознавать вложения. Напишите, пожалуйста текстом.", random_id=random.randint(-2147483648, +2147483648))

		# обрабатываем клики по callback кнопкам
		elif event.type == VkBotEventType.MESSAGE_EVENT:
			# vk.messages.sendMessageEventAnswer(
			#		 event_id=event.object.event_id,
			#		 user_id=event.object.user_id,
			#		 peer_id=event.object.peer_id,
			#		 event_data=json.dumps(event.object.payload)
			#	 )
			user_id = event.obj['user_id']
			if event.object.payload.get('type') == 'подопечному':
				to_whom[user_id] = 'подопечному'
				vk.messages.send(user_id=user_id, message='Наберите сообщение подопечному, а я его отправлю', random_id=random.randint(-2147483648, +2147483648))
			elif event.object.payload.get('type') == 'санте':
				to_whom[user_id] = 'санте'
				vk.messages.send(user_id=user_id, message='Наберите сообщение тайному Санте, а я его отправлю', random_id=random.randint(-2147483648, +2147483648))
			elif event.object.payload.get('type') == 'модератору':
				to_whom[user_id] = 'модератору'
				vk.messages.send(user_id=user_id, message='Наберите сообщение модератору, а я его отправлю', random_id=random.randint(-2147483648, +2147483648))

			elif event.object.payload.get('type') == 'узнать про подарки':
				send_gift_keyboard(user_id, 'Укажите подарили ли вам подарок, или его подарили вы. А может, и все вместе.')
			elif event.object.payload.get('type') == 'подарил подарок':
				df = pd.read_excel('results.xlsx')
				tag_who_gift(df, user_id, 'подарил')
				df.to_excel('results.xlsx', index=False)
				send_keyboard(user_id, 'Я отметил, что вы подарили подарок')
				userdata = vk_for_getting_names.method("users.get", {"user_ids": user_id})
				addresser_name = userdata[0]['first_name'] + ' ' + userdata[0]['last_name']
				print(f'\n{str(datetime.now())}: {addresser_name} ({user_id}) подарил подарок')
			elif event.object.payload.get('type') == 'получил подарок':
				df = pd.read_excel('results.xlsx')
				tag_who_gift(df, user_id, 'получил')
				df.to_excel('results.xlsx', index=False)
				send_keyboard(user_id, 'Я отметил, что вы получили подарок')
				userdata = vk_for_getting_names.method("users.get", {"user_ids": user_id})
				addresser_name = userdata[0]['first_name'] + ' ' + userdata[0]['last_name']
				print(f'\n{str(datetime.now())}: {addresser_name} ({user_id}) получил подарок')
			elif event.object.payload.get('type') == 'назад к основной клавиатуре':
				send_keyboard(user_id, 'Выберите на панели внизу кому хотите отправить сообщение')

def sendResponse(message):
	'''
	При написании боту любого текстового сообщения, отвечает ему единожды. Айди юзера записывается в файл sendedUsers и если он уэе записан, то ничего не отправляет.
	Сделано из-за того, что после регистрации челы могут что-то спросить, бот ответит на сообщение и сообщение будет прочитанным
	'''
	print(str(datetime.now()) + ': Spam machine launched\n')
	vk_for_getting_names = vk_session
	for event in longpoll.listen():
		if event.type == VkBotEventType.MESSAGE_NEW:
			if event.obj.message['text'] != '':
				text = event.obj.message['text']
				user_id = event.obj.message['from_id']
				with open("sendedUsers.txt", "r", encoding='utf-8') as sendedUsersFile:
					sendedUsers = sendedUsersFile.read().split('\n')
				if event.from_user:
					if (str(user_id) not in sendedUsers):
						vk.messages.send(user_id=user_id, message=message, random_id=random.randint(-2147483648, +2147483648))
						print(f'{datetime.now()}\tВыслал форму\thttps://vk.com/id{user_id}')
						sendedUsers.append(user_id)
						userInfo = vk.users.get(user_ids=user_id)[0]
						with open("sendedUsers.txt", "a", encoding='utf-8') as sendedUsersFile:
							sendedUsersFile.write(f"{user_id}\n")
					else:
						print(f'{datetime.now()}\tЯ уже высылал форму\thttps://vk.com/id{user_id}')
			elif event.obj.message['attachments'] != []:
				# print(event.obj.message['attachments'][0])
				# for attachment in event.obj.message['attachments']:
				# 	print(attachment['type'], attachment['images'][-1]['url'])
				# if event.obj.message['attachments'][0]['type'] == 'sticker':
				# 	print(event.obj.message['attachments'][0]['sticker']['images'][-1]['url'])
				user_id = event.obj.message['from_id']
				vk.messages.send(user_id=user_id, message="Извините, но из-за технических ограничений бот не может распознавать вложения. Напишите, пожалуйста текстом.", random_id=random.randint(-2147483648, +2147483648))

moderator_id = 197575967
users = [374498079, 159370300, 269979603, 434541190, 150422569, 625436250, 100956113, 559371702, 262673081, 132159952, 163177089, 145634704, 53008666, 226231873, 234539359, 201214709, 322798073, 305096077, 505302564, 202258317, 65704008, 499398594, 249335867, 298655683, 416409141, 2153814, 289778686, 540758297, 499640518, 81833709, 165594890, 314458131, 575739185, 374509951, 346949112, 59222745, 489341282, 173533022, 228232081, 192627346, 62720906, 245770683, 744636515, 182878754, 143778117, 444273691, 206645166, 270929713, 173356739, 175870436, 54794134, 399736264, 262030809, 359014722, 153740791, 188878796, 445507633, 398521668, 168423391, 746385852, 139824245, 323016134, 277633495, 584730627, 464985117, 62949881, 352205074, 171510325, 384674948, 528371803, 630808264, 234264762, 367510036, 225828814, 171907622, 300279491, 277165214, 357358069]

# Основная хуйня
mode = 'main' # main | response | createList
if mode != 'createList':
	while True:
		try:
			if mode == 'main':
				main(users) # Основная функция
			elif mode == 'response':
				sendResponse(message) # Это функция для рассылки сообщения по типу "Привет, зарегайся в форме" если боту что-то пишут
		except Exception as e:
			print(f'{str(datetime.now())}: {e}\n')

else:
	create_list_of_who_gifted(users) # Если нужно создать список людей с отметками подарили ли они и получили ли подарок

# Ход действий:
# 1. Запустить бота на sendResponse с сообщением "Для участия зарегайтесь в гугл форме"
# 2. Получить челов из формы, перетасовать их, разослать им сообщения о том, кто их подопечный и о начале игры
# 3. Записать их айдишники в список users в порядке, в котором они стоят в перетасованной табличке
# 4. Запустить create_list_of_who_gifted
# 5. Запустить main

'''
Santa's Black List
Костина Дина Евгеньевна		https://vk.com/id415375136
Зиновьев Егор Сергеевич		https://vk.com/id186100526
Кирик Игорь Дмитриевич 		https://vk.com/id171963468
Константинова Ирина Юрьевна	https://vk.com/id371029241
Новоселова Дарья Сергеевна 	https://vk.com/id342072350
Груздева Юлия Андреевна 	https://vk.com/id102847473
Трубачев Илья Игоревич		https://vk.com/id107613657
'''