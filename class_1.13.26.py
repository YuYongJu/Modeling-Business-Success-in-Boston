# Exercise 0
# 1)
my_grade = 80
print(my_grade)

# 2)
my_grade += 20
# OR: my_grade = my_grade + 20
print(my_grade)

greeting = "hello"
greeting += " world"
# OR: greeting = greeting + " world"
print(greeting) # hello world

text = "Hello World"

# print(text[0:5])
print(text[:5])

# print characters from index 0 to 4 with step 2:
print(text[0:5:2])

# reverse order of string:
print(text[::-1])

# common string methods:
"hello".upper()  # "HELLO"
"HELLO".lower()  # "hello"
"hello".count("l")  # 2
"heiio".replace("i", "l")  # "hello"
" hello\n".strip()  # "hello"
"Hello World".split(" ")  # ["Hello", "World"]
" ".join(["Hello", "World"])  # "Hello World"

# Exercise 1
course = "Python Programming"
print(course[0])    # Print the first character of course
print(course[-1])   # Print the last character of course
print(len(course))  # Print the total length of course
course = course.lower() # Convert course to lowercase
print(course)   # Print lowercase course
print(course[7:])   # Extract the word Programming
print(course.replace("Python", "Java")) # Replace Python with Java

# Exercise 2
s = "hello world. this sentence will print in the next line. this is another sentence."
print(s)
list_of_sentences = s.split(".") # breaks s into its sentences
list_of_sentences = list_of_sentences[:1]   # takes out last period as sentence
print(list_of_sentences)
num_sentences = len(list_of_sentences)  # counts number of terms (sentences) in the list
print(num_sentences)
list_of_words = s.split(" ")    # breaks s into words
num_words = len(list_of_words)  # counts number of terms (words) in the list
print(num_words)

# lists are mutable (can be changed), tuples are immutable (cannot be changed)

# Exercise 3
numbers = [1,2,3,4,5]
print(numbers[2])  # print the 3rd item in the list
numbers[-1] = 10    # replace last item in the list with 10
print(numbers)  # prints [1,2,3,4,10]
numbers.append(6)   # adds 6 to end to make list [1,2,3,4,10,6]
print(numbers)
#numbers.remove(1)   # removes 1 to make list [2,3,4,10,6]
print(numbers[1:])

# Exercise 4
fruits = ["apple", "orange", "mango", "strawberry"]
print(len(fruits))    # prints number of fruits (num items in list)
print(sorted(fruits))   # prints in alphabetical order
# OR: fruits.sort()...\n print(fruits) does the same!
print(sorted(fruits)[::-1]) # prints in reverse alphabetical order
# this is especially helpful when sorting numbers like grades from lowest to highest
# (or -1 for highest to lowest)