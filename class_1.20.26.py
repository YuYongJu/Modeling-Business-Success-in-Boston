import csv
# Exercise 1
lst = [50, 60, 70, 80, 90, 80, 70]

# print the first item
#print(lst[0])

# use a for loop to print each item
#for i in range(len(lst)):
    #print(lst[i])
#for i in lst:
   # print(i)

# use a for loop to print each item + 10
#for i in lst:
   #print(i += 10)

# Exercise 2
fruits = ["apple", "banana", "cherry", "mango"]
# 1) print first letter in each word
#for fruit in fruits:
    #print(fruit[0])

# 2) print the length of every item in fruits
#for i in range(len(fruits)):
    #fruit = fruits[i]
    #print(len(fruit))

# Exercise 3: for loop + condition
scores = [100, 50, 70, 80, 90, 100, 100]
# 1) Use a for loop to iterate through and print scores greater than or equal to 80
#for score in scores:
    #if score >= 80:
        #print(score)

# 2) Calculate and print sum of all scores greater than or equal to 80
total = 0
#for score in scores:
    #if score >= 80:
        #total = total + score
#print(total)

# Exercise 4: nested for loop (inner/outer)
# use a nested for loop to generate course numbers from two lists
majors = ["DS", "CS"]
numbers = [1000, 2000]

#for major in majors:
    #for num in numbers:
        #print(major + " " + str(num))

# Exercise 5: while loop
# write a program that asks the user to enter an integer.
# this should continue accepting input until total sum >100.
# then display total sum and total number of inputs
# assume input is always an int
input_count = 0
total = 0
#while total <= 100:
    #user_input = input("Enter a number: ")
    #print(user_input)
    #input_count += 1
    #total += int(user_input)
#print("Number of inputs: " + str(input_count))
#print("Total: " + str(total))

# csv download (make sure to have import csv somewhere at the top of your file)
data = []
with open('Wk03_Class04_data.csv', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        data.append(row)
print(data)

for item in data:
    print(item)

for item in data:
    print(item["Score"])

for item in data:
    """Print student ids for students with scores higher than 90"""
    if int(item["Score"]) >= 90:
        print(item["ID"])

# Use a for loop to count the number of students who have
# either a DS or Biology major. Print the number after that.
count = 0
for student in data:
    if student["Major"] == "DS" or student["Major"] == "Biology":
        count += 1
print(count)