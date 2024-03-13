from telegram.ext import Updater, Application, CommandHandler, MessageHandler, ContextTypes, ConversationHandler, filters
from typing import final

from bot import startCommand, registerCommand, CreateGroupCommand, JoinGroupCommand, CreateThreadCommand, JoinThreadCommand, ReplyCommand, ListThreadsCommand, ListAllRepliesCommand
from bot import text, error, create_group, join_group, createthread, jointhread, reply, threadTitle
from bot import GET_CGROUP_NAME, GET_JGROUP_NAME, GET_CTHREAD_TOPIC, GET_JTHREAD_TOPIC, GET_REPLY, CREATE_THREAD


Token : final = "6395649052:AAE0OUQ0HPfx-iK0U-j5H_1WuzuoAzptGAo"
username : final = "@studygrpBot"

if __name__ == "__main__":

    print("Starting")

    app = Application.builder().token(Token).build()
    
    createG_handler = ConversationHandler(
        entry_points=[CommandHandler('createGroup', CreateGroupCommand)],
        states={
            GET_CGROUP_NAME: [MessageHandler(filters.TEXT, create_group)],
        },
        fallbacks=[],
    )

    joinG_handler = ConversationHandler(
        entry_points=[CommandHandler('joinGroup', JoinGroupCommand)],
        states={
            GET_JGROUP_NAME: [MessageHandler(filters.TEXT, join_group)],
        },
        fallbacks=[],
    )

    createT_handler = ConversationHandler(
        entry_points=[CommandHandler('createThread', CreateThreadCommand)],
        states={
            GET_CTHREAD_TOPIC: [MessageHandler(filters.TEXT, threadTitle)],
            CREATE_THREAD: [MessageHandler(filters.TEXT, createthread)],
        },
        fallbacks=[],
    )

    joinT_handler = ConversationHandler(
        entry_points=[CommandHandler('joinThread', JoinThreadCommand)],
        states={
            GET_JTHREAD_TOPIC: [MessageHandler(filters.TEXT, jointhread)],
        },
        fallbacks=[],
    )

    reply_handler = ConversationHandler(
        entry_points=[CommandHandler('reply', ReplyCommand)],
        states={
            GET_REPLY: [MessageHandler(filters.TEXT | filters._Photo, reply)],
        },
        fallbacks=[],
    )

    #commands
    app.add_handler(CommandHandler("start", startCommand))
    app.add_handler(CommandHandler("register", registerCommand))
    app.add_handler(createG_handler)
    app.add_handler(joinG_handler)
    app.add_handler(createT_handler)
    app.add_handler(CommandHandler("ListThreads", ListThreadsCommand))
    app.add_handler(CommandHandler("listReplies", ListAllRepliesCommand))
    app.add_handler(joinT_handler)
    app.add_handler(reply_handler)

    app.add_handler(MessageHandler(filters.TEXT, text))
    
    #app.add_error_handler(error)

    print("Polling")
    app.run_polling(5)
    