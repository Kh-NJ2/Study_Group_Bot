from database import connect, execute_query, close_connection, formatted_date

date = formatted_date


def register_user(user_id, username, chat_id, registration_date):
    conn = connect()
    execute_query(conn, "INSERT INTO users (user_id, username, chat_id, registration_date) VALUES (?, ?, ?, ?)",
                  (user_id, username, chat_id, registration_date))
    close_connection(conn)


def create_study_group(group_name, admin_id):
    conn = connect()
    execute_query(conn, "INSERT INTO study_groups (group_name, admin_id, creation_date) VALUES (?, ?, ?)",
        (group_name, admin_id, date))
    close_connection(conn)


def join_study_group(group_id, user_id):
    conn = connect()
    execute_query(conn, "INSERT INTO group_members (user_id, group_id) VALUES (?, ?)", (user_id, group_id))
    close_connection(conn)


def create_study_session(group_id, topic):
    conn = connect()
    execute_query(conn, "INSERT INTO study_sessions (group_id INTEGER, session_date TEXT, topic TEXT) VALUES (?, ?, ?)",
        (group_id, date, topic))
    close_connection(conn)


def join_study_session(topic):
    None


def create_thread(user_id, title, body):
    conn = connect()
    execute_query(conn, "INSERT INTO threads (user_id, title, content) VALUES (?, ?, ?)",
        (user_id, title, body))
    close_connection(conn)


def join_thread(user_id, thread_id):
    conn = connect()
    execute_query(conn, "INSERT INTO thread_members (user_id, thread_id) VALUES (?, ?)",
        (user_id, thread_id))
    close_connection(conn)
 

def post_reply(user_id, thread_id, body, rtype, f):
    conn = connect()
    execute_query(conn, "INSERT INTO replies (user_id, thread_id, content, reply_type, file) VALUES (?, ?, ?, ?, ?)",
        (user_id, thread_id, body, rtype, f))
    close_connection(conn)