import json
import os

# --- Configuration ---
DATA_FILE = "grades.json"
NUM_SUBJECTS = 5
# --- End Configuration ---

def load_grades():
    """Loads student grade data from the JSON file."""
    if not os.path.exists(DATA_FILE):
        return {}
    
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        
        # Convert string keys from JSON back to integer roll numbers
        grades = {int(roll_str): marks_list for roll_str, marks_list in data.items()}
        print(f"Loaded {len(grades)} records from {DATA_FILE}.")
        return grades
    
    except json.JSONDecodeError:
        print("Error: grades.json is corrupted or empty. Starting with an empty database.")
        return {}
    except Exception as e:
        print(f"Error loading data: {e}. Starting with an empty database.")
        return {}

def save_grades(grades):
    """Saves the current grades dictionary back to the JSON file."""
    try:
        # Convert integer keys to strings for JSON serialization
        to_save = {str(k): v for k, v in grades.items()}
        with open(DATA_FILE, "w") as f:
            json.dump(to_save, f, indent=4)
        print("Data saved successfully to grades.json.")
    except Exception as e:
        print(f"Error saving data: {e}")

def get_valid_roll(prompt="Enter student Roll Number: "):
    """Prompts user for a numeric roll number with validation."""
    while True:
        val = input(prompt).strip()
        if not val:
            print("Roll number cannot be empty.")
            continue
        try:
            return int(val)
        except ValueError:
            print("Invalid input. Please enter a whole number for the Roll Number.")

def get_valid_marks():
    """Prompts user for marks for all subjects with validation (0-100)."""
    marks = []
    print(f"\n--- Entering Marks for {NUM_SUBJECTS} Subjects ---")
    for i in range(1, NUM_SUBJECTS + 1):
        while True:
            s = input(f"  Enter marks for subject {i} (0-100): ").strip()
            if not s:
                print("Mark is required.")
                continue
            try:
                m = float(s)
                if m < 0 or m > 100:
                    print("Marks must be between 0 and 100.")
                    continue
                # Store as integer if it's a whole number, otherwise float
                marks.append(int(m) if m == int(m) else m)
                break
            except ValueError:
                print("Invalid input. Enter a numeric value.")
    return marks

def calculate_stats(marks):
    """Calculates the total and average from a list of marks."""
    # Ensure all elements are treated as numbers for calculation
    marks_for_calc = [float(m) for m in marks]
    total = sum(marks_for_calc)
    avg = total / len(marks_for_calc) if marks_for_calc else 0
    return total, avg

def add_grades(grades):
    """Adds a new student record to the system."""
    print("\n--- Add Student Record ---")
    roll = get_valid_roll()
    if roll in grades:
        print(f"Error: Roll Number {roll} already exists. Use the Update option to change marks.")
        return
    
    marks = get_valid_marks()
    grades[roll] = marks
    save_grades(grades)
    print(f"\nSuccess: Record for Roll {roll} added.")

def delete_grades(grades):
    """Deletes an existing student record."""
    print("\n--- Delete Student Record ---")
    roll = get_valid_roll()
    
    if roll in grades:
        confirm = input(f"Confirm deletion for Roll {roll} ({grades[roll]})? (y/n): ").strip().lower()
        if confirm == 'y':
            del grades[roll]
            save_grades(grades)
            print(f"Success: Record for Roll {roll} deleted.")
        else:
            print("Deletion cancelled.")
    else:
        print(f"Error: Roll Number {roll} not found.")

def update_grades(grades):
    """Updates the marks for an existing student record."""
    print("\n--- Update Student Record ---")
    roll = get_valid_roll()
    
    if roll not in grades:
        print(f"Error: Roll Number {roll} not found. Use the Add option to create a new record.")
        return
    
    print(f"Current marks for Roll {roll}: {grades[roll]}")
    print("Please enter the new set of marks to replace the existing ones.")
    marks = get_valid_marks()
    
    grades[roll] = marks
    save_grades(grades)
    print(f"\nSuccess: Record for Roll {roll} updated.")

def view_all_grades(grades):
    """Displays all student records with calculated totals and averages."""
    print("\n" + "="*70)
    print("--- STUDENT GRADE REPORT (All Records) ---")
    print("="*70)
    
    if not grades:
        print("No student records available to display.")
        return
    
    # Header formatting
    header = f"{'Roll':<10} | {'Marks (Sub 1-5)':<30} | {'Total':<8} | {'Avg':<8}"
    print(header)
    print("-" * 70)
    
    # Print records sorted by roll number
    for roll in sorted(grades.keys()):
        marks = grades[roll]
        total, avg = calculate_stats(marks)
        
        # Create a neat string representation of marks
        marks_str = ", ".join(f"{m:<4}" for m in marks)
        
        print(f"{roll:<10} | {marks_str:<30} | {total:<8.0f} | {avg:<8.2f}")
    print("-" * 70)

def search_by_roll(grades):
    """Searches and displays a single student record by roll number."""
    print("\n--- Search by Roll Number ---")
    roll = get_valid_roll()
    
    if roll in grades:
        marks = grades[roll]
        total, avg = calculate_stats(marks)
        marks_str = ", ".join(str(m) for m in marks)
        
        print(f"\n--- Result for Roll {roll} ---")
        print(f"  Marks: [{marks_str}]")
        print(f"  Total Score: {total:.0f}")
        print(f"  Average Score: {avg:.2f}")
    else:
        print(f"Record not found for Roll Number {roll}.")

def export_report(grades, filename="grades_report.txt"):
    """Exports all student records, totals, and averages to a text file."""
    try:
        with open(filename, "w") as f:
            f.write("Student Grades Report\n")
            f.write(f"Generated on: {os.path.basename(__file__)}\n\n")
            
            if not grades:
                f.write("No records available.\n")
            else:
                f.write(f"{'Roll':<10}\t{'Marks (Sub 1-5)':<25}\t{'Total':<8}\t{'Average':<8}\n")
                f.write("-" * 70 + "\n")
                
                for roll in sorted(grades.keys()):
                    marks = grades[roll]
                    total, avg = calculate_stats(marks)
                    marks_str = ", ".join(str(m) for m in marks)
                    
                    f.write(f"{roll:<10}\t{marks_str:<25}\t{total:<8.0f}\t{avg:<8.2f}\n")
        
        print(f"\nSuccess: Report successfully exported to {filename}")
    except Exception as e:
        print(f"Error exporting report: {e}")

def main_menu():
    """The main command-line interface loop for the application."""
    grades = load_grades()
    
    menu = f"""
{'-'*40}
 Student Grades Management System
{'-'*40}
1. Add New Record
2. Delete Record
3. Update Marks
4. View All Records
5. Search by Roll Number
6. Export Report to Text File
7. Exit
{'-'*40}
"""
    
    while True:
        print(menu)
        choice = input("Choose an option (1-7): ").strip()
        
        if choice == "1":
            add_grades(grades)
        elif choice == "2":
            delete_grades(grades)
        elif choice == "3":
            update_grades(grades)
        elif choice == "4":
            view_all_grades(grades)
        elif choice == "5":
            search_by_roll(grades)
        elif choice == "6":
            export_report(grades)
        elif choice == "7":
            print("Exiting application. Goodbye!")
            break
        else:
            print("\nInvalid choice. Please enter a number between 1 and 7.")

if __name__ == "__main__":
    main_menu()
