## Сервис рассылки сообщений
import time  # форматирование времени
from datetime import datetime
import api_weather as w
import pytz as tz  # часовые пояса
import functions as f
import configparser  # парсинг конфига

# Получаем параметры из конфига
config = configparser.ConfigParser()
# справочник состояний погоды, для вывода юзеру, потом уберём в файл
c = {'clear': u'\u2600 ясно',
	 'partly-cloudy': u'\U0001F324 малооблачно',
	 'cloudy': u'\U0001F325 облачно с прояснениями',
	 'overcast': u'\u2601 пасмурно',
	 'drizzle': u'\U0001F327 морось',
	 'light-rain': u'\U0001F327 небольшой дождь',
	 'rain': u'\U0001F327 дождь',
	 'moderate-rain': u'\U0001F327 умеренно сильный дождь',
	 'heavy-rain': u'\U0001F327 сильный дождь',
	 'continuous-heavy-rain': u'\U0001F327 длительный сильный дождь',
	 'showers': u'\U0001F327 ливень',
	 'wet-snow': u'\U0001F327 \u2744 дождь со снегом',
	 'light-snow': u'\u2603 небольшой снег',
	 'snow': u'\u2744 снег',
	 'snow-showers': u'\U0001F328 снегопад',
	 'thunderstorm': u'\U0001F329 гроза',
	 'hail': 'град',
	 'thunderstorm-with-rain': u'\u26C8 дождь с грозой',
	 'thunderstorm-with-hail': u'\U0001F329 гроза с градом'}


# функция форматирования данных о прогнозе для отправки в бота
def formatMes(forecast, user_id, place):
	config.read('ya_weather_dict', encoding='cp1251')
	text = ''
	part = ''
	for i in forecast:
		if i != 'date':
			a = '\n' + config['Parts'][i]
			for key, val in forecast[i].items():
				if key in ['feels_like', 'humidity', 'uv_index']:
					param = '\n' + config['Params'][key] + ': ' + str(val)
					part += param
				elif key == 'condition':
					cond = '\n' + c[val]
				elif key == 'temp_max':
					if val <= 0:
						t_max = str(val)
					else:
						t_max = '+' + str(val)
				elif key == 'temp_min':
					if val <= 0:
						t_min = str(val)
					else:
						t_min = '+' + str(val)
				elif key == 'wind_dir':
					wd = '\nВетер: ' + config['Wind_dir'][val]
				elif key == 'wind_speed':
					ws = str(val)
			text = text + a + cond + f'\nТемпература: от {t_min} до {t_max}' + part + wd + ', ' + ws + 'м/с\n'
			part = ''
	body = {
		"chat_id": user_id,
		"text": f"Прогноз погоды для {place} на завтра {datetime.strftime(datetime.strptime(forecast['date'], '%Y-%m-%d'), '%d.%m.%Y')}\n{text}"}
	return body


# Отправляем прогноз юзерам, если подошло время отправки
while True:
	config.read('properties', encoding='utf-8')
	user_data = f.read_user_data('user_data.json')
	# выбираем юзеров, у которых time_res<текущего (с учётом часового пояса), is_active!=0, last_send!=сегодня
	send_list = {i: user_data[i]['location'] for i in user_data if
				 user_data[i].get('is_active', 0) != 0 and user_data[i].get('timezone', 0) != 0 and user_data[i].get(
					 'time_res', 0) != 0 and datetime.now(tz.timezone(user_data[i].get('timezone'))).strftime(
					 "%H:%M") > datetime.strptime(user_data[i].get('time_res'), '%H:%M').time().strftime(
					 "%H:%M") and datetime.now(tz.timezone(user_data[i].get('timezone'))).strftime("%Y-%m-%d") !=
				 user_data[
					 i].get('last_send')}
	if send_list != {}:  # если нашли юзеров, запрашиваем прогноз и отправляем юзерам в телегу
		for i in send_list:
			try:
				body = w.getForecast(lat=send_list[i]['lat'], lon=send_list[i]['lng'])
				body = formatMes(body, int(i), place=user_data[i]['place'])
				f.sendMessage(user_id=int(i), body=body)
			except Exception as err:
				f_log = open('log', 'a')  # потом сделаем нормальные логи :-)
				f_log.writelines('\n' + str(err))
				f_log.close()
				continue
			# перезаписываем у юзера дату последней отправки на текущую, чтоб больше не присылать прогноз сегодня
			user_data[i]['last_send'] = datetime.now(tz.timezone(user_data[i].get('timezone'))).strftime("%Y-%m-%d")
			f.write_user_data('user_data.json', user_data)
	time.sleep(int(config['Telegram']['CHECK_INTERVAL']))  # ждём указанный интервал времени перед следующей итерацией
