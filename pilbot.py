import telebot
from telebot import types
from PIL import Image, ImageFilter, ImageOps, ImageEnhance
import os

TOKEN = '7076403702:AAE3jhymRIbX5bPTKIfDrQ1feqX6m1fgYJI'
bot = telebot.TeleBot(TOKEN)

# === Словарь доступных фильтров ===
FILTERS = {
    'Резкость': 'sharpen',
    'Контур': 'contour',
    'Негатив': 'negative',
    'Гравировка': 'engrave'
}

# Папка для временных файлов
os.makedirs('temp', exist_ok=True)

# === Команда /start ===
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for name in FILTERS.keys():
        markup.add(types.KeyboardButton(name))
    bot.send_message(
        message.chat.id,
        "Привет! Я помогу преобразовать твоё фото.\nВыбери фильтр:",
        reply_markup=markup
    )

# === Обработка выбора фильтра ===
@bot.message_handler(func=lambda msg: msg.text in FILTERS.keys())
def choose_filter(message):
    filter_name = message.text
    bot.send_message(
        message.chat.id,
        f"Отлично! Пришли фото, я применю фильтр «{filter_name}»."
    )
    bot.register_next_step_handler(message, handle_photo, filter_name)

# === Получение и обработка фото ===
def handle_photo(message, filter_name):
    if not message.photo:
        bot.send_message(message.chat.id, "Это не фото 😅 Пришли изображение.")
        return

    # Получаем файл
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    input_path = os.path.join('temp', f"{message.chat.id}_input.jpg")
    output_path = os.path.join('temp', f"{message.chat.id}_output.jpg")

    with open(input_path, 'wb') as f:
        f.write(downloaded_file)

    img = Image.open(input_path).convert('RGB')

    filter_name = FILTERS[filter_name]

    if filter_name == 'sharpen':
        img = img.filter(ImageFilter.SHARPEN)

    if filter_name == 'contour':
        img = img.filter(ImageFilter.CONTOUR)

    if filter_name == 'negative':
        img = ImageEnhance.Contrast(img).enhance(-1)

    if filter_name == 'engrave':
        img = img.filter(ImageFilter.EMBOSS)

    img.save(output_path)

    with open(output_path, 'rb') as f:
        bot.send_photo(message.chat.id, f, caption=f'Вот твоё фото с фильтром {filter_name}')

    os.remove(input_path)
    os.remove(output_path)

    start(message)



bot.infinity_polling()












