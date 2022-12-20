from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
# import requests
import random
from datetime import datetime
import pandas as pd
import json

token = '3f00e8ac3d8055c8651604bdfca2ee26733d32c1ca8a0b829435231b7bd5321beced743a55a409f9dd24c'
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


def echo(users, text, exceptlist=[]):
	'''
	Функция для написания всем пользователям какого-нибо сообщения
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
	vk_for_getting_names = vk_session
	to_df = {}
	names = []
	ids1 = []
	gifts1 = []
	gifts2 = []
	for user in users:
		print(user)
		userdata = vk_for_getting_names.method("users.get", {"user_ids": user})
		names.append(userdata[0]['first_name'] + ' ' + userdata[0]['last_name'])
		ids1.append(user)
		gifts1.append('нет')
		gifts2.append('нет')
	to_df['Имя'] = names
	to_df['ID'] = ids1
	to_df['Подарил'] = gifts1
	to_df['Получил'] = gifts2
	df = pd.DataFrame(to_df)
	print(df)
	df.to_csv('C:/Users/Timur/Desktop/secret_santa/results.csv', index=False)
	df.to_excel('C:/Users/Timur/Desktop/secret_santa/results.xlsx', index=False)

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

longpoll = VkBotLongPoll(vk_session, group_id=183683217)
vk = vk_session.get_api()


def new_main(users):
	'''
	Основная функция. Если пользователь пишет в группу, то Тайный Санта находит его пару функцией right_pair и отсылает ему сообщение пользователя и выводится сообщение об отправке.
	В терминале отображается история сообщений.
	'''
	print(str(datetime.now()) + ': Spam machine launched\n')
	vk_for_getting_names = vk_session
	to_whom = {401054068: 'empty', 226609103: 'empty', 186100526: 'empty', 52042889: 'empty', 305096077: 'empty', 171963468: 'empty', 171907622: 'empty', 145634704: 'empty', 270929713: 'empty', 371029241: 'empty', 173236758: 'empty', 15841068: 'empty', 271412430: 'empty', 281968824: 'empty', 291285225: 'empty', 367244648: 'empty', 110822802: 'empty', 363693140: 'empty', 215682424: 'empty', 178614856: 'empty', 170692187: 'empty', 191013113: 'empty', 322798073: 'empty', 322881656: 'empty', 382988110: 'empty', 183805243: 'empty', 156627961: 'empty', 178012491: 'empty', 114341839: 'empty', 188878796: 'empty', 185400320: 'empty', 332066040: 'empty', 290438365: 'empty', 167689869: 'empty', 179273507: 'empty', 342072350: 'empty', 56727315: 'empty', 53391658: 'empty', 223479143: 'empty', 268597737: 'empty', 238101151: 'empty', 246012674: 'empty', 384674948: 'empty', 268417040: 'empty', 192627346: 'empty', 382721103: 'empty', 271412130: 'empty', 190738309: 'empty', 147328219: 'empty', 149190250: 'empty', 559371702: 'empty', 172818601: 'empty', 235130909: 'empty', 177402682: 'empty', 407227340: 'empty', 246648758: 'empty', 111079435: 'empty', 346949112: 'empty', 124453843: 'empty', 53937947: 'empty', 266812162: 'empty', 125468847: 'empty', 138731510: 'empty', 383187323: 'empty', 240828179: 'empty', 377933800: 'empty', 224047026: 'empty', 445507633: 'empty', 248402535: 'empty', 201193181: 'empty', 553602261: 'empty', 506826368: 'empty', 321371879: 'empty', 150674969: 'empty', 102847473: 'empty', 107613657: 'empty', 430390769: 'empty', 206645166: 'empty', 183567711: 'empty', 230990514: 'empty', 223118580: 'empty', 210061277: 'empty', 612609730: 'empty', 499902257: 'empty', 347734438: 'empty', 234539359: 'empty', 204643789: 'empty', 101244944: 'empty', 44549493: 'empty', 125413651: 'empty', 53032696: 'empty', 503153346: 'empty', 668892274: 'empty', 196460006: 'empty', 392890308: 'empty', 233794165: 'empty', 238270043: 'empty', 415375136: 'empty', 352205074: 'empty', 271464718: 'empty', 150260613: 'empty', 277165214: 'empty', 341114245: 'empty', 142867944: 'empty', 62720906: 'empty', 208137179: 'empty'}
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

							to_whom[user_id] = 'empty'

						else:
							send_keyboard(user_id, 'Выберите на панели внизу кому хотите отправить сообщение')
					except Exception as e:
						send_keyboard(user_id, 'Изините, что-то пошло не так, пожалуйста, попробуйте еще раз')
						print(f'{str(datetime.now())}: {e} ', end='')

		# обрабатываем клики по callback кнопкам
		elif event.type == VkBotEventType.MESSAGE_EVENT:
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
				df = pd.read_csv('C:/Users/Timur/Desktop/secret_santa/results.csv')
				tag_who_gift(df, user_id, 'подарил')
				df.to_csv('C:/Users/Timur/Desktop/secret_santa/results.csv', index=False)
				send_keyboard(user_id, 'Я отметил, что вы подарили подарок')
			elif event.object.payload.get('type') == 'получил подарок':
				df = pd.read_csv('C:/Users/Timur/Desktop/secret_santa/results.csv')
				tag_who_gift(df, user_id, 'получил')
				df.to_csv('C:/Users/Timur/Desktop/secret_santa/results.csv', index=False)
				send_keyboard(user_id, 'Я отметил, что вы получили подарок')
			elif event.object.payload.get('type') == 'назад к основной клавиатуре':
				send_keyboard(user_id, 'Выберите на панели внизу кому хотите отправить сообщение')


moderator_id = 197575967
users = [197575967, 136227130]
# users = [401054068, 226609103, 186100526, 52042889, 305096077, 171963468, 171907622, 145634704, 270929713, 371029241, 173236758, 15841068, 271412430, 281968824, 291285225, 367244648, 110822802, 363693140, 215682424, 178614856, 170692187, 191013113, 322798073, 322881656, 382988110, 183805243, 156627961, 178012491, 114341839, 188878796, 185400320, 332066040, 290438365, 167689869, 179273507, 342072350, 56727315, 53391658, 223479143, 268597737, 238101151, 246012674, 384674948, 268417040, 192627346, 382721103, 271412130, 190738309, 147328219, 149190250, 559371702, 172818601, 235130909, 177402682, 407227340, 246648758, 111079435, 346949112, 124453843, 53937947, 266812162, 125468847, 138731510, 383187323, 240828179, 377933800, 224047026, 445507633, 248402535, 201193181, 553602261, 506826368, 321371879, 150674969, 102847473, 107613657, 430390769, 206645166, 183567711, 230990514, 223118580, 210061277, 612609730, 499902257, 347734438, 234539359, 204643789, 101244944, 44549493, 125413651, 53032696, 503153346, 668892274, 196460006, 392890308, 233794165, 238270043, 415375136, 352205074, 271464718, 150260613, 277165214, 341114245, 142867944, 62720906, 208137179]
# green = [226609103, 281968824, 291285225, 178614856, 170692187, 382988110, 178012491, 114341839, 188878796, 185400320, 290438365, 167689869, 179273507, 268597737, 238101151, 246012674, 177402682, 407227340, 246648758, 383187323, 445507633, 201193181, 206645166, 183567711, 223118580, 210061277, 44549493, 125413651, 271464718]

while True:
	try:
		new_main(users)
	except Exception as e:
		print(f'{str(datetime.now())}: {e}\n')
