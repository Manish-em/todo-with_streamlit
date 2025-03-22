import streamlit as st
import pandas as pd

conn = st.connection("mysql", type="sql")



if 'tasks' not in st.session_state:
    st.session_state.tasks = conn.query("SELECT * FROM tasks", ttl=0)



def add_task(description):
    conn = st.connection("mysql", type="sql")
    conn.query("INSERT INTO tasks (description) VALUES (%s)", params=(description,), ttl=0)
    new_id = conn.query("SELECT LAST_INSERT_ID()", ttl=0).iloc[0, 0]
    new_task_df = pd.DataFrame({'id': [new_id], 'description': [description], 'status': [0]})
    st.session_state.tasks = pd.concat([st.session_state.tasks, new_task_df], ignore_index=True)

def update_status(task_id, status):
    conn.query("UPDATE tasks SET status = %s WHERE id = %s", (status, task_id), ttl=0)
    idx = st.session_state.tasks.index[st.session_state.tasks['id'] == task_id].tolist()[0]
    st.session_state.tasks.at[idx, 'status'] = status


def update_task(task_id, new_description):
    conn.query("UPDATE tasks SET description = %s WHERE id = %s", (new_description, task_id), ttl=0)
    idx = st.session_state.tasks.index[st.session_state.tasks['id'] == task_id].tolist()[0]
    st.session_state.tasks.at[idx, 'description'] = new_description


def delete_task(task_id):
    conn.query("DELETE FROM tasks WHERE id = %s", (task_id,), ttl=0)
    st.session_state.tasks = st.session_state.tasks[st.session_state.tasks['id'] != task_id]



st.header("Add New Task")
new_task = st.text_input("Enter task description")
if st.button("Add Task"):
    if new_task:
        add_task(new_task)
        st.success("Task added")


st.header("Tasks")
if not st.session_state.tasks.empty:
    for idx, task in st.session_state.tasks.iterrows():
        st.write(f"{task['description']} - {'Done' if task['status'] else 'Not Done'}")
        done = st.checkbox("Done", value=bool(task['status']), key=f"done_{task['id']}")
        if done != bool(task['status']):
            update_status(task['id'], 1 if done else 0)
        # Edit and delete buttons follow
else:
    st.write("No tasks yet.")