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
print(len(text)) # finds length of text
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
list_of_Spam = spam.split("Spam ") # breaks list into times Spam appears
count_Spam = len(list_of_Spam) - 1 # counts items in list (times Spam appears) and takes out extra break
# 2)
list_of_spam = spam.split("spam ") # breaks list into times spam appears
count_spam = len(list_of_spam) - 1 # counts items in list (times spam appears) and takes out extra break
# 3)
list_of_spams = spam.split("spams") # breaks list into times spams appears
count_spams = len(list_of_spams) - 1 # counts items in list (times spams appears) and takes out extra break
# 4)
spam_clean = spam.replace("Spams", "spams").replace("spams", "spam").replace("Spam", "spam") # makes all words spam
# 5)
list_of_clean_spam = spam_clean.split(" ") # breaks list into times spam appears
count_spam_clean = len(list_of_clean_spam) # counts items in list (times spam appears) and takes out extra break
print(count_spam_clean)
# 6)
spam_list = list_of_clean_spam # makes spam_list variable for list of spam strings
# 7)
count_items = len(spam_list) # counts number of items in spam_list
# 8)
spam_list_sliced = spam_list[:4] # splits list in steps of 4 to produce list of 4 spam