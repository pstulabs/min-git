## Модуль взаимодействия с API сервиса погоды и вспомогательными сервисами
import geocoder  # модуль геокодинга с несколькими поставщиками
import configparser  # парсинг конфига
import requests  # http-запросы

# Получаем параметры из конфига
config = configparser.ConfigParser()


# получение координат нас. пункта
def getLocality(place):  # используем сервис OpenCage, т.к. он дополнительно отдаёт часовой пояс
	config.read('properties', encoding='utf-8')
	key = config['OpenCage']['API_KEY']
	geo = geocoder.opencage(place, key=key, countrycode='ru', language='ru', no_record=1,
							limit=1)
	if geo is not None:
		geo = geo.json.get('raw', {})
		result = {'location': geo.get('geometry', {}),
				  'timezone': geo.get('annotations', {}).get('timezone', {}).get('name', {})}
	else:
		result = None
	return result


# получение прогноза
def getForecast(lat, lon, limit=2, hours='false'):
	config.read('properties', encoding='utf-8')
	URL = config['Yandex']['URL']
	KEY = config['Yandex']['API_KEY']
	req = requests.get(URL, params={'lat': lat, 'lon': lon, 'limit': limit, 'hours': hours}, timeout=5,
					   headers={'X-Yandex-API-Key': KEY})
	req = req.json().get('forecasts')[1]
	result = {i: {'condition': req['parts'][i]['condition'], 'feels_like': req['parts'][i]['feels_like'],
				  'humidity': req['parts'][i]['humidity'], 'temp_max': req['parts'][i]['temp_max'],
				  'temp_min': req['parts'][i]['temp_min'], 'wind_dir': req['parts'][i]['wind_dir'],
				  'wind_speed': req['parts'][i]['wind_speed'], 'uv_index': req['parts'][i]['uv_index']}
			  for i in req['parts'] if i not in ['day_short', 'night_short']}
	result = {'night': result['night'], 'morning': result['morning'], 'day': result['day'],
			  'evening': result['evening']}
	result['date'] = req['date']  # добавляем дату
	return result
