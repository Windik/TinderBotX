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
dialog.user_profile_question_count = 1
dialog.user_profile_data = {}
dialog.opener_question_count = 1
dialog.opener_data = {}

gpt_mode = "gpt"
main_mode = "main"
date_mode = "date"
message_mode = "message"
profile_mode = "profile"
opener_mode = "opener"

command_start_message = load_message(main_mode)
command_gpt_message = load_message(gpt_mode)
command_date_message = load_message(date_mode)
command_message_message = load_message(message_mode)

chatgpt = ChatGptService(token=CHATGPT_TOKEN)
gpt_prompt = load_prompt("gpt")

menu_commands = {
    "start": "главное меню бота",
    "profile": "генерация Tinder-профиля 😎",
    "opener": "сообщение для знакомства 🥰",
    "message": "переписка от вашего имени 😈",
    "date": "переписка со звездами 🔥",
    "gpt": "задать вопрос чату GPT 🧠",
}

profile_questions = {
    1: "Сколько Вам лет?",
    2: "Кем Вы работаете?",
    3: "У Вас есть хобби?",
    4: "Что Вам НЕнравится в людях?",
    5: "Цели знакомства?",
}

profile_answers = {
    1: "age",
    2: "occupation",
    3: "hobby",
    4: "annoys",
    5: "goals",
}

opener_questions = {
    1: "Имя девушки?",
    2: "Сколько ей лет?",
    3: "Оцените ее внешность от 1 до 10 баллов.",
    4: "Кем она работает?",
    5: "Цель знакомства?",
}

opener_answers = {
    1: "name",
    2: "age",
    3: "handsome",
    4: "occupation",
    5: "goals",
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


async def command_profile(update, context):
    profile_image = profile_mode
    dialog.mode = profile_mode

    message = load_message(profile_mode)

    await send_photo(update, context, profile_image)
    await send_text(update, context, message)

    dialog.user_profile_data.clear()
    dialog.user_profile_question_count = 1

    await send_text(update, context, profile_questions[dialog.user_profile_question_count])


async def command_opener(update, context):
    opener_image = opener_mode
    dialog.mode = opener_mode

    message = load_message(opener_mode)

    await send_photo(update, context, opener_image)
    await send_text(update, context, message)

    dialog.opener_data.clear()
    dialog.opener_question_count = 1

    await send_text(update, context, opener_questions[dialog.opener_question_count])


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


async def profile_dialog(update, context):
    text = update.message.text

    current_answer_key = opener_answers[dialog.user_profile_question_count]
    dialog.user_profile_data[current_answer_key] = text

    dialog.user_profile_question_count += 1

    if dialog.user_profile_question_count <= 5:
        await send_text(update, context, profile_questions[dialog.user_profile_question_count])
    else:
        prompt = load_prompt(profile_mode)
        user_info = dialog_user_info_to_str(dialog.user_profile_data)
        pre_message_text = "Подготавливаю описание профиля..."

        pre_message = await send_text(update, context, pre_message_text)

        answer = await chatgpt.send_question(prompt, user_info)

        await pre_message.edit_text(answer)


async def opener_dialog(update, context):
    text = update.message.text

    current_answer_key = opener_answers[dialog.opener_question_count]
    dialog.opener_data[current_answer_key] = text

    dialog.opener_question_count += 1

    if dialog.opener_question_count <= 5:
        await send_text(update, context, opener_questions[dialog.opener_question_count])
    else:
        prompt = load_prompt(opener_mode)
        opener_info = dialog_user_info_to_str(dialog.opener_data)
        pre_message_text = "Подготавливаю сообщение для знакомства..."

        pre_message = await send_text(update, context, pre_message_text)

        answer = await chatgpt.send_question(prompt, opener_info)

        await pre_message.edit_text(answer)


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
    elif dialog.mode == profile_mode:
        await profile_dialog(update, context)
    elif dialog.mode == opener_mode:
        await opener_dialog(update, context)
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
app.add_handler(CommandHandler(profile_mode, command_profile))
app.add_handler(CommandHandler(opener_mode, command_opener))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))

app.add_handler(CallbackQueryHandler(date_button, pattern="^date_.*"))
app.add_handler(CallbackQueryHandler(message_button, pattern="^message_.*"))
app.add_handler(CallbackQueryHandler(process_button))
app.run_polling()
