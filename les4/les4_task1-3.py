import numpy

## задача 1
print('Сумма чисел от 0 до 100=', sum(numpy.array(range(101))))

## задача 2
while True:
	try:
		num = int(input('Введите число: '))
		if num is not None:
			if num <= 0:
				print(sum(numpy.array(range(num, 0))))
			else:
				print(sum(numpy.array(range(num + 1))))
			break
	except:
		print('Введите корректное число')
		continue

## задача 3
print('Среднее из 100 случайных чисел=', sum(numpy.random.random(100)))