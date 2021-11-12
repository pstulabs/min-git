# описание персон словарём
persons = [{'name': 'Иван', 'surname': 'Иванович', 'birthday': '12.03.1992', 'sex': 'male'},
		   {'name': 'Авиценна', 'surname': 'ибн Сина', 'birthday': '1.08.980', 'sex': 'male'},
		   {'name': 'Коко', 'surname': 'де Шанель', 'birthday': '19.08.1883', 'sex': 'female'}]

# получение запроса на поиск
req = input('Введите подстроку для поиска:\n')

# перебираем список с поиском подстроки в значении
for i in persons:
	a = list(i.values())
	for j in a:
		if j.find(req) != -1:
			print(i)  # выводим записи, в которых нашли подстроку
