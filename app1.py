"""
Student Grades Management
Author: Gemini
File: student_grades.py

Features:
- Store student records with Roll number as key and 5 subject marks as value.
- Add, Delete, Update, View all, Search by roll.
- Data persisted to grades.json locally.
- Simple input validation (marks 0-100, roll as int).
"""

import json
import os

DATA_FILE = "grades.json"
NUM_SUBJECTS = 5

def load_grades():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        grades = {}
        for k, v in data.items():
            try:
                roll = int(k)
                marks = []
                for m in v:
                    if isinstance(m, str):
                        marks.append(float(m) if '.' in m else int(m))
                    else:
                        marks.append(m)
                grades[roll] = marks
            except ValueError:
                print(f"Skipping invalid record for key: {k}")
        return grades
    except Exception as e:
        print("Error loading data. Starting with an empty database:", e)
        return {}

def save_grades(grades):
    try:
        to_save = {str(k): v for k, v in grades.items()}
        with open(DATA_FILE, "w") as f:
            json.dump(to_save, f, indent=4)
        print("Data saved to grades.json.")
    except Exception as e:
        print("Error saving data:", e)

def input_roll(prompt="Enter roll number: "):
    while True:
        val = input(prompt).strip()
        if not val:
            print("Roll number is required.")
            continue
        if not val.isdigit():
            print("Please enter a numeric roll number.")
            continue
        return int(val)

def input_marks():
    marks = []
    for i in range(1, NUM_SUBJECTS + 1):
        while True:
            s = input(f"Enter marks for subject {i} (0-100): ").strip()
            if not s:
                print("Mark is required.")
                continue
            try:
                m = float(s)
                if m < 0 or m > 100:
                    print("Marks must be between 0 and 100.")
                    continue
                marks.append(int(m) if m.is_integer() else m)
                break
            except ValueError:
                print("Enter a valid number.")
    return marks

def add_grades(grades):
    print("\n--- Add Record ---")
    roll = input_roll()
    if roll in grades:
        print(f"Roll {roll} already exists. Use the Update option to change marks.")
        return
    marks = input_marks()
    grades[roll] = marks
    save_grades(grades)
    print("Record added successfully.")

def delete_grades(grades):
    print("\n--- Delete Record ---")
    roll = input_roll()
    if roll in grades:
        confirm = input(f"Are you sure you want to delete record for roll {roll}? (y/n): ").strip().lower()
        if confirm == 'y':
            del grades[roll]
            save_grades(grades)
            print("Record deleted.")
        else:
            print("Deletion cancelled.")
    else:
        print("Roll number not found.")

def update_grades(grades):
    print("\n--- Update Record ---")
    roll = input_roll()
    if roll not in grades:
        print("Roll number not found. Use the Add option to create a new record.")
        return
    print(f"Current marks for roll {roll}: {grades[roll]}")
    print("Enter new marks (this will replace existing marks).")
    marks = input_marks()
    grades[roll] = marks
    save_grades(grades)
    print("Record updated.")

def view_grades(grades):
    print("\n--- All Records ---")
    if not grades:
        print("No records available.")
        return
    print(f"{'Roll':<8} | {'Marks (5 Subjects)':<25} | {'Total':<8} | {'Avg':<8}")
    print("-" * 60)
    for roll in sorted(grades.keys()):
        marks = grades[roll]
        marks_for_calc = [float(m) if not isinstance(m, (int, float)) else m for m in marks]
        total = sum(marks_for_calc)
        avg = total / len(marks_for_calc) if marks_for_calc else 0
        marks_str = ", ".join(str(m) for m in marks)
        print(f"{roll:<8} | [{marks_str:<23}] | {total:<8} | {avg:<8.2f}")

def search_by_roll(grades):
    print("\n--- Search by Roll ---")
    roll = input_roll()
    if roll in grades:
        marks = grades[roll]
        marks_for_calc = [float(m) if not isinstance(m, (int, float)) else m for m in marks]
        total = sum(marks_for_calc)
        avg = total / len(marks_for_calc) if marks_for_calc else 0
        marks_str = ", ".join(str(m) for m in marks)
        print(f"\n--- Result for Roll {roll} ---")
        print(f"Marks: [{marks_str}]")
        print(f"Total: {total}")
        print(f"Average: {avg:.2f}")
    else:
        print("Record not found.")

def export_report(grades, filename="grades_report.txt"):
    try:
        with open(filename, "w") as f:
            if not grades:
                f.write("No records.\n")
            else:
                f.write("Roll\tMarks\t\tTotal\tAverage\n")
                for roll in sorted(grades.keys()):
                    marks = grades[roll]
                    marks_for_calc = [float(m) if not isinstance(m, (int, float)) else m for m in marks]
                    total = sum(marks_for_calc)
                    avg = total / len(marks_for_calc) if marks_for_calc else 0
                    marks_str = ", ".join(str(m) for m in marks)
                    f.write(f"{roll}\t[{marks_str}]\t{total}\t{avg:.2f}\n")
        print(f"\nReport successfully exported to {filename}")
    except Exception as e:
        print("Error exporting report:", e)

def main_menu():
    grades = load_grades()
    menu = f"""
{'-'*30}
Student Grades Management System
{'-'*30}
1. Add grades
2. Delete grades
3. Update grades
4. View all grades
5. Search by roll number
6. Export report (text file)
7. Exit
{'-'*30}
Choose an option (1-7): """
    
    while True:
        choice = input(menu).strip()
        if choice == "1":
            add_grades(grades)
        elif choice == "2":
            delete_grades(grades)
        elif choice == "3":
            update_grades(grades)
        elif choice == "4":
            view_grades(grades)
        elif choice == "5":
            search_by_roll(grades)
        elif choice == "6":
            export_report(grades)
        elif choice == "7":
            print("Exiting application. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 7.")

if _name_ == "_main_":
    main_menu()