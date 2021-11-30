# подключаем модуль нечёткого поиска
from fuzzywuzzy import process

# описание персон словарём
persons_d = [{'name': 'Иван', 'surname': 'Иванович', 'birthday': '12.03.1992', 'sex': 'male'},
			 {'name': 'Авиценна', 'surname': 'ибн Сина', 'birthday': '1.08.980', 'sex': 'male'},
			 {'name': 'Коко', 'surname': 'де Шанель', 'birthday': '19.08.1883', 'sex': 'female'}]

# описание персон списком: имя,фамилия,дата рождения,пол
persons_l = [['Иван', 'Иванович', '12.03.1992', 'male'], ['Авиценна', 'ибн Сина', '1.08.980', 'male'],
			 ['Коко', 'де Шанель', '19.08.1883', 'female']]

# получение запроса на поиск
req = input('Введите подстроку для поиска:\n')


# перебираем справочник с поиском подстроки в значении
def dict_search(req):
	result = []
	for i in persons_d:
		a = list(i.values())
		if [f[1] for f in process.extract(req, a)] >= [60]:
			result.append(i)
	return (result)


# перебираем список с поиском подстроки в значении
def list_search(req):
	result = []
	for i in persons_l:
		if [f[1] for f in process.extract(req, i)] >= [60]:
			result.append(i)
	return (result)


print(f'Результаты поиска по справочникку: {dict_search(req)}')
print(f'Результаты поиска по списку: {list_search(req)}')
