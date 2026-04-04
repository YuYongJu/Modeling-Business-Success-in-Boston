# LAB EXERCISE 03

# SET UP BEGINS - Do Not Modify
employees = [
        {"name": "Alice", "department": "Engineering", "years_experience": 5},
        {"name": "Ann", "department": "Marketing", "years_experience": 4},
        {"name": "Ben", "department": "Engineering", "years_experience": 2},
        {"name": "Bob", "department": "Engineering", "years_experience": 6},
        {"name": "Eve", "department": "HR", "years_experience": 3},
    ]

pairs = [(5, 2), (1, 4), (3, 1), (2, 9)]
# SET UP ENDS - Do Not Modify

# PROBLEM 01
def count_ints(lst, num):
    """Takes a list of 2D integers and a single integer and returns the number of 
    occurrences of that integer in the list."""
    count = 0
    for sub in lst:
        for item in sub:
            if item == num:
                count = count + 1
    return count
# print(count_ints([[-1, -2, -3], [4, 5, 6]], 8)) #returns 0
# print(count_ints([[-1, -2, -3], [-1, 5, 6]], -1)) #returns 2
# print(count_ints([[-1, -2, -3, 4, 4], [4, 5, 6]], 4)) #returns 3

# PROBLEM 02
def remove_duplicates(lst):
    """Removes duplicates from list"""
    new_lst = []
    for i in lst:
        if i not in new_lst:
            new_lst.append(i)
    return new_lst

# print(remove_duplicates([1,1])) #returns [1]
# print(remove_duplicates([1,2,3])) #returns [1, 2, 3]
# print(remove_duplicates([3,1,2,3,2])) #returns [3, 1, 2])

# PROBLEM 03
def filter_employees(emp_dict):
    """Returns employee names from employees dictionary"""
    return [emp["name"] for emp in emp_dict if emp["department"] == "Engineering" and emp["years_experience"] > 3]

print(filter_employees([
{"name": "Alice", "department": "Engineering", "years_experience": 5},
{"name": "Bob", "department": "Engineering", "years_experience": 2}
]))
# returns ["Alice"]

# PROBLEM 04
def function_p4(tuple_list):
    for tup in tuple_list:
        prod = tup[0] * tup[1]
    return [(tup[0], tup[1], tup[0] * tup[1]) for tup in tuple_list]

print(function_p4([(1, 1), (3, 2)]))
# returns [(1, 1, 1), (3, 2, 6)])
# PROBLEM 05

def function_p5(pairs):
    """Takes list of tuples and sorts them by the second element of each tuple"""
    return sorted(pairs, key=lambda x:x[1])

print(function_p5(pairs))

# PROBLEM 06
def function_p6(pairs):
    """Takes a list of tuples and returns them in descending order by the sum of each tuple"""
    return sorted(pairs, key=lambda x: x[0] + x[1], reverse = True)

print(function_p6([(1, 2), (3, 4), (0, 5)]))
# returns [(3, 4), (0, 5), (1, 2)]

def main():
    pass

if __name__ == "__main__":
    main()
