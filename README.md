# Project Management Tool (Streamlit)

A local project-management web application inspired by the supplied screenshots.
It uses a peach, cream, white, and orange design.

## Features
- Dashboard with project/task metrics and charts
- Project create, view, update, and delete
- Task assignment, priorities, deadlines, and status updates
- Kanban-style task board
- Team member management
- Project file upload and download
- Time tracking
- Reports and CSV export

## Run locally (Windows)
1. Install Python 3.9 or newer.
2. Extract this ZIP folder.
3. Open Command Prompt in this folder.
4. Install dependencies:

   `python -m pip install -r requirements.txt`

5. Start the website:

   `streamlit run app.py`

6. Open the local URL shown in the terminal (usually http://localhost:8501).

## Database
By default, the app creates `project_management.db` (SQLite) in this folder. This is the easiest option for local testing.

To use MySQL instead, create a database first, install the dependencies, and set the `DATABASE_URL` environment variable before starting Streamlit.

Windows Command Prompt example:

`set DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/project_management`

Then run:

`streamlit run app.py`

Replace `YOUR_PASSWORD` with your MySQL password. Do not share database credentials.

## Notes
- Uploaded files are stored in the `uploaded_files/` folder.
- The database and uploaded files are created locally when you use the app.
- The Kanban board changes task status using the “Move to” selector (rather than drag-and-drop).
- This is a learning/demo starter application. Add production authentication, authorization, validation, backups, and deployment security before using it with real business data.
