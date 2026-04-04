# LAB EXERCISE 01
# Problem 1
# 1)
num = 25
# 2)
subject = "Computer Science"
# 3)
is_active = True

# Problem 2
# 1)
text = "Data Science"
# 2)
first_char = text[0] # extracts first character of text variable
# 3)
last_char = text[-1] # extracts last character of text variable
# 4)
text_length = len(text) # finds length of text
# 5)
text_upper = text.upper() # converts text to uppercase in a new variable
# 6)
second_word = text[5:12] # extracts second word in text to new variable
# 7)
text1 = text.replace("Data", "Computer") # replaces data with computer in text as new variable

# Problem 3
# 1)
fruits = ["banana", "apple", "orange"]
# 2)
fruits.append("grapes") # adds grapes to list of fruits
# 3)
fruits[1] = "mango" # replaces apple with mango
# 4)
first_item = fruits[0] # extracts first fruit and assigns to new variable
# 5)
last_item = fruits[-1] # extracts last fruit and assigns to new variable

# Problem 4
spam = "Spam spam Spam spam Spam spam Spam Spam Spam spam spams spams spams spams spams spams spams Spam Spam Spam Spams Spam spam spam Spam spams spams Spam Spam Spam Spams Spam spam spam Spam spams spam spam spams spams"
# 1)
count_Spam = spam.count("Spam") # counts times Spam appears
# 2)
count_spam = spam.count("spam") # counts times spam appears
# 3)
count_spams = spam.count("spams") # counts times spams appears
# 4)
#spam_clean = spam.replace("Spams", "spams").replace("spams", "spam").replace("Spam", "spam") # makes all words spam
spam_clean = spam.lower().replace("spams", "spam")
# 5)
count_spam_clean = spam_clean.count("spam") # counts times spam appears
print(count_spam_clean)
# 6)
spam_list = spam_clean.split(" ") # breaks into spam words at spaces
# 7)
count_items = len(spam_list) # counts number of items in spam_list
# 8)
spam_list_sliced = spam_list[:4] # splits list in steps of 4 to produce list of 4 spam
print(spam_list_sliced)