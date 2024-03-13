from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from io import BytesIO

from database import formatted_date, connect, close_connection, cursor, conn
from sgb import create_study_group, join_study_group, register_user, create_thread, join_thread, post_reply


#States
GET_CGROUP_NAME, GET_JGROUP_NAME, GET_CTHREAD_TOPIC, GET_JTHREAD_TOPIC, CREATE_THREAD, GET_REPLY, GET_FILE = range(7)
Current_thread = -1


async def registerCommand(update : Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.from_user.username
    userId = update.message.from_user.id
    chat_id = update.message.chat_id
    date = formatted_date
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (userId,))
    is_regestered = cursor.fetchall()

    if not is_regestered:
        register_user(userId, username, chat_id, date)
        await update.message.reply_text(f"Welcome, {username}! You are now registered.")
    else:
        await update.message.reply_text("You are already registered.")


async def startCommand(update : Update, context : ContextTypes.DEFAULT_TYPE):  
    await update.message.reply_text("Hello \nChoose Command from commands below:\n1. /register \n2. /createGroup \n3. /joinGroup \n4. /createThread \n5. /joinThread\n6. /listThreads \n7. /listReplies")


async def CreateGroupCommand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Great! Please enter the name of the group.")
    return GET_CGROUP_NAME

async def create_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    group_name = update.message.text
    cursor.execute("SELECT group_id FROM study_groups WHERE group_name = ?", (group_name,))
    group_exists = cursor.fetchone()

    if not group_exists:
    # creates the group
        create_study_group(group_name, user_id)
        await update.message.reply_text(f"Group '{group_name}' created successfully!")
    else: 
        await update.message.reply_text("This group already Exists! Please choose another name")

    return ConversationHandler.END
    

async def JoinGroupCommand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Great! Please enter the name of the group.")
    return GET_JGROUP_NAME

async def join_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    group_name = update.message.text
    cursor.execute("SELECT group_id FROM study_groups WHERE group_name = ?", (group_name,))
    group_exists = cursor.fetchone()

    if group_exists:
        conn = connect()
    
        group_id = group_exists[0]
        cursor.execute("SELECT user_id FROM group_members WHERE user_id = ? AND group_id = ?", (user_id, group_id,)) 
        existing_member = cursor.fetchone()
        close_connection(conn)

        if not existing_member:
        # Add the user to the group_members table
            join_study_group(group_id, user_id)
            await update.message.reply_text(f"you joined '{group_name}' successfully!")
        else:
            await update.message.reply_text(f"you are already a member of '{group_name}'.")
    else :
         await update.message.reply_text(f"Group {group_name} does not exist")
    return ConversationHandler.END


async def CreateThreadCommand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Enter Discussion Topic")
    return GET_CTHREAD_TOPIC

async def threadTitle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    title = update.message.text
    # Store the title in the context dictionary
    context.user_data['title'] = title
    await update.message.reply_text(f"Type you question")
    return CREATE_THREAD

async def createthread(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    # Retrieve the title from the context dictionary
    title = context.user_data.get('title', None)
    body = update.message.text

    create_thread(user_id, title, body)
    await update.message.reply_text(f"'{title}' created successfully!")

    return ConversationHandler.END
    

async def ListThreadsCommand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Execute a SELECT query to fetch all thread names
    cursor.execute('SELECT title, content FROM threads')
        
    # Fetch all the results
    thread_names = cursor.fetchall()

    # Print the thread names
    if thread_names:
        for thread_name in thread_names:
            await update.message.reply_text(f"'{thread_name[0]}' \n {thread_name[1]}")

    else:
        await update.message.reply_text("No threads found.")


async def JoinThreadCommand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Great! Please enter the topic of the thread.")
    return GET_JTHREAD_TOPIC

async def jointhread(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global Current_thread
    user_id = update.message.from_user.id
    title = update.message.text
    cursor.execute("SELECT thread_id FROM threads WHERE title = ?", (title,))
    thread_exists = cursor.fetchone()

    if thread_exists:
        conn = connect()
    
        thread_id = thread_exists[0]
        Current_thread = thread_id
        cursor.execute("SELECT user_id FROM thread_members WHERE user_id = ? AND thread_id = ?", (user_id, thread_id,)) 
        existing_member = cursor.fetchone()
        close_connection(conn)

        if not existing_member:
        # Add the user to the group_members table
            join_thread(thread_id, user_id)
            await update.message.reply_text(f"you joined '{title}' successfully!")
            # getting title and content of the Thread
            cursor.execute("SELECT content FROM threads WHERE thread_id = ?", (thread_id,)) 
            content = cursor.fetchone()
            content = content[0]
            await update.message.reply_text(f"QUESTION:  '{content}'")
            
            cursor.execute("SELECT user_id, content, reply_type FROM replies WHERE thread_id = ?", (thread_id,)) 
            replieslist = cursor.fetchall()
            for reply in replieslist:
                users_ids, message, rtype = reply
                cursor.execute("SELECT username FROM users WHERE user_id = ?", (users_ids,)) 
                user_name = cursor.fetchall()
                user_name = user_name[0][0]
                if rtype == 2:
                    await update.message.reply_text(f"{users_ids} {user_name}: {message} ")
                    #context.bot.send_document(chat_id=update.effective_chat.id, document=file_id)
                    
                elif rtype == 3:
                    await update.message.reply_text(f"{users_ids} {user_name}: {message} ")
                    #context.bot.send_photo(chat_id=update.effective_chat.id, photo=file_id)

                elif rtype == 1:
                    await update.message.reply_text(f"{users_ids} {user_name}: {message} ")
                else:
                    await update.message.reply_text(f"{users_ids} {user_name}'s reply is not available ")
        else:
            await update.message.reply_text(f"you are already a member of '{title}'.")
    else :
         await update.message.reply_text(f"Thread {title} does not exist")
    return ConversationHandler.END


async def ListAllRepliesCommand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor.execute("SELECT user_id, content, reply_type FROM replies WHERE thread_id = ?", (Current_thread,)) 
    replieslist = cursor.fetchall()
    if replieslist:
        for reply in replieslist:
            users_ids, message, rtype = reply
            cursor.execute("SELECT username FROM users WHERE user_id = ?", (users_ids,)) 
            user_name = cursor.fetchall()
            user_name = user_name[0][0]
            if rtype == 2:
                await update.message.reply_text(f"{users_ids} {user_name}: {message} ")
                #context.bot.send_document(chat_id=update.effective_chat.id, document=file_id)
                        
            elif rtype == 3:
                await update.message.reply_text(f"{users_ids} {user_name}: {message} ")
                #context.bot.send_photo(chat_id=update.effective_chat.id, photo=file_id)

            elif rtype == 1:
                await update.message.reply_text(f"{users_ids} {user_name}: {message} ")
            else:
                await update.message.reply_text(f"{users_ids} {user_name}'s reply is not available ")
    else:
        await update.message.reply_text("No replies are available ")


async def ReplyCommand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if Current_thread != -1:
        await update.message.reply_text("Type Your Reply")
        return GET_REPLY
    await update.message.reply_text("Join a Thread First")

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    if not update.message.text:
        #if reply is a document or an image will add feature latter
        None  
    elif update.message.text:
        body = update.message.text
        post_reply(user_id, Current_thread, body, 1, None)

    await update.message.reply_text("Reply Posted Succesfully")
    return ConversationHandler.END


async def text(update: Update, context: ContextTypes.DEFAULT_TYPE)  :
    userText : str = update.message.text
    await update.message.reply_text(f'you entered {userText}')

async def error(update:Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('An error occured.')      



async def save_file(update:Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document or update.message.photo[-1].get_file()

    with BytesIO(file.download_as_bytearray()) as file_bytearray:
        file_type = file.file_name.split('.')[-1]
        cursor.execute('INSERT INTO files (file, file_type) VALUES (?, ?)', (file_bytearray.read(), file_type))
        conn.commit()