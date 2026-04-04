# class_1.27.26.py
# Exercise 1: Use LC to...
# 1) get squares of numbers 1-10
list_1 = list(range(1, 11))
list_2 = []
for i in list_1:
    list_2.append(i**2) # or i*i
print(list_2)
# we want to make this into one line (list comprehension)
list_2 = [i**2 for i in list_1]
print(list_2)

# 2) get lengths of each word in list ["apple", "banana", "cherry"]
list_3 = ["apple", "banana", "cherry"]
# original method:
list_4 = []
for fruit in list_3:
    list_4.append(len(fruit))
# now using LC:
list_4 = [len(fruit) for fruit in list_3]
print(list_4)

# Exercise 2
# 1) Create a list of odd numbers from numbers 1-10
list_5 = list(range(1, 11))
list_6 = []
for i in list_5:
    if i % 2 == 1:
        list_6.append(i)
# print(list_6)
# using LC:
list_6 = [i for i in list_5 if i % 2 == 1]
print(list_6)

# 2) create a list of words starting w/ a from list
fruits_2 = ["apple", "mango", "avocado", "tomato"]
fruits_with_a = [fruit for fruit in fruits_2 if fruit[0] == "a"]
print(fruits_with_a)

# Exercise 3
# 1) Replace all negative numbers with 0 in the list
nums = [1, -2, 3, -4, 5]
pos_nums = [num if num > 0 else 0 for num in nums]
print(pos_nums)

# 2) Convert all scores greater than 80 to pass, others to fail
scores = [100, 100, 100, 50, 50, 50]
score_outcome = ["Pass" if score > 80 else "Fail" for score in scores]
print(score_outcome)

# Exercise 4
# 1) Write a lambda func that takes 2 nums and returns their sum
add = lambda a,b: a+b
print(add(3,4)) # prints 7

# 2) Write a lambda func that takes 2 nums and returns their product
multiply = lambda a,b: a*b
print(multiply(3,4))    # prints 12

# 3) Write a lambda func that takes a value and returns the same value
value = lambda a: a
print(value(5)) # prints 5

# we use lambda for functional operations: mapping, filtering, or sorting

# Exercise 5
# 1) Sort the list of tuples by the 2nd element in ascending order
pairs = [(1,3), (2,2), (4,1), (3,5)]
pairs_sorted = sorted(pairs, key=lambda x:x[1])
print(pairs_sorted) # Ans: [(4,1), (2,2), (1,3), (3,5)]

# 2) Sort by length of each word
fruits = ["apple", "banana", "fig", "cherry"]
fruits_sorted = sorted(fruits, key=lambda fruit:len(fruit))
print(fruits_sorted)