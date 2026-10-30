import os
from pathlib import Path
from datetime import date, datetime, time
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text

# ------------------------------------------------------------
# Project Management Tool - Streamlit local application
# Default database: SQLite. Set DATABASE_URL to use MySQL.
# Example:
# mysql+pymysql://root:password@localhost:3306/project_management
# ------------------------------------------------------------

st.set_page_config(
    page_title="Project Management Tool",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///project_management.db")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    pool_pre_ping=True,
)

STATUSES = ["To Do", "In Progress", "In Review", "Completed"]
PRIORITIES = ["High", "Medium", "Low"]


def init_db():
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                manager TEXT,
                start_date TEXT,
                deadline TEXT,
                status TEXT DEFAULT 'Planning',
                progress INTEGER DEFAULT 0,
                created_at TEXT
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS team_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                role TEXT,
                created_at TEXT
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                title TEXT NOT NULL,
                description TEXT,
                assignee TEXT,
                priority TEXT DEFAULT 'Medium',
                status TEXT DEFAULT 'To Do',
                due_date TEXT,
                estimated_hours REAL DEFAULT 0,
                created_at TEXT
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                author TEXT,
                message TEXT,
                created_at TEXT
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS project_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                filename TEXT,
                stored_path TEXT,
                uploaded_at TEXT
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS time_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                member TEXT,
                work_date TEXT,
                hours REAL,
                notes TEXT,
                created_at TEXT
            )
        """))


def read_df(query, params=None):
    with engine.connect() as conn:
        return pd.read_sql(text(query), conn, params=params or {})


def execute(query, params=None):
    with engine.begin() as conn:
        result = conn.execute(text(query), params or {})
        return result.lastrowid


def seed_data():
    projects = read_df("SELECT id FROM projects")
    if not projects.empty:
        return
    p1 = execute(
        """INSERT INTO projects(name, description, manager, start_date, deadline, status, progress, created_at)
           VALUES(:name,:description,:manager,:start_date,:deadline,:status,:progress,:created_at)""",
        {"name": "Website Redesign", "description": "Refresh the company website and improve user experience.",
         "manager": "Alex Morgan", "start_date": str(date.today()), "deadline": str(date.today()),
         "status": "Active", "progress": 65, "created_at": datetime.now().isoformat(timespec="seconds")}
    )
    p2 = execute(
        """INSERT INTO projects(name, description, manager, start_date, deadline, status, progress, created_at)
           VALUES(:name,:description,:manager,:start_date,:deadline,:status,:progress,:created_at)""",
        {"name": "Mobile App Launch", "description": "Plan and deliver the first mobile application release.",
         "manager": "Jamie Lee", "start_date": str(date.today()), "deadline": str(date.today()),
         "status": "Planning", "progress": 20, "created_at": datetime.now().isoformat(timespec="seconds")}
    )
    for name, email, role in [
        ("Alex Morgan", "alex@example.com", "Project Manager"),
        ("Jamie Lee", "jamie@example.com", "Developer"),
        ("Taylor Smith", "taylor@example.com", "Designer"),
    ]:
        execute("INSERT INTO team_members(name,email,role,created_at) VALUES(:n,:e,:r,:c)",
                {"n": name, "e": email, "r": role, "c": datetime.now().isoformat(timespec="seconds")})
    for vals in [
        (p1, "Prepare homepage wireframe", "Taylor Smith", "High", "In Progress"),
        (p1, "Build responsive navigation", "Jamie Lee", "Medium", "To Do"),
        (p2, "Define launch checklist", "Alex Morgan", "High", "In Review"),
    ]:
        execute("""INSERT INTO tasks(project_id,title,assignee,priority,status,due_date,created_at)
                   VALUES(:p,:t,:a,:pr,:s,:d,:c)""",
                {"p": vals[0], "t": vals[1], "a": vals[2], "pr": vals[3], "s": vals[4],
                 "d": str(date.today()), "c": datetime.now().isoformat(timespec="seconds")})


init_db()
seed_data()

# -------------------- Styling --------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #fffaf7; color: #24212d; }
section[data-testid="stSidebar"] { background: #fff0e6; border-right: 1px solid #f6dfd2; }
.block-container { padding-top: 1.6rem; padding-bottom: 2.5rem; max-width: 1450px; }
.hero {
  background: linear-gradient(115deg, #fff0e6 0%, #fff8f3 65%, #ffe2d1 100%);
  border: 1px solid #f5d7c7; border-radius: 22px; padding: 25px 28px; margin-bottom: 22px;
}
.hero h1 { color: #24212d; font-size: 2rem; margin: 0 0 7px 0; font-weight: 800; }
.hero p { color: #d96535; font-size: 1rem; margin: 0; font-weight: 600; }
.metric-card {
  background: white; border: 1px solid #f2dfd5; border-radius: 17px;
  padding: 17px 18px; box-shadow: 0 5px 18px rgba(82,45,25,.04);
}
.metric-label { color: #77717a; font-size: .86rem; font-weight: 600; }
.metric-value { color: #24212d; font-size: 1.8rem; font-weight: 800; margin-top: 5px; }
.section-title { font-size: 1.18rem; font-weight: 750; color: #24212d; margin: 8px 0 12px 0; }
div.stButton > button, div[data-testid="stFormSubmitButton"] button {
  background: #f47745; color: white; border: 0; border-radius: 10px;
  font-weight: 650; min-height: 2.55rem;
}
div.stButton > button:hover, div[data-testid="stFormSubmitButton"] button:hover {
  background: #df6334; color: white; border: 0;
}
[data-testid="stDataFrame"] { border: 1px solid #f2dfd5; border-radius: 12px; overflow: hidden; }
div[data-baseweb="input"] input, div[data-baseweb="textarea"] textarea { border-radius: 9px; }
.small-note { color: #77717a; font-size: .82rem; }
</style>
""", unsafe_allow_html=True)

# -------------------- Helpers --------------------
def options_for_projects():
    df = read_df("SELECT id, name FROM projects ORDER BY name")
    return {int(r.id): r.name for r in df.itertuples()} if not df.empty else {}

def options_for_members():
    df = read_df("SELECT name FROM team_members ORDER BY name")
    return df["name"].tolist() if not df.empty else []

def refresh():
    st.rerun()

def metric(label, value, icon):
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">{icon} &nbsp;{label}</div>'
        f'<div class="metric-value">{value}</div></div>', unsafe_allow_html=True
    )

# -------------------- Sidebar --------------------
with st.sidebar:
    st.markdown("## 📊 ProjectFlow")
    st.caption("PROJECT MANAGEMENT WORKSPACE")
    page = st.radio(
        "NAVIGATION",
        ["Dashboard", "Projects", "Tasks", "Kanban Board", "Team", "Files", "Time Tracking", "Reports"],
        label_visibility="visible",
    )
    st.divider()
    st.markdown("**Workspace status**")
    st.success("Database connected")
    st.caption("Local Streamlit application")
    st.caption("Peach • Cream • Orange theme")

st.markdown(
    '<div class="hero"><h1>📊 Project Management Tool</h1>'
    '<p>Plan projects, assign tasks, collaborate with your team, and track progress in one place.</p></div>',
    unsafe_allow_html=True
)

projects_map = options_for_projects()
members = options_for_members()

# -------------------- Dashboard --------------------
if page == "Dashboard":
    projects = read_df("SELECT * FROM projects ORDER BY id DESC")
    tasks = read_df("SELECT * FROM tasks")
    team = read_df("SELECT * FROM team_members")
    total_projects = len(projects)
    active_projects = int((projects["status"] == "Active").sum()) if not projects.empty else 0
    completed_projects = int((projects["status"] == "Completed").sum()) if not projects.empty else 0
    pending_tasks = int((tasks["status"] != "Completed").sum()) if not tasks.empty else 0
    overdue = int(((tasks["due_date"] < str(date.today())) & (tasks["status"] != "Completed")).sum()) if not tasks.empty else 0

    cols = st.columns(5)
    for col, label, value, icon in zip(
        cols, ["Total Projects", "Active Projects", "Completed Projects", "Pending Tasks", "Overdue Tasks"],
        [total_projects, active_projects, completed_projects, pending_tasks, overdue],
        ["📁", "🚀", "✅", "📌", "⏰"]
    ):
        with col:
            metric(label, value, icon)

    st.write("")
    left, right = st.columns([1.15, 1])
    with left:
        st.markdown('<div class="section-title">Project progress</div>', unsafe_allow_html=True)
        if not projects.empty:
            fig = px.bar(projects, x="name", y="progress", color="status", text="progress",
                         range_y=[0, 100], labels={"name": "Project", "progress": "Progress (%)", "status": "Status"})
            fig.update_layout(height=340, plot_bgcolor="white", paper_bgcolor="white",
                              margin=dict(l=10,r=10,t=20,b=10), legend_title_text="")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Create a project to see progress here.")
    with right:
        st.markdown('<div class="section-title">Task status overview</div>', unsafe_allow_html=True)
        if not tasks.empty:
            status_df = tasks.groupby("status").size().reset_index(name="tasks")
            fig = px.pie(status_df, names="status", values="tasks", hole=.58)
            fig.update_layout(height=340, margin=dict(l=10,r=10,t=20,b=10), legend_title_text="")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Add tasks to see the status overview.")

    st.markdown('<div class="section-title">Recent projects</div>', unsafe_allow_html=True)
    if not projects.empty:
        show = projects[["name", "manager", "start_date", "deadline", "status", "progress"]].copy()
        st.dataframe(show, use_container_width=True, hide_index=True)
    st.markdown('<div class="section-title">Upcoming task deadlines</div>', unsafe_allow_html=True)
    if not tasks.empty:
        upcoming = tasks[ tasks["status"] != "Completed" ].sort_values("due_date").head(6)
        st.dataframe(upcoming[["title", "assignee", "priority", "status", "due_date"]],
                     use_container_width=True, hide_index=True)

# -------------------- Projects --------------------
elif page == "Projects":
    st.markdown('<div class="section-title">📁 Project management</div>', unsafe_allow_html=True)
    with st.expander("＋ Create a new project", expanded=False):
        with st.form("new_project"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Project name *")
            manager = c2.selectbox("Project manager", ["Not assigned"] + members)
            description = st.text_area("Description")
            c3, c4, c5 = st.columns(3)
            start = c3.date_input("Start date", value=date.today())
            deadline = c4.date_input("Deadline", value=date.today())
            status = c5.selectbox("Project status", ["Planning", "Active", "On Hold", "Completed"])
            progress = st.slider("Progress", 0, 100, 0)
            submitted = st.form_submit_button("Create project")
            if submitted:
                if not name.strip():
                    st.error("Please enter a project name.")
                elif deadline < start:
                    st.error("Deadline cannot be earlier than the start date.")
                else:
                    execute("""INSERT INTO projects(name,description,manager,start_date,deadline,status,progress,created_at)
                               VALUES(:n,:d,:m,:s,:dl,:st,:p,:c)""",
                            {"n": name.strip(), "d": description, "m": manager, "s": str(start),
                             "dl": str(deadline), "st": status, "p": progress,
                             "c": datetime.now().isoformat(timespec="seconds")})
                    st.success("Project created successfully.")
                    refresh()

    projects = read_df("SELECT * FROM projects ORDER BY id DESC")
    if not projects.empty:
        st.dataframe(projects[["id","name","manager","start_date","deadline","status","progress"]],
                     use_container_width=True, hide_index=True)
        st.markdown("**Update or delete a project**")
        selected = st.selectbox("Select project", projects["id"].tolist(),
                                format_func=lambda x: f"{x} — {projects.loc[projects.id == x, 'name'].iloc[0]}")
        row = projects[projects.id == selected].iloc[0]
        with st.form("edit_project"):
            ename = st.text_input("Project name", row["name"])
            emanager = st.text_input("Manager", row["manager"] or "")
            edesc = st.text_area("Description", row["description"] or "")
            c1, c2, c3 = st.columns(3)
            estart = c1.date_input("Start date", value=pd.to_datetime(row["start_date"]).date())
            edeadline = c2.date_input("Deadline", value=pd.to_datetime(row["deadline"]).date())
            estatus = c3.selectbox("Status", ["Planning", "Active", "On Hold", "Completed"],
                                   index=["Planning", "Active", "On Hold", "Completed"].index(row["status"]))
            eprogress = st.slider("Progress (%)", 0, 100, int(row["progress"]))
            save = st.form_submit_button("Save changes")
            if save:
                execute("""UPDATE projects SET name=:n,manager=:m,description=:d,start_date=:s,
                           deadline=:dl,status=:st,progress=:p WHERE id=:id""",
                         {"n": ename, "m": emanager, "d": edesc, "s": str(estart), "dl": str(edeadline),
                          "st": estatus, "p": eprogress, "id": int(selected)})
                st.success("Project updated.")
                refresh()
        if st.button("🗑️ Delete selected project", type="secondary"):
            execute("DELETE FROM projects WHERE id=:id", {"id": int(selected)})
            execute("DELETE FROM tasks WHERE project_id=:id", {"id": int(selected)})
            execute("DELETE FROM comments WHERE project_id=:id", {"id": int(selected)})
            execute("DELETE FROM project_files WHERE project_id=:id", {"id": int(selected)})
            st.success("Project and its related tasks were deleted.")
            refresh()
    else:
        st.info("No projects yet. Create your first project above.")

# -------------------- Tasks --------------------
elif page == "Tasks":
    st.markdown('<div class="section-title">📌 Task assignment</div>', unsafe_allow_html=True)
    if not projects_map:
        st.warning("Create a project first, then add tasks.")
    else:
        with st.expander("＋ Add a task", expanded=False):
            with st.form("new_task"):
                title = st.text_input("Task title *")
                project_id = st.selectbox("Project", list(projects_map), format_func=lambda x: projects_map[x])
                desc = st.text_area("Description")
                c1, c2, c3 = st.columns(3)
                assignee = c1.selectbox("Assign to", ["Unassigned"] + members)
                priority = c2.selectbox("Priority", PRIORITIES, index=1)
                status = c3.selectbox("Status", STATUSES)
                c4, c5 = st.columns(2)
                due = c4.date_input("Due date", value=date.today())
                estimate = c5.number_input("Estimated hours", min_value=0.0, step=0.5)
                add = st.form_submit_button("Add task")
                if add:
                    if not title.strip():
                        st.error("Please enter a task title.")
                    else:
                        execute("""INSERT INTO tasks(project_id,title,description,assignee,priority,status,due_date,estimated_hours,created_at)
                                   VALUES(:p,:t,:d,:a,:pr,:s,:due,:h,:c)""",
                                {"p": int(project_id), "t": title.strip(), "d": desc, "a": assignee,
                                 "pr": priority, "s": status, "due": str(due), "h": estimate,
                                 "c": datetime.now().isoformat(timespec="seconds")})
                        st.success("Task added.")
                        refresh()
        tasks = read_df("""SELECT tasks.*, projects.name AS project_name FROM tasks
                           LEFT JOIN projects ON projects.id=tasks.project_id ORDER BY tasks.id DESC""")
        if not tasks.empty:
            f1, f2 = st.columns(2)
            selected_status = f1.multiselect("Filter by status", STATUSES, default=STATUSES)
            selected_priority = f2.multiselect("Filter by priority", PRIORITIES, default=PRIORITIES)
            filtered = tasks[tasks.status.isin(selected_status) & tasks.priority.isin(selected_priority)]
            st.dataframe(filtered[["id","title","project_name","assignee","priority","status","due_date","estimated_hours"]],
                         use_container_width=True, hide_index=True)
            st.markdown("**Update task status or details**")
            task_id = st.selectbox("Select task ID", tasks["id"].tolist(),
                                   format_func=lambda x: f"#{x} — {tasks.loc[tasks.id == x, 'title'].iloc[0]}")
            tr = tasks[tasks.id == task_id].iloc[0]
            with st.form("edit_task"):
                etitle = st.text_input("Title", tr["title"])
                edescription = st.text_area("Description", tr["description"] or "")
                ec1, ec2, ec3 = st.columns(3)
                eassignee = ec1.text_input("Assignee", tr["assignee"] or "")
                epriority = ec2.selectbox("Priority", PRIORITIES, index=PRIORITIES.index(tr["priority"]))
                estatus = ec3.selectbox("Status", STATUSES, index=STATUSES.index(tr["status"]))
                edue = st.date_input("Due date", value=pd.to_datetime(tr["due_date"]).date())
                ehours = st.number_input("Estimated hours", min_value=0.0, value=float(tr["estimated_hours"] or 0), step=0.5)
                save_task = st.form_submit_button("Save task")
                if save_task:
                    execute("""UPDATE tasks SET title=:t,description=:d,assignee=:a,priority=:p,status=:s,
                               due_date=:due,estimated_hours=:h WHERE id=:id""",
                             {"t": etitle, "d": edescription, "a": eassignee, "p": epriority,
                              "s": estatus, "due": str(edue), "h": ehours, "id": int(task_id)})
                    st.success("Task updated.")
                    refresh()
            if st.button("🗑️ Delete selected task"):
                execute("DELETE FROM tasks WHERE id=:id", {"id": int(task_id)})
                st.success("Task deleted.")
                refresh()
        else:
            st.info("No tasks have been added yet.")

# -------------------- Kanban --------------------
elif page == "Kanban Board":
    st.markdown('<div class="section-title">🗂️ Kanban board</div>', unsafe_allow_html=True)
    tasks = read_df("""SELECT tasks.*, projects.name AS project_name FROM tasks
                       LEFT JOIN projects ON projects.id=tasks.project_id ORDER BY tasks.id DESC""")
    if tasks.empty:
        st.info("Add tasks to populate your Kanban board.")
    else:
        columns = st.columns(4)
        for col, status in zip(columns, STATUSES):
            with col:
                st.markdown(f"### {status}")
                subset = tasks[tasks.status == status]
                st.caption(f"{len(subset)} task(s)")
                for _, task in subset.iterrows():
                    with st.container(border=True):
                        st.markdown(f"**{task['title']}**")
                        st.caption(task["project_name"] or "No project")
                        st.write(f"👤 {task['assignee'] or 'Unassigned'}")
                        st.write(f"Priority: **{task['priority']}**")
                        new_status = st.selectbox("Move to", STATUSES, index=STATUSES.index(status),
                                                  key=f"kanban_{int(task['id'])}")
                        if new_status != status:
                            execute("UPDATE tasks SET status=:s WHERE id=:id",
                                    {"s": new_status, "id": int(task["id"])})
                            refresh()

# -------------------- Team --------------------
elif page == "Team":
    st.markdown('<div class="section-title">👥 Team members</div>', unsafe_allow_html=True)
    with st.expander("＋ Add team member"):
        with st.form("new_member"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Full name *")
            email = c2.text_input("Email address")
            role = st.selectbox("Role", ["Project Manager", "Developer", "Designer", "Analyst", "Other"])
            add_member = st.form_submit_button("Add member")
            if add_member:
                if not name.strip():
                    st.error("Please enter a name.")
                else:
                    execute("INSERT INTO team_members(name,email,role,created_at) VALUES(:n,:e,:r,:c)",
                            {"n": name.strip(), "e": email, "r": role, "c": datetime.now().isoformat(timespec="seconds")})
                    st.success("Team member added.")
                    refresh()
    team = read_df("SELECT * FROM team_members ORDER BY name")
    if not team.empty:
        st.dataframe(team[["id","name","email","role"]], use_container_width=True, hide_index=True)
        member_id = st.selectbox("Member to remove", team["id"].tolist(),
                                 format_func=lambda x: f"{x} — {team.loc[team.id == x, 'name'].iloc[0]}")
        if st.button("Remove member"):
            execute("DELETE FROM team_members WHERE id=:id", {"id": int(member_id)})
            st.success("Member removed.")
            refresh()
    else:
        st.info("No team members yet.")

# -------------------- Files --------------------
elif page == "Files":
    st.markdown('<div class="section-title">📎 Project file sharing</div>', unsafe_allow_html=True)
    if not projects_map:
        st.info("Create a project before uploading files.")
    else:
        project_id = st.selectbox("Choose project", list(projects_map), format_func=lambda x: projects_map[x])
        uploaded = st.file_uploader("Upload a project file", type=["pdf","png","jpg","jpeg","doc","docx","xls","xlsx","csv","txt","zip"])
        if uploaded is not None and st.button("Save uploaded file"):
            folder = Path("uploaded_files") / str(project_id)
            folder.mkdir(parents=True, exist_ok=True)
            safe_name = Path(uploaded.name).name
            destination = folder / safe_name
            destination.write_bytes(uploaded.getbuffer())
            execute("""INSERT INTO project_files(project_id,filename,stored_path,uploaded_at)
                       VALUES(:p,:f,:s,:u)""",
                    {"p": int(project_id), "f": safe_name, "s": str(destination),
                     "u": datetime.now().isoformat(timespec="seconds")})
            st.success("File uploaded.")
            refresh()
        files = read_df("SELECT * FROM project_files WHERE project_id=:p ORDER BY id DESC", {"p": int(project_id)})
        if not files.empty:
            for _, file_row in files.iterrows():
                path = Path(file_row["stored_path"])
                if path.exists():
                    st.download_button(f"⬇️ {file_row['filename']}", data=path.read_bytes(),
                                       file_name=file_row["filename"], key=f"download_{int(file_row['id'])}")
                else:
                    st.warning(f"{file_row['filename']} is listed but its local file is missing.")

# -------------------- Time tracking --------------------
elif page == "Time Tracking":
    st.markdown('<div class="section-title">⏱️ Time tracking</div>', unsafe_allow_html=True)
    tasks = read_df("SELECT id,title FROM tasks ORDER BY title")
    if tasks.empty:
        st.info("Add a task before recording time.")
    else:
        with st.form("time_entry"):
            task_id = st.selectbox("Task", tasks["id"].tolist(),
                                   format_func=lambda x: f"{x} — {tasks.loc[tasks.id == x, 'title'].iloc[0]}")
            member = st.selectbox("Team member", ["Unassigned"] + members)
            work_date = st.date_input("Work date", value=date.today())
            hours = st.number_input("Hours spent", min_value=0.25, max_value=24.0, value=1.0, step=0.25)
            notes = st.text_input("Work notes")
            add_time = st.form_submit_button("Record time")
            if add_time:
                execute("""INSERT INTO time_entries(task_id,member,work_date,hours,notes,created_at)
                           VALUES(:t,:m,:d,:h,:n,:c)""",
                         {"t": int(task_id), "m": member, "d": str(work_date), "h": hours,
                          "n": notes, "c": datetime.now().isoformat(timespec="seconds")})
                st.success("Time entry saved.")
                refresh()
    entries = read_df("""SELECT time_entries.*, tasks.title AS task_title FROM time_entries
                         LEFT JOIN tasks ON tasks.id=time_entries.task_id ORDER BY work_date DESC""")
    if not entries.empty:
        st.metric("Total recorded hours", f"{entries['hours'].sum():.2f} hrs")
        st.dataframe(entries[["work_date","task_title","member","hours","notes"]],
                     use_container_width=True, hide_index=True)
        summary = entries.groupby("member", as_index=False)["hours"].sum()
        fig = px.bar(summary, x="member", y="hours", title="Hours by team member")
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No time entries recorded yet.")

# -------------------- Reports --------------------
elif page == "Reports":
    st.markdown('<div class="section-title">📈 Reports and analytics</div>', unsafe_allow_html=True)
    projects = read_df("SELECT * FROM projects")
    tasks = read_df("SELECT * FROM tasks")
    if not projects.empty:
        a, b = st.columns(2)
        with a:
            pstatus = projects.groupby("status").size().reset_index(name="count")
            fig = px.pie(pstatus, names="status", values="count", title="Projects by status", hole=.45)
            st.plotly_chart(fig, use_container_width=True)
        with b:
            priority = tasks.groupby("priority").size().reset_index(name="count") if not tasks.empty else pd.DataFrame()
            if not priority.empty:
                fig = px.bar(priority, x="priority", y="count", color="priority", title="Tasks by priority")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Add tasks to see priority analytics.")
        st.markdown("**Project report**")
        st.dataframe(projects[["name","manager","status","progress","start_date","deadline"]],
                     use_container_width=True, hide_index=True)
        st.download_button("⬇️ Download project report (CSV)",
                           data=projects.to_csv(index=False).encode("utf-8"),
                           file_name="project_report.csv", mime="text/csv")
    else:
        st.info("Create projects to generate reports.")

st.divider()
st.markdown(
    '<p class="small-note">Project Management Tool • Built with Streamlit and Python • '
    'Data is stored locally in your configured database.</p>', unsafe_allow_html=True
)



# -------------------- White & Gray theme override --------------------
st.markdown("""
<style>
.stApp { background: #f4f5f7 !important; color: #111111 !important; }
html, body, [class*="css"], p, label, span, div { color: inherit; }
section[data-testid="stSidebar"] {
  background: #eeeeef !important;
  border-right: 1px solid #d7d9dd !important;
}
section[data-testid="stSidebar"] * { color: #111111 !important; }
.hero {
  background: #ffffff !important;
  border: 1px solid #d9dce1 !important;
  box-shadow: 0 4px 16px rgba(0,0,0,.04) !important;
}
.hero h1, .hero p { color: #111111 !important; }
.metric-card {
  background: #ffffff !important;
  border: 1px solid #d9dce1 !important;
  box-shadow: 0 3px 12px rgba(0,0,0,.035) !important;
}
.metric-label, .metric-value, .section-title, .small-note {
  color: #111111 !important;
}
div.stButton > button, div[data-testid="stFormSubmitButton"] button {
  background: #e5e7eb !important;
  color: #111111 !important;
  border: 1px solid #c9cdd3 !important;
  border-radius: 9px !important;
  font-weight: 650 !important;
}
div.stButton > button:hover, div[data-testid="stFormSubmitButton"] button:hover {
  background: #d5d8dd !important;
  color: #000000 !important;
  border: 1px solid #aeb4bd !important;
}
[data-testid="stDataFrame"], [data-testid="stTable"] {
  background: #ffffff !important;
  border: 1px solid #d9dce1 !important;
}
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea,
div[data-baseweb="select"] > div {
  background: #ffffff !important;
  color: #111111 !important;
  border-color: #c9cdd3 !important;
}
div[data-baseweb="input"] input::placeholder,
div[data-baseweb="textarea"] textarea::placeholder { color: #666666 !important; }
[data-testid="stExpander"] {
  background: #ffffff !important;
  border: 1px solid #d9dce1 !important;
  border-radius: 12px !important;
}
[data-testid="stMetric"] {
  background: #ffffff !important;
  border: 1px solid #d9dce1 !important;
  border-radius: 12px !important;
  padding: 12px !important;
}
[data-testid="stAlert"] { color: #111111 !important; }
h1, h2, h3, h4, h5, h6 { color: #111111 !important; }
</style>
""", unsafe_allow_html=True)
