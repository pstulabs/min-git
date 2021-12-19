#!/usr/bin/python
import configparser  # парсинг конфигов
import functions as f
import time  # для типа данных "время"

# Получаем параметры из конфига
config = configparser.ConfigParser()

# циклом вызываем getUpdates с заданным периодом (в телеге есть параметр timeout для getupdates, но не понятно как он работает)
while True:
	config.read('properties', encoding='utf-8')
	time.sleep(int(config['Telegram']['REQ_INTERVAL']))
	try:
		in_message = f.getUpdates()
		if in_message is not None:
			WHITELIST = set([int(elem) for elem in (config['Telegram']['WHITELIST']).split(',')])
			user_id = in_message['user_id']
			data = in_message['data']
			if user_id in WHITELIST:  # проверяем доступ к боту по id юзера, спамеры нам не нужны
				# получаем настройки юзера из файла, потом можно прикрутить БД, если прям надо будет
				user_data = f.read_user_data('user_data.json')
				if data == '/start':
					text = None
					if str(user_id) in user_data.keys():
						# тело запроса для sendMessage для существующего пользователя при старте бота, обратно будет
						# возвращаться сразу вызов функции, может не секьюрно, зато хитро :-), правда длина 64 всего :-(
						body = {
							"chat_id": user_id,
							"text": "*Укажите настройки для рассылки прогноза погоды*",
							"reply_markup": {
								"inline_keyboard": [
									[
										{
											"text": "🏘Указать населённый пункт для прогноза",
											"callback_data": "f.setLocality(initial=True, user_id=user_id)"
										}
									],
									[
										{
											"text": "⏰Установить время рассылки прогноза (по умолчанию 21:00)",
											"callback_data": "f.setTimeRecieve(initial=True, user_id=user_id)"
										}
									],
									[
										{
											"text": "❌Отключить рассылку",
											"callback_data": "f.setActivity(user_id=user_id, is_active=0)"
										}
									],
									[
										{
											"text": "✅Включить рассылку",
											"callback_data": "f.setActivity(user_id=user_id, is_active=1)"
										}
									]
								]
							}
						}
					else:
						# тело запроса для sendMessage для нового пользователя
						body = {
							"chat_id": user_id,
							"text": "Укажите настройки для рассылки прогноза погоды",
							"reply_markup": {
								"inline_keyboard": [
									[
										{
											"text": "🏘Указать населённый пункт для прогноза",
											"callback_data": "f.setLocality(initial=True,user_id=user_id)"
										}
									],
									[
										{
											"text": "⏰Установить время рассылки прогноза (по умолчанию 21:00)",
											"callback_data": "f.setTimeRecieve(initial=True,user_id=user_id)"
										}
									]
								
								]
							}
						}
				elif data == '🛑':  # секретное сообщение для прерывания работы модуля :-)
					break
				elif in_message.get('set_time_msg', False) is True:  # если сообщение для установки времени
					result = f.setTimeRecieve(initial=False, time_res=data, user_id=user_id)
					if result.find('\u23f0') != -1:
						# тело повторного запроса на установку времени при неправильном формате
						body = {
							"chat_id": user_id,
							"text": result,
							"reply_markup": {"force_reply": True,
											 "input_field_placeholder": "Укажите время в формате HH:MM"}}
					else:
						text = result
						body = None
				elif in_message.get('set_location', False) is True:  # если сообщение для установки локации
					result = f.setLocality(initial=False, city=data, user_id=user_id)
					if result.find('🏘') != -1:
						# тело повторного запроса на установку локации при неправильном формате
						body = {
							"chat_id": user_id,
							"text": result,
							"reply_markup": {"force_reply": True,
											 "input_field_placeholder": "Укажите корректное название"}}
					else:
						text = result
						body = None
				elif in_message.get('is_callback', False) is True:  # если сообщение с действием по кнопке
					try:
						text = eval(data)  # разворачиваем вызов функции из строкового значения, да, пока так
						body = None
					except Exception as err:
						f_log = open('log', 'a')  # потом сделаем нормальные логи :-)
						f_log.writelines('\n' + str(err))
						f_log.close()
						continue
			else:
				text = 'access denied'
				body = None
			if text != 'OK':
				f.sendMessage(text=text, body=body, user_id=user_id)  # отправляем ответ в бота
	except Exception as err:
		f_log = open('log', 'a')  # потом сделаем нормальные логи :-)
		f_log.writelines('\n' + str(err))
		f_log.close()
		continue
