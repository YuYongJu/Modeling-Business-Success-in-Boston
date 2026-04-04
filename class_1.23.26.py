# Exercise 2
def apply_discount(cost, discount):
    """Returns number after taking discount off"""
    return cost - ((discount/100) * cost)
print(apply_discount(10, 10))

def apply_tax(cost, tax):
    """Returns number after adding tax"""
    return cost + (cost * (tax/100))
print(apply_tax(10, 8))

# Exercise 3
def get_words(sentence):
    """Extracts words from a sentence and returns them as a list"""
    words = sentence.lower().strip().split()
    return words

def count_long_words(words):
    """Counts words with more than 5 characters"""
    count = 0
    for word in words:
        if len(word) > 5:
            count += 1
    return count

sentence = "hello this is a sentence"
list_of_words = get_words(sentence)
count = count_long_words(list_of_words)
print(count)

# Exercise 4
def count_vowels(word):
    """Counts the number of vowels within a word"""
    vowels = "aeiouAEIOU"
    count = 0
    for letter in word:
        if letter in vowels:
            count += 1
    return count

print(count_vowels("Abigail"))

def find_most_vowel_words(words):
    """Returns the word(s) that contain the most vowels"""
    counts = []
    for word in words:
        vowel_count = count_vowels(word)
        counts.append(vowel_count)
    max_count = 0
    for count in counts:
        if count > max_count:
            max_count = count

    words_with_most_vowels = []
    for idx, count in enumerate(counts):
        if count == max_count:
            word = words[idx]
            words_with_most_vowels.append(word)
    return words_with_most_vowels

print(find_most_vowel_words(["Abby", "Abigail", "Abegail"]))
