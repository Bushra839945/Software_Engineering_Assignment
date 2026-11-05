import streamlit as st
import requests
import pandas as pd

API = "http://127.0.0.1:5000/students"

st.set_page_config(page_title="Student Management", layout="centered")
st.title("🎓 Student Management System")

# Show success message saved before the last refresh
if "msg" in st.session_state:
    st.success(st.session_state.pop("msg"))


def fetch_students():
    try:
        r = requests.get(API, timeout=5)
        r.raise_for_status()
        return r.json()
    except requests.RequestException:
        st.error("Cannot reach the Flask API. Is app.py running?")
        st.stop()


students = fetch_students()

# ---------- Display ----------
st.subheader("All Students")
if students:
    st.dataframe(pd.DataFrame(students), hide_index=True)
else:
    st.info("No students yet. Add one below.")

# ---------- Add ----------
st.subheader("Add New Student")
with st.form("add_form", clear_on_submit=True):
    name = st.text_input("Name")
    dept = st.text_input("Department")
    email = st.text_input("Email")
    if st.form_submit_button("Add Student"):
        if not (name and dept and email):
            st.warning("Please fill all fields.")
        else:
            r = requests.post(API, json={"name": name, "department": dept, "email": email})
            if r.status_code == 201:
                st.session_state["msg"] = "Student added successfully!"
                st.rerun()
            else:
                st.error(r.json().get("error", "Failed to add student"))

# ---------- Update / Delete ----------
st.subheader("Update or Delete Student")
if students:
    selected = st.selectbox(
        "Select a student",
        students,
        format_func=lambda s: f"{s['id']} - {s['name']}",
    )
    sid = selected["id"]

    with st.form(f"update_form_{sid}"):
        new_name = st.text_input("Name", selected["name"])
        new_dept = st.text_input("Department", selected["department"])
        new_email = st.text_input("Email", selected["email"])
        if st.form_submit_button("Update Student"):
            r = requests.put(f"{API}/{sid}", json={
                "name": new_name, "department": new_dept, "email": new_email})
            if r.status_code == 200:
                st.session_state["msg"] = "Student updated successfully!"
                st.rerun()
            else:
                st.error(r.json().get("error", "Failed to update student"))

    if st.button("Delete Student", type="primary"):
        r = requests.delete(f"{API}/{sid}")
        if r.status_code == 200:
            st.session_state["msg"] = "Student deleted successfully!"
            st.rerun()
        else:
            st.error(r.json().get("error", "Failed to delete student"))
else:
    st.caption("Nothing to update or delete yet.")