import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType;
import requests
from vk_api.longpoll import VkLongPoll, VkEventType
import random
from colorama import init, Fore, Back, Style
init()

token = "699dc8e890b683d8ad1b1f10c3ef5bd1611ca18f5dab744ab633c33011ba94d5b8ad16e9b89eea2e5726d"

users = [197575967];

session = requests.Session()
vk_session = vk_api.VkApi(token=token)

longpoll = VkLongPoll(vk_session)
vk = vk_session.get_api()

print("Spam machine launched")
from vk_api.longpoll import VkLongPoll, VkEventType
vk = vk_session.get_api()

for user in users:
	# try:
	mesId = random.randint(-2147483648, +2147483648)
	vk.messages.send(user_id=user, message="Тест", random_id = mesId)
	vk.messages.delete(message_ids=[mesId], group_id=201148024)
	print(Fore.GREEN + "Отправил сообщение " + str(user) + Fore.WHITE);
	# except vk_api.exceptions.ApiError:
		# print(Fore.RED + "Не разрешил сообщения " + str(user) + Fore.WHITE)