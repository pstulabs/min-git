# произведение чисел, кратных и 3 и 5
nums=[1,2,3,15,20,30,11,13,45]
prod=1
for i in nums:
	if i%5==0 and i%3==0:
		prod*=i
print(prod)
