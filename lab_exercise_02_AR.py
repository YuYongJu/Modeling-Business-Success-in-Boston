# LAB EXERCISE 02
# PROBLEM 01
# 1)
sum_1_1000 = 0
for i in range(1, 1001):
    sum_1_1000 += i
# print(sum_1_1000)

# 2)
sum_odd_1_2501 = 0
for i in range(1, 2502, 2):
    sum_odd_1_2501 += i
print(sum_odd_1_2501)

sum_odd = 0
for i in range(1, 2502):
    if i % 2 == 1:
        sum_odd += i
print(sum_odd)

# PROBLEM 02
# 1)
fruits = ["apple", "pear", "grapes", "peach"]
letter2fruits = {}
for fruit in fruits:
    if fruit[0] not in letter2fruits:
        letter2fruits[fruit[0]] = []
    letter2fruits[fruit[0]].append(fruit)
# print(letter2fruits)

# 2)
common_letters = []
for letter in fruits[0]:
    letter_found = True
    for i in range(1, len(fruits)):
        if letter not in fruits[i]:
            letter_found = False
            break
    if letter_found and letter not in common_letters:
        common_letters.append(letter)
#print(common_letters)

# PROBLEM 03
# 1)
lst1 = [6, 7, 8, 9, 10]
total_sum = 0
# i = 0
# add values from lst1 while total sum is less than 2500
while i < len(lst1) and total_sum < 2500:
    total_sum += lst1[i]
    i += 1
print(total_sum)

# 2)
lst2 = [1, 2, 3, 4, 5, 6]
limited_sum = 0
for i in lst2:
    if i % 2 == 0:
        break
    limited_sum += i
#print(limited_sum)

# PROBLEM 04
### SETUP BEGINS -- DO NOT MODIFY
course_description = "Offers intermediate to advanced Python programming for data science. Covers object oriented design patterns using Python, including encapsulation, composition, and inheritance. Advanced programming skills cover software architecture, recursion, profiling, unit testing and debugging, lineage and data provenance, using advanced integrated development environments, and software control systems. Uses case studies to survey key concepts in data science with an emphasis on machine learning (classification, clustering, deep learning); data visualization; and natural language processing. Additional assigned readings survey topics in Ethics, Model Bias, and Data Privacy pertinent to todays Big Data world. Offers students an opportunity to prepare for more advanced courses in data science and to enable practical contributions to software development and data science projects in a commercial setting."
### SETUP ENDS -- DO NOT MODIFY

# 1)
course_description = course_description.lower()
for punctuation in ",.();":
    course_description = course_description.replace(punctuation, "")
words = course_description.split(" ")
#print(words)

# 2)
word2count = {}
for word in words:
    if word != "":
        if word in word2count:
            word2count[word] += 1
        else:
            word2count[word] = 1
#print(word2count)