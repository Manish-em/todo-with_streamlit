import streamlit as st
from pymongo import MongoClient
from datetime import datetime

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['todo_db']
tasks_collection = db['tasks']

# Initialize session state for tasks and editing
if "tasks" not in st.session_state:
    # Load tasks from MongoDB
    st.session_state.tasks = list(tasks_collection.find())
if "editing_task_id" not in st.session_state:
    st.session_state.editing_task_id = None
if "edit_text" not in st.session_state:
    st.session_state.edit_text = ""

st.title("📝 Simple To-Do App")

# Input field to add tasks
new_task = st.text_input("Add a new task:")

if st.button("Add Task") and new_task:
    # Create new task document
    task_doc = {
        "task": new_task,
        "completed": False,
        "created_at": datetime.now()
    }
    
    # Insert into MongoDB
    tasks_collection.insert_one(task_doc)
    
    # Update session state
    st.session_state.tasks = list(tasks_collection.find())
    st.rerun()

# Display the task list
st.write("### Your Tasks:")
for task in st.session_state.tasks:
    # Create four columns: task text, mark done button, edit button, and delete button
    col1, col2, col3, col4 = st.columns([0.5, 0.15, 0.15, 0.15])
    
    # Task text
    if st.session_state.editing_task_id == task['_id']:
        # Show edit input field
        edited_text = st.text_input("Edit task:", value=task['task'], key=f"edit_{task['_id']}")
        if st.button("Save", key=f"save_{task['_id']}"):
            tasks_collection.update_one(
                {"_id": task["_id"]},
                {"$set": {"task": edited_text}}
            )
            st.session_state.tasks = list(tasks_collection.find())
            st.session_state.editing_task_id = None
            st.session_state.edit_text = ""
            st.rerun()
        if st.button("Cancel", key=f"cancel_{task['_id']}"):
            st.session_state.editing_task_id = None
            st.session_state.edit_text = ""
            st.rerun()
    else:
        col1.write(f"✅ {task['task']}" if task["completed"] else f"🔲 {task['task']}")
    
    # Mark Done button
    if col2.button("Mark Done", key=f"done_{task['_id']}"):
        tasks_collection.update_one(
            {"_id": task["_id"]},
            {"$set": {"completed": True}}
        )
        st.session_state.tasks = list(tasks_collection.find())
        st.rerun()
    
    # Edit button
    if col3.button("Edit", key=f"edit_btn_{task['_id']}"):
        st.session_state.editing_task_id = task['_id']
        st.session_state.edit_text = task['task']
        st.rerun()
    
    # Delete button
    if col4.button("Delete", key=f"delete_{task['_id']}"):
        tasks_collection.delete_one({"_id": task["_id"]})
        st.session_state.tasks = list(tasks_collection.find())
        st.rerun()
