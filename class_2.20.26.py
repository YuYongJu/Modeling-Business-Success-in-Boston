def main():
    # ...
    # ...
    student_list = ["John", "Jane"]
    student_grades = [[60,70,90,100], [80,90,90,80]]

file = open("student_data.txt", "w")
file.write("Hello World")

for name in student_names:
    file.write(name+"\n")
file.close()

file.write(",".join(student_names)+"\n")
john_scores = student_grades[0]
jane_scores = student_grades[1]
for idx, i in enumerate(john_scores):
    john_score = i
    jane score = jane_scores[idx]

    row = f"{john_score}, {jane_score}\n"

# if w pandas:

# df.to_csv("student_names.csv")
# df.to_excel("student_names.xlsx")


if __name__ == '__main__':
    main()