## Основные функции приложения
import json  # преобразование в json и обратно
import requests  # http-запросы
import configparser  # парсинг конфига
from datetime import datetime, timedelta  # преобразование дат и времени
import api_weather as w
import pytz as tz  # для часовых поясов


# получаем данные юзеров из файла
def read_user_data(file):
	r_data = open(file, 'r', encoding='utf-8')
	user_data = r_data.readlines()[0]
	r_data.close()
	file_data = json.loads(user_data)
	return file_data


# пишем данные юзера в файл
def write_user_data(file, data):
	f_data = open(file, 'w', encoding='utf-8')
	u_data = json.dumps(data)
	f_data.writelines(u_data)
	f_data.close()
	return


# Получаем параметры из конфига
config = configparser.ConfigParser()
config.read('properties', encoding='utf-8')
TG_API = config['Telegram']['URL']


# функция для получения сообщений из телеги, берём только сообщения типа "message", "callback_query"
def getUpdates():
	req = requests.get(f'{TG_API}getUpdates',
					   params={'offset': -1, 'allowed_updates': ["message", "callback_query"]}, timeout=5)
	req = req.json()
	if req['result'] != []:
		req = req['result'][0]
		# метим прочитанным сообщение в телеге, чтобы оно не приходило повторно
		requests.get(f'{TG_API}getUpdates', params={'offset': req['update_id'] + 1}, timeout=5)
		if req.get('message', {}).get('text', {}) != {}:
			resp = {'data': req.get('message', {}).get('text', {}),
					'user_id': req.get('message', {}).get('from', {}).get('id')}
			# тут мы определяем, содержит ли сообщение данные для установки времени через setTimeRecieve (лучше не придумал)
			if req.get('message', {}).get('reply_to_message', {}).get('text', 'empty').find('\u23f0') != -1:
				resp['set_time_msg'] = True
			# тут мы определяем, содержит ли сообщение данные для установки локации через setLocality
			elif req.get('message', {}).get('reply_to_message', {}).get('text', 'empty').find('🏘') != -1:
				resp['set_location'] = True
		elif req.get('callback_query', {}) != {}:
			resp = {'id': req.get('callback_query', {}).get('id'), 'data': req.get('callback_query', {}).get('data'),
					'user_id': req.get('callback_query', {}).get('from', {}).get('id'), 'is_callback': True}
	else:
		resp = None
	return resp


# функция для отправки сообщений в бота
def sendMessage(user_id, text=None, body=None):
	if body is None:
		body = {
			"chat_id": user_id,
			"text": text}
	req = requests.post(f'{TG_API}sendMessage', json=body, timeout=5)
	return req.status_code


# установка нас. пункта
def setLocality(initial, user_id, city='Пермь'):
	if initial is True:  # если это выбор настройки нас. пункта
		# отправка запроса нас. пункта
		body = {
			"chat_id": user_id,
			"text": "🏘 Укажите название населённого пункта",
			"reply_markup": {"force_reply": True, "input_field_placeholder": "Укажите населённый пункт"}}
		sendMessage(user_id=user_id, text=None, body=body)
		result = 'OK'
	else:  # если это пришло само название нас. пункта
		geo = w.getLocality(city)  # идём в сервис геокодинга
		if geo is not None:
			user_data = read_user_data('user_data.json')
			if user_data.get(str(user_id), None) is None:
				user_data[str(user_id)] = {}
			user_data[str(user_id)]['location'] = geo['location']
			user_data[str(user_id)]['timezone'] = geo['timezone']
			user_data[str(user_id)]['last_send'] = (datetime.now(tz.timezone(geo['timezone'])) - timedelta(1)).strftime(
				'%Y-%m-%d')
			user_data[str(user_id)]['is_active'] = 1
			user_data[str(user_id)]['place'] = city
			if user_data[str(user_id)].get('time_res', None) is None:
				user_data[str(user_id)]['time_res'] = '21:00'
				result = f'Населённый пункт {city} установлен. Время рассылки по умолчанию 21:00. Для изменения времени установите время рассылки.'
			else:
				result = f'Населённый пункт {city} установлен'
			write_user_data('user_data.json', user_data)
		else:
			result = '🏘 Населённый пункт не определён. Проверьте корректность названия.'
	return result


# установка времени рассылки
def setTimeRecieve(user_id, initial, time_res='21:00'):
	if initial is True:
		# отправка запроса на установку времени
		body = {
			"chat_id": user_id,
			"text": "\u23f0 Укажите время для рассылки прогноза погоды",
			"reply_markup": {"force_reply": True, "input_field_placeholder": "Укажите время в формате HH:MM"}}
		sendMessage(user_id=user_id, text=None, body=body)
		result = 'OK'
	else:
		try:
			datetime.strptime(time_res, '%H:%M').time()
		except ValueError:
			result = '\u23f0 Неверный формат времени, укажите время в формате HH:MM, например, 21:00'
			return result
		user_data = read_user_data('user_data.json')
		if user_data.get(str(user_id), None) is None:
			user_data[str(user_id)] = {}
		user_data[str(user_id)]['time_res'] = time_res
		write_user_data('user_data.json', user_data)
		if user_data.get(str(user_id), {}).get('location', None) is not None:
			result = f'Время рассылки прогноза установлено на {time_res}'
		else:
			result = f'Время рассылки прогноза установлено на {time_res}. Необходимо выбрать населённый пункт'
	return result


# вкл/выкл рассылку
def setActivity(user_id, is_active):
	user_data = read_user_data('user_data.json')
	if user_data.get(str(user_id), None) is None:
		user_data[str(user_id)] = {}
	user_data[str(user_id)]['is_active'] = is_active
	write_user_data('user_data.json', user_data)
	if is_active == 0:
		result = 'Рассылка отключена'
	else:
		result = 'Рассылка включена'
	return result
