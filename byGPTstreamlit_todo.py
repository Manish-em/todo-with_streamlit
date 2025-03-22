import streamlit as st
import mysql.connector
from mysql.connector import Error

# Configure your MySQL database connection here.
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "uiiopp",
    "database": "todo_app"
}

def create_connection():
    """Create a connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"]
        )
        return connection
    except Error as e:
        st.error(f"Error connecting to MySQL: {e}")
        return None

def create_table():
    """Create tasks table if it doesn't exist."""
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                task VARCHAR(255) NOT NULL,
                status BOOLEAN DEFAULT FALSE
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()

def get_tasks():
    """Fetch all tasks from the database."""
    conn = create_connection()
    tasks = []
    if conn is not None:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tasks ORDER BY id DESC")
        tasks = cursor.fetchall()
        cursor.close()
        conn.close()
    return tasks

def add_task(task):
    """Insert a new task into the database."""
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (description) VALUES (%s)", (task,))
        conn.commit()
        cursor.close()
        conn.close()

def update_task(task_id, new_task):
    """Update the task text in the database."""
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET task = %s WHERE id = %s", (new_task, task_id))
        conn.commit()
        cursor.close()
        conn.close()

def mark_task_done(task_id, status=True):
    """Mark a task as done or undone."""
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET status = %s WHERE id = %s", (status, task_id))
        conn.commit()
        cursor.close()
        conn.close()

def delete_task(task_id):
    """Delete a task from the database."""
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        conn.commit()
        cursor.close()
        conn.close()

# Initialize the database table.
create_table()

# Streamlit UI
st.title("To-Do App")

# Form to add a new task
with st.form(key="new_task_form", clear_on_submit=True):
    new_task = st.text_input("Enter a new task")
    submit_button = st.form_submit_button(label="Add Task")
    if submit_button and new_task:
        add_task(new_task)
        st.success("Task added!")

# Fetch and display tasks
tasks = get_tasks()

if tasks:
    for task in tasks:
        col1, col2, col3, col4 = st.columns([4, 1, 1, 1])
        # Display task text with a strikethrough if done.
        task_text = task["description"]
        if task["status"]:
            task_text = f"~~{task_text}~~"
        col1.markdown(task_text)

        # Checkbox to mark task as done/undone.
        done = col2.checkbox("Done", value=task["status"], key=f"done_{task['id']}")
        if done != task["status"]:
            mark_task_done(task["id"], done)
            st.rerun()

        # Edit button
        if col3.button("Edit", key=f"edit_{task['id']}"):
            new_value = st.text_input("Edit Task", value=task["description"], key=f"edit_input_{task['id']}")
            if st.button("Save", key=f"save_{task['id']}"):
                update_task(task["id"], new_value)
                st.success("Task updated!")
                st.rerun()

        # Delete button
        if col4.button("Delete", key=f"delete_{task['id']}"):
            delete_task(task["id"])
            st.success("Task deleted!")
            st.rerun()
else:
    st.info("No tasks found. Add a task above!")
