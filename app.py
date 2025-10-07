# app.py
import streamlit as st
import pandas as pd
import os

# -------------------------------
# File setup
# -------------------------------
FILE_PATH = "grades.csv"

def load_data():
    if os.path.exists(FILE_PATH):
        return pd.read_csv(FILE_PATH)
    else:
        return pd.DataFrame(columns=[
            "Roll", "Subject1", "Subject2", "Subject3", "Subject4", "Subject5", "Total", "Average"
        ])

def save_data(df):
    df.to_csv(FILE_PATH, index=False)

# -------------------------------
# Record operations
# -------------------------------
def add_record(df, roll, marks):
    total = sum(marks)
    avg = total / len(marks)
    new_row = {
        "Roll": str(roll),
        "Subject1": marks[0],
        "Subject2": marks[1],
        "Subject3": marks[2],
        "Subject4": marks[3],
        "Subject5": marks[4],
        "Total": total,
        "Average": avg
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_data(df)
    st.success("✅ Record added successfully!")
    return df

def update_record(df, roll, marks):
    mask = df["Roll"].astype(str) == str(roll)
    if mask.any():
        idx = df[mask].index[0]
        total = sum(marks)
        avg = total / len(marks)
        df.loc[idx, ["Subject1","Subject2","Subject3","Subject4","Subject5"]] = marks
        df.loc[idx, ["Total","Average"]] = [total, avg]
        save_data(df)
        st.success("✅ Record updated successfully!")
    else:
        st.error("❌ Roll number not found!")
    return df

def delete_record(df, roll):
    if str(roll) in df["Roll"].astype(str).values:
        df = df[df["Roll"].astype(str) != str(roll)].reset_index(drop=True)
        save_data(df)
        st.warning("🗑 Record deleted successfully!")
    else:
        st.error("❌ Roll number not found!")
    return df

# -------------------------------
# Streamlit App
# -------------------------------
st.set_page_config(page_title="Student Grades Manager", layout="wide")
st.title("🎓 Student Grades Manager")

menu = st.sidebar.radio("Menu", ["Add", "View", "Update", "Delete", "Download CSV"])
df = load_data()

if menu == "Add":
    st.subheader("➕ Add Record")
    roll = st.text_input("Roll Number")
    marks = [st.number_input(f"Marks for Subject {i+1}", 0, 100, step=1, key=f"a{i}") for i in range(5)]
    if st.button("Add Record"):
        if not roll:
            st.error("Please enter Roll Number.")
        else:
            df = add_record(df, roll, marks)

elif menu == "View":
    st.subheader("📋 All Records")
    if df.empty:
        st.info("No records available yet.")
    else:
        st.dataframe(df)

elif menu == "Update":
    st.subheader("✏️ Update Record")
    roll = st.text_input("Roll Number to Update")
    marks = [st.number_input(f"New marks for Subject {i+1}", 0, 100, step=1, key=f"u{i}") for i in range(5)]
    if st.button("Update Record"):
        if not roll:
            st.error("Please enter Roll Number.")
        else:
            df = update_record(df, roll, marks)

elif menu == "Delete":
    st.subheader("🗑 Delete Record")
    roll = st.text_input("Roll Number to Delete")
    if st.button("Delete Record"):
        if not roll:
            st.error("Please enter Roll Number.")
        else:
            df = delete_record(df, roll)

elif menu == "Download CSV":
    st.subheader("⬇️ Download CSV File")
    if df.empty:
        st.info("No data to download.")
    else:
        csv = df.to_csv(index=False)
        st.download_button("Download grades.csv", csv, file_name="grades.csv", mime="text/csv")
