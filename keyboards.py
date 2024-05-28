from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

level_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton('Beginner'),
    KeyboardButton('Intermediate'),
    KeyboardButton('Advanced')
)

topic_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton('Technology'),
    KeyboardButton('Science'),
    KeyboardButton('History'),
    KeyboardButton('Free topic')
)

option_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton('Listening'),
    KeyboardButton('Assessment of the essay'),
)
