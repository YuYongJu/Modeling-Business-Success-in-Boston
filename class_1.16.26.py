# Class 1.16.26

# Exercise 1.1
kitkat = {"price": "$1", "type1": "chocolate", "type2": "candy"}
kitkat["calories"] = 10
kitkat["calories"] = 400
#print(kitkat["price"])
#print(kitkat["type1"])
#print(kitkat["type2"])
#print(kitkat["calories"])

# Exercise 1.2: Single Dictionary
# 1)
# create a dictionary named snickers that contains the key value pairs
snickers = {"price": "$1.5", "type1": "chocolate", "type2": "candy"}
# add new key calories with value 500
snickers["calories"] = 500
#print(snickers)

# Exercise 1.3
del snickers["type2"]
del kitkat["type2"]
# 1)
skittles = {"price": "$2", "type1": "candy", "calories": 300}
doritos = {"price": "$4", "type1": "chips", "calories": 700}
#print(kitkat)
#print(snickers)
#print(skittles)
#print(doritos)
# 2)
chocolate = {}
# 3)
del snickers["type1"]
del kitkat["type1"]
# 4)
chocolate["kitkat"] = kitkat
chocolate["snickers"] = snickers
print(chocolate)

# Exercise 1.5: nested dictionary
#1) 
del skittles["type1"]
del doritos["type1"]
candy = {}
candy["skittles"] = skittles
chips = {}
chips["doritos"] = doritos
#print(chocolate)
#print(candy)
#print(chips)
#print(candy["skittles"])
#print(candy["skittles"]["price"])

# Exercise 1.6
store = {}
store["chocolate"] = chocolate
store["candy"] = candy
store["chips"] = chips
#print(store)

# Exercise 1.7
#print(store["chocolate"]["snickers"]["price"])

# Exercise 1.8
store["chips"]["fritos"] = {"price": "$5", "calories": 500}
#print(store["chips"]["fritos"]["price"])

# Exercise 2
score = int(input("Enter a score: "))
if 90 <= score <= 100:
    print("A")
elif score >= 80:
    print("B")
elif score >= 70:
    print("C")
elif score >= 60:
    print("D")
else:
    print("F")

# Exercise 3
fruits = ["apple", "banana", "cherry"]
choice = input("Enter a fruit: ")

if choice in fruits: # membership checking in python uses "in" keyword
    print(f"{choice} is available. ")
else:
    print(f"{choice} is not available. ")