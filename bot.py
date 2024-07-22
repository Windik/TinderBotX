from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler
from gpt import *
from util import *

with open("./resources/tokens.txt", "r") as f:
    lines = f.readlines()

    BOT_TOKEN = lines[0].strip("\n")
    CHATGPT_TOKEN = lines[1].strip("\n")

command_start_message = load_message("main")
command_gpt_message = load_message("gpt")

dialog = Dialog()
dialog.mode = None

gpt_mode = "gpt"
main_mode = "main"

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


async def gpt_dialog(update, context):
    user_message = update.message.text

    answer = await chatgpt.send_question(gpt_prompt, user_message)
    await send_text(update, context, answer)


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


app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", command_start))
app.add_handler(CommandHandler("gpt", command_gpt))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))
app.add_handler(CallbackQueryHandler(process_button))
app.run_polling()
