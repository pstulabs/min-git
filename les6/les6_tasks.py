# задача 1, описание персон классом
import uuid
from pprint import pprint

from fuzzywuzzy import process


class Person:
	def __init__(self, name, surname, birthday, sex):
		self.name, self.surname, self.birthday, self.sex = name, surname, birthday, sex
		self.key = str(uuid.uuid4())
	
	def __repr__(self):
		return f'({self.name}, {self.surname}, {self.birthday}, {self.sex})'


p1 = Person('Иван', 'Иванович', '12.03.1992', 'male')
p2 = Person('Авиценна', 'ибн Сина', '1.08.980', 'male')
p3 = Person('Коко', 'де Шанель', '19.08.1883', 'female')

persons = {p1.key: p1, p2.key: p2, p3.key: p3}
print(f'Справочник персон:')
pprint(persons)

# задача 2, поиск по полям
req = input('\nВведите подстроку для поиска:\n')

print('Чётенький поиск:')
for key, val in persons.items():
	if persons[key].surname.find(req) != -1:
		print(key, ":", val)

# задача 3, нечёткий поиск по полям
print('\nНечёткий поиск:')
def dict_search(req):
	result = []
	for i in persons:
		# a = list(i.values())
		if process.extract(req, [persons[i].surname])[0][1] >= 60:
			result.append({persons[i].key: persons[i]})
	return (result)

pprint(dict_search(req))
