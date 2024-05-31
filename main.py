from mysql.connector import connect
import telebot
from telebot import types
import time

bot = telebot.TeleBot('7043693417:AAGHltl-EYA5cu5XBGILe8npQNZh9-k06z0')

connection = connect(host='localhost',
                     user='root',
                     password='root',
                     database='diettelegranbot')

week_dict = {'Понеділок': 1, 'Вівторок': 2, 'Середа': 3, 'Четвер': 4, 'П\'ятниця': 5, 'Субота': 6, 'Неділя': 7}
ingestion_list = ['breakfast', 'lunch', 'dinner']
cursor = connection.cursor()


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.from_user.id, 'Привіт')
    day_choosing(message)


def day_choosing(message):
    monday_button = types.KeyboardButton('Понеділок')
    tuesday_button = types.KeyboardButton('Вівторок')
    wednesday_button = types.KeyboardButton('Середа')
    thursday_button = types.KeyboardButton('Четвер')
    friday_button = types.KeyboardButton('П\'ятниця')
    saturday_button = types.KeyboardButton('Субота')
    sunday_button = types.KeyboardButton('Неділя')
    markup = types.ReplyKeyboardMarkup()
    markup.add(monday_button,
               tuesday_button,
               wednesday_button,
               thursday_button,
               friday_button,
               saturday_button,
               sunday_button)
    bot.send_message(message.from_user.id, 'Оберіть день дієти:', reply_markup=markup)
    get_meals_list(message)


@bot.message_handler(content_types=['text'])
def get_meals_list(message, menu=''):
    global day_id
    if message.text in week_dict:
        day_id = week_dict[message.text]
        for index, ingestion in enumerate(ingestion_list, start=1):
            query = f"""
            SELECT f.food_name, f.food_composition, f.kkal, f.food_image 
            FROM food f 
            JOIN {ingestion} e ON f.food_id = e.food_id 
            JOIN day d ON e.day_id = d.day_id 
            WHERE d.day_id = %s
            """
            cursor.execute(query, (day_id,))
            eating = cursor.fetchall()
            menu += f"{index}. {eating[0][0]}.\n"
        bot.send_message(message.from_user.id, menu)
        confirmation(message)


def confirmation(message):
    yes_button = types.KeyboardButton('Так')
    no_button = types.KeyboardButton('Ні, повернутися назад')
    markup = types.ReplyKeyboardMarkup()
    markup.add(yes_button, no_button)
    bot.send_message(message.from_user.id, "Ви правильно обрали день?", reply_markup=markup)
    bot.register_next_step_handler(message, choosing_confirmation)


def choosing_confirmation(message):
    if message.text == 'Так':
        bot.send_message(message.from_user.id, 'Добре, тоді надаю вам список інградієнтів на кожну зі страв.')
        meals_ingredients(message)
    elif message.text == 'Ні, повернутися назад':
        day_choosing(message)


def meals_ingredients(message):
    back_button = types.KeyboardButton('Повернутися на початок')
    markup = types.ReplyKeyboardMarkup()
    markup.add(back_button)
    for ingestion in ingestion_list:
        query = f"""
        SELECT f.food_name, f.food_composition, f.kkal, f.food_image 
        FROM food f 
        JOIN {ingestion} e ON f.food_id = e.food_id 
        JOIN day d ON e.day_id = d.day_id 
        WHERE d.day_id = %s
        """
        cursor.execute(query, (day_id,))
        result = cursor.fetchall()
        bot.send_photo(message.from_user.id, f"https://ucarecdn.com/{result[0][3]}/",
                       f"<b>{result[0][0]}</b> \n\n{result[0][1]}\n\nКількість калорій - {result[0][2]} kkal",
                       parse_mode="html")
        time.sleep(1)
    bot.send_message(message.from_user.id, 'Ви можете повернутися на початок.', reply_markup=markup)
    bot.register_next_step_handler(message, back_to_start)


def back_to_start(message):
    if message.text == 'Повернутися на початок':
        day_choosing(message)
    else:
        bot.send_message(message.from_user.id, 'Не розумію вас!')


bot.polling(none_stop=True, interval=0)
