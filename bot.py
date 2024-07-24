from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler
from gpt import *
from util import *

with open("./resources/tokens.txt", "r") as f:
    lines = f.readlines()

    BOT_TOKEN = lines[0].strip("\n")
    CHATGPT_TOKEN = lines[1].strip("\n")

dialog = Dialog()
dialog.mode = None
dialog.list = []

gpt_mode = "gpt"
main_mode = "main"
date_mode = "date"
message_mode = "message"

command_start_message = load_message(main_mode)
command_gpt_message = load_message(gpt_mode)
command_date_message = load_message(date_mode)
command_message_message = load_message(message_mode)

chatgpt = ChatGptService(token=CHATGPT_TOKEN)
gpt_prompt = load_prompt("gpt")

menu_commands = {
    "start": "главное меню бота",
    "profile": "генерация Tinder-профля 😎",
    "opener": "сообщение для знакомства 🥰",
    "message": "переписка от вашего имени 😈",
    "date": "переписка со звездами 🔥",
    "gpt": "задать вопрос чату GPT 🧠",
}


async def command_start(update, context):
    main_image = "main"
    dialog.mode = main_mode

    await show_main_menu(update, context, menu_commands)

    await send_photo(update, context, main_image)
    await send_text(update, context, command_start_message)


async def command_gpt(update, context):
    gpt_image = "gpt"
    dialog.mode = gpt_mode

    await send_photo(update, context, gpt_image)
    await send_text(update, context, command_gpt_message)


async def command_date(update, context):
    date_image = date_mode
    dialog.mode = date_mode

    message = load_message(date_mode)

    date_buttons = {
        "date_grande": "Ариана Гранде",
        "date_robbie": "Марго Робби",
        "date_zendaya": "Зендея",
        "date_gosling": "Райан Гослинг",
        "date_hardy": "Том харди",
    }

    await send_photo(update, context, date_image)
    await send_text_buttons(update, context, message, date_buttons)


async def command_message(update, context):
    message_image = message_mode
    dialog.mode = message_mode

    message = load_message(message_mode)

    message_buttons = {
        "message_next": "Следующее сообщение",
        "message_date": "Пригласить на свидание",
    }

    await send_photo(update, context, message_image)
    await send_text_buttons(update, context, message, message_buttons)

    dialog.list.clear()


async def gpt_dialog(update, context):
    user_message = update.message.text

    answer = await chatgpt.send_question(gpt_prompt, user_message)
    await send_text(update, context, answer)


async def date_dialog(update, context):
    text = update.message.text
    pre_message_text = "Собеседник набирает текст..."

    pre_message = await send_text(update, context, pre_message_text)

    answer = await chatgpt.add_message(text)
    await pre_message.edit_text(answer)


async def message_dialog(update, context):
    text = update.message.text

    dialog.list.append(text)


async def hello(update, context):
    message = "Hello"
    image = "avatar_main"
    buttons_message = "Запустить процесс?"
    buttons = {
        "start": "Запустить",
        "stop": "Остановить",
    }

    if dialog.mode == gpt_mode:
        await gpt_dialog(update, context)
    elif dialog.mode == date_mode:
        await date_dialog(update, context)
    elif dialog.mode == message_mode:
        await message_dialog(update, context)
    elif dialog.mode == main_mode:
        await send_text(update, context, message)
        await send_photo(update, context, image)
        await send_text_buttons(update, context, buttons_message, buttons)


async def process_button(update, context):
    query = update.callback_query.data

    start_button_text = "start"
    stop_button_text = "stop"

    start_button_message = "Процесс запущен!"
    stop_button_message = "Процесс остановлен!"
    unknown_command = "Неизвасная команда！"

    if query == start_button_text:
        await send_text(update, context, start_button_message)
    elif query == stop_button_text:
        await send_text(update, context, stop_button_message)
    else:
        await send_text(update, context, unknown_command)


async def date_button(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()

    girls = ["date_grande", "date_robbie", "date_zendaya"]
    girls_select_message = "Отличный выбор! Пригласите девушку на свидание за 5 сообщений"
    boys_select_message = "Отличный выбор! Пригласите парня на свидание за 5 сообщений"
    prompt = load_prompt(query)

    await send_photo(update, context, query)

    if query in girls:
        await send_text(update, context, girls_select_message)
    else:
        await send_text(update, context, boys_select_message)

    chatgpt.set_prompt(prompt)


async def message_button(update, context):
    pre_message_text = "ChatGPT думает над вариантом ответа..."
    query = update.callback_query.data
    await update.callback_query.answer()

    prompt = load_prompt(query)
    user_chat_history = "\n\n".join(dialog.list)

    pre_message = await send_text(update, context, pre_message_text)
    answer = await chatgpt.send_question(prompt, user_chat_history)

    await pre_message.edit_text(answer)


app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", command_start))
app.add_handler(CommandHandler(gpt_mode, command_gpt))
app.add_handler(CommandHandler(date_mode, command_date))
app.add_handler(CommandHandler(message_mode, command_message))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))

app.add_handler(CallbackQueryHandler(date_button, pattern="^date_.*"))
app.add_handler(CallbackQueryHandler(message_button, pattern="^message_.*"))
app.add_handler(CallbackQueryHandler(process_button))
app.run_polling()
