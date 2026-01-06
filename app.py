import streamlit as st
import sqlite3
import pandas as pd
import google.generativeai as genai

# Page Configuration
st.set_page_config(page_title="AI Manager", layout="wide")

# --- 🧠 AI SETUP (Gemini 3 Flash Preview) ---
genai.configure(api_key="AIzaSyCsjEoiX5IYEMWY69-vFXm1_-z_xDLCPfE")


def suggest_priority(task_description):
    try:
        model = genai.GenerativeModel('models/gemini-3-flash-preview')
        prompt = f"Analyze task urgency and importance. Return ONLY one word (Low, Medium, or High): {task_description}"
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"AI Error: {e}"

# --- 📂 DATABASE FUNCTIONS ---


def complete_task(task_id):
    conn = sqlite3.connect('management.db')
    c = conn.cursor()
    c.execute('UPDATE tasks SET status = "Completed" WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()


def delete_task(task_id):
    conn = sqlite3.connect('management.db')
    c = conn.cursor()
    c.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()


def add_task(title, desc, priority):
    conn = sqlite3.connect('management.db')
    c = conn.cursor()
    c.execute('INSERT INTO tasks (title, description, priority) VALUES (?, ?, ?)',
              (title, desc, priority))
    conn.commit()
    conn.close()


def view_all_tasks():
    conn = sqlite3.connect('management.db')
    c = conn.cursor()
    c.execute('SELECT * FROM tasks')
    data = c.fetchall()
    conn.close()
    return data


def delete_client(client_id):
    conn = sqlite3.connect('management.db')
    c = conn.cursor()
    c.execute('DELETE FROM clients WHERE id = ?', (client_id,))
    conn.commit()
    conn.close()


def add_client(name, email, project):
    conn = sqlite3.connect('management.db')
    c = conn.cursor()
    c.execute('INSERT INTO clients (name, email, project) VALUES (?, ?, ?)',
              (name, email, project))
    conn.commit()
    conn.close()


def view_all_clients():
    conn = sqlite3.connect('management.db')
    c = conn.cursor()
    c.execute('SELECT * FROM clients')
    data = c.fetchall()
    conn.close()
    return data


# --- 🚀 UI NAVIGATION ---
st.title("⚡ Nexus AI: Operations Hub")

# Session State check taake page change yaad rahe
if 'choice' not in st.session_state:
    st.session_state.choice = "Dashboard"

# Sidebar Title Update
st.sidebar.markdown("# ⚛️ Nexus Hub")
st.sidebar.write("---")
# Button 1: Dashboard
if st.sidebar.button("📊 Dashboard", use_container_width=True):
    st.session_state.choice = "Dashboard"

# Thora gap dene ke liye
st.sidebar.markdown("<div style='margin: 10px 0;'></div>",
                    unsafe_allow_html=True)

# Button 2: Tasks
if st.sidebar.button("📋 Tasks Manager", use_container_width=True):
    st.session_state.choice = "Tasks"

st.sidebar.markdown("<div style='margin: 10px 0;'></div>",
                    unsafe_allow_html=True)

# Button 3: Clients
if st.sidebar.button("👥 Client Hub", use_container_width=True):
    st.session_state.choice = "Clients"

# Puraane 'choice' variable ko session state se connect kar diya
choice = st.session_state.choice

# --- DASHBOARD PAGE ---
if choice == "Dashboard":
    st.subheader("📊 System Overview")

    all_t = view_all_tasks()
    all_c = view_all_clients()

    t_count = len(all_t)
    c_count = len(all_c)
    completed_count = len([t for t in all_t if t[4] == "Completed"])
    pending_count = t_count - completed_count

    # 4 Columns for alignment
    col1, col2, col3, col4 = st.columns(4)

    # Note: Text ko short rakha hai taake height barabar rahay
    with col1:
        st.info(f"**Total Tasks** \n## {t_count}")

    with col2:
        st.success(f"**Completed** \n## {completed_count}")

    with col3:
        st.warning(f"**Pending** \n## {pending_count}")

    with col4:
        st.error(f"**Clients** \n## {c_count}")
# --- TASKS PAGE ---
elif choice == "Tasks":
    st.subheader("➕ Add New Task")

    # AI Suggestion session state
    if 'ai_suggest' not in st.session_state:
        st.session_state.ai_suggest = ""

    with st.expander("Open Form to Add Task"):
        temp_desc = st.text_area("Step 1: Describe task for AI Analysis")
        if st.button("🤖 Analyze with AI"):
            if temp_desc:
                st.session_state.ai_suggest = suggest_priority(temp_desc)
                st.info(f"AI Suggestion: **{st.session_state.ai_suggest}**")

        st.divider()

        with st.form("TaskEntryForm", clear_on_submit=True):
            title = st.text_input("Task Name")
            final_desc = st.text_area("Final Description", value=temp_desc)
            priority = st.selectbox("Priority", ["Low", "Medium", "High"])

            if st.form_submit_button("Save Task to Database"):
                if title:
                    add_task(title, final_desc, priority)
                    st.success(f"Task '{title}' saved!")
                    st.session_state.ai_suggest = ""
                    st.rerun()

    st.divider()
    st.subheader("📋 Task List & Actions")
    all_tasks = view_all_tasks()

    if all_tasks:
        for task in all_tasks:
            # Table ki jagah interactive cards (taake buttons nazar aaein)
            t_id, t_title, t_desc, t_priority, t_status = task

            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])

                with col1:
                    status_icon = "✅" if t_status == "Completed" else "⏳"
                    st.markdown(f"### {status_icon} {t_title}")
                    st.write(
                        f"**Priority:** {t_priority} | **Status:** {t_status}")
                    st.caption(t_desc)

                with col2:
                    # YEH RAHI COMPLETED KI OPTION
                    if t_status == "Pending":
                        if st.button("Complete", key=f"comp_{t_id}"):
                            complete_task(t_id)
                            st.rerun()
                    else:
                        st.write("Done! 🎉")

                with col3:
                    # DELETE KI OPTION
                    if st.button("Delete", key=f"del_{t_id}"):
                        delete_task(t_id)
                        st.rerun()

                st.divider()
    else:
        st.write("No tasks found.")

# --- CLIENTS PAGE ---
elif choice == "Clients":
    st.subheader("👥 Client Management")
    with st.expander("➕ Add New Client"):
        with st.form("ClientEntryForm", clear_on_submit=True):
            c_name = st.text_input("Client Name")
            c_email = st.text_input("Client Email")
            c_project = st.text_input("Project Name")

            if st.form_submit_button("Save Client"):
                if c_name and c_email:
                    add_client(c_name, c_email, c_project)
                    st.success(f"Client '{c_name}' Added!")
                    st.rerun()

    st.divider()
    st.subheader("📋 Registered Clients")
    all_clients = view_all_clients()

    if all_clients:
        for client in all_clients:
            c_id, c_name, c_email, c_project = client

            with st.container():
                # 4 hissay text ke liye, 1 hissa button ke liye
                col1, col2 = st.columns([4, 1])

                with col1:
                    st.write(f"👤 **{c_name}**")
                    st.write(f"📧 {c_email} | 📁 Project: {c_project}")

                with col2:
                    st.write("")  # Alignment ke liye thori space
                    if st.button("Delete", key=f"del_client_{c_id}"):
                        delete_client(c_id)
                        st.rerun()

                st.divider()
    else:
        st.write("No clients found.")
