import os

import telebot
from telebot import types

bot = telebot.TeleBot("7470242505:AAHHwuiHAhj8uPdPnZjaaRet6qZfB3805SM", parse_mode=None)
FILMS = "movies.txt"
IMAGES_DIR = 'images'


def add_film_to_file(filename, name, description, image_file=None):
    with open(filename, 'a', encoding='utf-8') as file:
        if image_file:
            file.write(f"{name}|{description}|{image_file}\n")
            print("фільм успішно додано")
        else:
            file.write(f"{name}|{description}\n")


def load_movies(filename):
    movies_dict = {}
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line:
                    parts = line.split('|')
                    if len(parts) == 3:
                        name, description, image_file = parts
                        movies_dict[name.strip()] = {
                            'description': description.strip(),
                            'image': image_file.strip()
                        }
                    elif len(parts) == 2:
                        # Якщо зображення відсутнє
                        name, description = parts
                        movies_dict[name.strip()] = {
                            'description': description.strip(),
                            'image': None
                        }
        return movies_dict
    except FileNotFoundError:
        print(f"Файл {filename} не знайдено.")
        return {}


movies = load_movies(FILMS)
user_states = {}


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "🎬 <b>Ласкаво просимо до бота-кіноафіші!</b>\n\n"
        "Ви можете виконати наступні команди:\n"
        "➡️ /movies - Показати список фільмів\n"
        "➕ /add_movie - Додати новий фільм\n"
        "ℹ️ Просто введіть назву фільму, щоб отримати його опис."
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode='HTML')


@bot.message_handler(commands=['movies'])
def list_movies(message):
    if movies:
        movie_list = '\n'.join([f"🎥 {name}" for name in movies.keys()])
        bot.send_message(
            message.chat.id,
            f"<b>Доступні фільми:</b>\n{movie_list}\n\n"
            "Введіть назву фільму, щоб отримати опис.",
            parse_mode='HTML'
        )
    else:
        bot.send_message(message.chat.id, "Наразі немає доступних фільмів.")


@bot.message_handler(commands=['add_movie'])
def add_movie(message):
    bot.send_message(message.chat.id, "Введіть назву фільму, який ви хочете додати:")
    bot.register_next_step_handler(message, add_movie_step2)


def add_movie_step2(message):
    movie_name = message.text.strip()

    if not movie_name:
        bot.send_message(message.chat.id, "⚠️ Назва фільму не може бути порожньою. Спробуйте ще раз.")
        return
    if movie_name in movies:
        bot.send_message(message.chat.id, "❗️ Такий фільм вже є у списку.")
        return
    else:
        user_states[message.chat.id] = {'movie_name': movie_name}
        bot.send_message(message.chat.id, "✏️ Введіть опис фільму:")
        bot.register_next_step_handler(message, add_movie_step3)


def add_movie_step3(message):
    movie_description = message.text.strip()
    if not movie_description:
        bot.send_message(message.chat.id, "⚠️ Опис фільму не може бути порожнім. Спробуйте ще раз.")
        return
    user_states[message.chat.id]['movie_description'] = movie_description
    bot.send_message(message.chat.id, "📷 Відправте зображення фільму або введіть 'пропустити':")
    bot.register_next_step_handler(message, add_movie_step4)


def add_movie_step4(message):
    movie_name = user_states[message.chat.id]['movie_name']
    movie_description = user_states[message.chat.id]['movie_description']

    if message.content_type == 'photo':

        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        image_filename = f"{movie_name.replace(' ', '_')}.jpg"
        image_path = os.path.join(IMAGES_DIR, image_filename)
        with open(image_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        image_file = image_filename
    elif message.text.lower() == 'пропустити':
        image_file = None
    else:
        bot.send_message(message.chat.id, "⚠️ Будь ласка, відправте зображення або введіть 'пропустити'.")
        return

    add_film_to_file(FILMS, movie_name, movie_description, image_file)
    movies[movie_name] = {
        'description': movie_description,
        'image': image_file
    }
    bot.send_message(message.chat.id, f"✅ Фільм '<b>{movie_name}</b>' було успішно додано до списку!",
                     parse_mode='HTML')
    del user_states[message.chat.id]


@bot.message_handler(func=lambda message: True)
def send_movie_info(message):
    movie_name = message.text.strip()
    if movie_name in movies.keys():
        movie = movies[movie_name]
        description = movie['description']
        image_file = movie['image']
        if image_file:
            image_path = os.path.join(IMAGES_DIR, image_file)
            if os.path.exists(image_path):
                with open(image_path, 'rb') as photo:
                    bot.send_photo(
                        message.chat.id,
                        photo,
                        caption=f"🎥 <b>{movie_name}</b>\n\n{description}",
                        parse_mode='HTML'
                    )
            else:
                bot.send_message(
                    message.chat.id,
                    f"🎥 <b>{movie_name}</b>\n\n{description}",
                    parse_mode='HTML'
                )
        else:
            bot.send_message(
                message.chat.id,
                f"🎥 <b>{movie_name}</b>\n\n{description}",
                parse_mode='HTML'
            )
    else:
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        btn1 = types.KeyboardButton('/movies')
        btn2 = types.KeyboardButton('/add_movie')
        markup.add(btn1, btn2)
        bot.send_message(
            message.chat.id,
            "❓ Я не знайшов інформації про цей фільм.\n"
            "Ви можете переглянути доступні фільми, додати новий або видалити фільм.",
            reply_markup=markup
        )


bot.infinity_polling()