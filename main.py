import os

from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, BotCommand

from gpt import ChatSession
from keyboards import level_keyboard, topic_keyboard, option_keyboard
from utils import check_email, load_paid_emails

bot = Bot(token=os.environ.get(TOKEN))
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

chat_session = ChatSession(api_key=os.environ.get(OPENAI_API_KEY))
# States
LEVEL, TOPIC, MESSAGE, OPTION = range(4)

# User states dictionary
user_states = {}


def get_user_state(user_id, key):
    return user_states.get(user_id, {}).get(key)


def update_user_state(user_id, key, value):
    if user_id not in user_states:
        user_states[user_id] = {}
    user_states[user_id][key] = value


def clear_user_state(user_id):
    if user_id in user_states:
        user_states.pop(user_id, None)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    clear_user_state(message.from_user.id)
    await message.answer(f'Hello {message.from_user.username}!'
                         f"🌟 Welcome to the FlyEng Speaking Bot! 🌟\n\n"
                         f"🎉 I'm here to be your friendly language buddy, ready to chat about anything and "
                         f"everything under the sun! "
                         f"Whether you're a curious learner or just looking to polish your English skills, "
                         f"we're going to have a great time together! 📚✨\n\n "
                         f"🗣️ Ask me about daily topics, play word games, or dive into deep discussions. There's no "
                         f"limit to what we can explore. "
                         f"Let's make learning fun and engaging! 🚀\n\n"
                         f"👋 So, what's on your mind today? Let's start chatting and improve your English one "
                         f"conversation at a time! 🎈")
    await message.answer("Enter your email.")

    dp.register_message_handler(process_email_step, state=None)


async def process_email_step(message: types.Message):
    paid_emails = load_paid_emails()
    user_email = message.text
    if check_email(user_email):
        if user_email in paid_emails:
            await bot.send_message(message.chat.id, "You are registered. Welcome!")
            update_user_state(message.from_user.id, 'state', OPTION)
            await message.answer("Choose what you want:", reply_markup=option_keyboard)
        else:
            await bot.send_message(message.chat.id, "You are not registered")
            msg = await bot.send_message(message.chat.id, "Некорректный email. Введите еще раз:")
            dp.register_message_handler(process_email_step, state=None)
    else:
        msg = await bot.send_message(message.chat.id, "Некорректный email. Введите еще раз:")
        dp.register_message_handler(process_email_step, state=None)


@dp.message_handler(lambda message: get_user_state(message.from_user.id, 'state') == OPTION)
async def choose_option(message: types.Message):
    update_user_state(message.from_user.id, 'option', message.text)
    if message.text == 'Listening':
        update_user_state(message.from_user.id, 'state', LEVEL)
        await message.answer("Choose your level:", reply_markup=level_keyboard)
    if message.text == 'Assessment of the essay':
        update_user_state(message.from_user.id, 'state', LEVEL)
        await message.answer("Choose your level:", reply_markup=level_keyboard)


@dp.message_handler(commands=['help'])
async def start(message: types.Message):
    await message.answer("help text")


@dp.message_handler(lambda message: get_user_state(message.from_user.id, 'state') == LEVEL)
async def set_level(message: types.Message):
    update_user_state(message.from_user.id, 'level', message.text)
    chosen_option = get_user_state(message.from_user.id, 'option')
    if chosen_option == 'Listening':
        update_user_state(message.from_user.id, 'state', TOPIC)
        await message.answer("Choose a topic for conversation:", reply_markup=topic_keyboard)
    elif chosen_option == 'Assessment of the essay':
        update_user_state(message.from_user.id, 'state', MESSAGE)
        await message.answer("Please send me your essay for assessment.", reply_markup=ReplyKeyboardRemove())


@dp.message_handler(lambda message: get_user_state(message.from_user.id, 'state') == TOPIC)
async def set_topic(message: types.Message):
    update_user_state(message.from_user.id, 'topic', message.text)
    update_user_state(message.from_user.id, 'state', MESSAGE)
    await message.answer("What is your question for today?", reply_markup=ReplyKeyboardRemove())


@dp.message_handler(
    lambda message: get_user_state(message.from_user.id, 'state') == MESSAGE and get_user_state(message.from_user.id,
                                                                                                'option') == 'Assessment of the essay')
async def handle_essay_assessment(message: types.Message):
    essay_text = message.text
    prompt = chat_session.generate_prompt_essay(essay_text)
    response_text = chat_session.get_response_from_gpt(prompt)
    await message.answer(response_text)


@dp.message_handler(
    lambda message: get_user_state(message.from_user.id, 'state') == MESSAGE and get_user_state(message.from_user.id,
                                                                                                'option') == 'Listening')
async def send_gpt_answer(message: types.Message):
    level = get_user_state(message.from_user.id, 'level')
    topic = get_user_state(message.from_user.id, 'topic')
    user_message = message.text

    chat_session.update_dialogue(user_message)
    prompt = chat_session.generate_prompt(topic, level, user_message)
    response_text = chat_session.get_response_from_gpt(prompt)
    from gtts import gTTS
    try:
        tts = gTTS(text=response_text, lang='en', slow=False, tld='com.au')
        audio_file = f'{message.from_user.id}.ogg'
        tts.save(audio_file)
        chat_session.update_dialogue(user_message, response_text)
        await message.answer_voice(open(f'{message.from_user.id}.ogg', 'rb'))
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if os.path.exists(audio_file):
            os.remove(audio_file)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
