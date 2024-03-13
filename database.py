import sqlite3
from datetime import datetime

today_date = datetime.today().date()
formatted_date = today_date.strftime("%Y-%m-%d")



# Connect to SQLite database (this will create a new database file if it doesn't exist)
def connect():
    return sqlite3.connect('study_group_bot.db')

def execute_query(conn, query, values=None):
    cursor = conn.cursor()
    if values:
        cursor.execute(query, values)
    else:
        cursor.execute(query)
    conn.commit()

def close_connection(conn):
    conn.close()


def create_tables():
    conn = connect()

    # Create a table for users
    execute_query(conn, '''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER,
            username TEXT,
            chat_id INTEGER,
            registration_date TEXT
        )
    ''')

    # Create a table for study groups
    execute_query(conn, '''
        CREATE TABLE IF NOT EXISTS study_groups (
            group_id INTEGER PRIMARY KEY,
            group_name TEXT,
            admin_id INTEGER,
            creation_date TEXT
        )
    ''')

    execute_query(conn, '''
        CREATE TABLE IF NOT EXISTS threads (
            thread_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            title TEXT,
            content TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')

    # members
    execute_query(conn, '''
        CREATE TABLE IF NOT EXISTS group_members (
            member_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            group_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (group_id) REFERENCES study_groups (group_id)
        )
    ''')
    
    execute_query(conn, '''
        CREATE TABLE IF NOT EXISTS thread_members (
            member_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            thread_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (thread_id) REFERENCES threads (thread_id)
        )
    ''')

    # Create a table for study sessions
    execute_query(conn, '''
        CREATE TABLE IF NOT EXISTS study_sessions (
            session_id INTEGER PRIMARY KEY,
            group_id INTEGER,
            session_date TEXT,
            topic TEXT,
            FOREIGN KEY (group_id) REFERENCES study_groups (group_id)
        )
    ''')


    

    execute_query(conn, '''
        CREATE TABLE IF NOT EXISTS replies (
            reply_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            thread_id INTEGER,
            content TEXT,
            reply_type INTEGER,
            file TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (thread_id) REFERENCES threads (thread_id)
        )
    ''')

    close_connection(conn)


create_tables()

conn = connect()
cursor = conn.cursor()

