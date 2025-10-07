import streamlit as st
import json
import os
import pandas as pd

# --- Configuration ---
DATA_FILE = "grades.json"
NUM_SUBJECTS = 5
# Updated SUBJECT_NAMES to specific subject titles
SUBJECT_NAMES = ["Maths", "Science", "History", "Geography", "Marathi"]
# --- End Configuration ---

# --- Data Persistence Functions (Adapted) ---

@st.cache_resource(ttl=3600) # Cache the function that loads the data file
def load_grades():
    """Loads student grade data from the JSON file."""
    if not os.path.exists(DATA_FILE):
        return {}
    
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        
        # Convert string keys from JSON back to integer roll numbers
        grades = {int(roll_str): marks_list for roll_str, marks_list in data.items()}
        return grades
    
    except json.JSONDecodeError:
        st.error("Error: grades.json is corrupted or empty. Starting with an empty database.")
        return {}
    except Exception as e:
        st.error(f"Error loading data: {e}. Starting with an empty database.")
        return {}

def save_grades(grades):
    """Saves the current grades dictionary back to the JSON file."""
    try:
        # Convert integer keys to strings for JSON serialization
        to_save = {str(k): v for k, v in grades.items()}
        with open(DATA_FILE, "w") as f:
            json.dump(to_save, f, indent=4)
        st.success("Data saved successfully to grades.json.")
    except Exception as e:
        st.error(f"Error saving data: {e}")

# --- Utility Functions ---

def calculate_stats(marks):
    """Calculates the total and average from a list of marks."""
    # Ensure all elements are treated as numbers for calculation
    marks_for_calc = [float(m) for m in marks]
    total = sum(marks_for_calc)
    avg = total / len(marks_for_calc) if marks_for_calc else 0
    return total, avg

def grades_to_dataframe(grades):
    """Converts the grades dictionary into a Pandas DataFrame for display."""
    data_list = []
    for roll, marks in grades.items():
        total, avg = calculate_stats(marks)
        
        row = {"Roll Number": roll}
        for i, mark in enumerate(marks):
            row[SUBJECT_NAMES[i]] = mark
        
        row["Total"] = round(total, 0)
        row["Average"] = round(avg, 2)
        data_list.append(row)
    
    df = pd.DataFrame(data_list)
    if not df.empty:
        # Sort by Roll Number
        df = df.sort_values(by="Roll Number").reset_index(drop=True)
    return df

# --- Streamlit UI Components ---

def add_record_page():
    """UI for adding a new student record."""
    st.header("➕ Add New Student Record")

    with st.form("add_form", clear_on_submit=True):
        roll = st.number_input("Roll Number", min_value=1, step=1, key="add_roll")
        
        marks = []
        for i in range(NUM_SUBJECTS):
            # Changed st.slider to st.number_input as requested
            mark = st.number_input(
                f"{SUBJECT_NAMES[i]} Mark (0-100)", 
                min_value=0, max_value=100, value=75, step=1, 
                key=f"add_mark_{i}"
            )
            marks.append(mark)
        
        submitted = st.form_submit_button("Add Record")

        if submitted:
            if roll in st.session_state.grades:
                st.error(f"Roll Number **{roll}** already exists. Use the Update section instead.")
            else:
                st.session_state.grades[roll] = marks
                save_grades(st.session_state.grades)
                st.success(f"Record for Roll **{roll}** added successfully!")

def update_record_page():
    """UI for updating an existing student record."""
    st.header("✍️ Update Student Marks")

    rolls = list(st.session_state.grades.keys())
    
    if not rolls:
        st.warning("No records available to update. Please add a record first.")
        return

    selected_roll = st.selectbox("Select Roll Number to Update", sorted(rolls))
    
    if selected_roll:
        current_marks = st.session_state.grades.get(selected_roll, [0] * NUM_SUBJECTS)
        st.subheader(f"Current Marks for Roll {selected_roll}:")
        st.write(current_marks)

        with st.form("update_form"):
            new_marks = []
            for i in range(NUM_SUBJECTS):
                mark = st.slider(
                    f"New {SUBJECT_NAMES[i]} Mark", 
                    min_value=0, max_value=100, 
                    value=int(current_marks[i]), # Use current value as default
                    step=1, 
                    key=f"update_mark_{i}"
                )
                new_marks.append(mark)
            
            submitted = st.form_submit_button("Update Marks")

            if submitted:
                st.session_state.grades[selected_roll] = new_marks
                save_grades(st.session_state.grades)
                st.success(f"Marks for Roll **{selected_roll}** updated successfully!")

def delete_record_page():
    """UI for deleting a student record."""
    st.header("🗑️ Delete Student Record")
    
    rolls = list(st.session_state.grades.keys())
    if not rolls:
        st.warning("No records available to delete.")
        return

    selected_roll = st.selectbox("Select Roll Number to Delete", sorted(rolls))
    
    if selected_roll:
        marks_str = ", ".join(map(str, st.session_state.grades[selected_roll]))
        st.warning(f"You are about to delete record for Roll **{selected_roll}** (Marks: {marks_str}).")
        
        if st.button(f"Confirm Delete Roll {selected_roll}"):
            del st.session_state.grades[selected_roll]
            save_grades(st.session_state.grades)
            st.success(f"Record for Roll **{selected_roll}** has been deleted.")
            # Rerun to clear the selection box
            st.rerun()

def view_all_records_page():
    """UI for viewing all records."""
    st.header("📊 All Student Records")
    
    df = grades_to_dataframe(st.session_state.grades)
    
    if df.empty:
        st.info("The grades database is empty.")
    else:
        st.dataframe(df, use_container_width=True)
        

def search_record_page():
    """UI for searching a student record by roll number."""
    st.header("🔍 Search by Roll Number")
    
    search_roll = st.number_input("Enter Roll Number to Search", min_value=1, step=1, key="search_roll")
    
    if st.button("Search"):
        if search_roll in st.session_state.grades:
            marks = st.session_state.grades[search_roll]
            total, avg = calculate_stats(marks)
            
            st.success(f"Record Found for Roll **{search_roll}**")
            
            # Create a small DataFrame for the single result
            result_data = {
                "Roll Number": [search_roll],
                "Marks": [", ".join(map(str, marks))],
                "Total": [round(total, 0)],
                "Average": [round(avg, 2)],
            }
            df_result = pd.DataFrame(result_data)
            st.table(df_result)

            # Display individual marks
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Individual Subject Scores:**")
                for i, mark in enumerate(marks):
                    st.write(f"- {SUBJECT_NAMES[i]}: **{mark}**")

        else:
            st.error(f"Record for Roll Number **{search_roll}** not found.")


# --- Main Application Execution ---

def streamlit_app():
    """Initializes state and runs the Streamlit UI."""
    st.set_page_config(layout="wide", page_title="Student Grades Manager")
    
    # 1. Initialize session state if not already set
    if 'grades' not in st.session_state:
        st.session_state.grades = load_grades()

    st.title("Student Grades Management Dashboard")
    st.markdown("A simple application to manage, view, and export student grades.")

    # 2. Sidebar Navigation
    page_options = {
        "📊 View All Records": view_all_records_page,
        "➕ Add New Record": add_record_page,
        "✍️ Update Marks": update_record_page,
        "🔍 Search by Roll Number": search_record_page,
        "🗑️ Delete Record": delete_record_page,
    }

    selection = st.sidebar.selectbox("Navigation", list(page_options.keys()))

    # 3. Dynamic Page Rendering
    page_options[selection]()
    
    # Export button (placed at the bottom of the sidebar)
    st.sidebar.markdown("---")
    
    df_export = grades_to_dataframe(st.session_state.grades)
    
    @st.cache_data
    def convert_df_to_csv(df):
        # IMPORTANT: Caching the conversion prevents computation on every rerun
        return df.to_csv(index=False).encode('utf-8')
    
    csv_data = convert_df_to_csv(df_export)
    
    st.sidebar.download_button(
        label="Export All Data (CSV)",
        data=csv_data,
        file_name='student_grades_report.csv',
        mime='text/csv',
        disabled=df_export.empty
    )

if __name__ == "__main__":
    streamlit_app()
