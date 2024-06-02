'''
TOKEN is stored in a separate file "TOKEN.py"
'''

import telebot
from PIL import Image, ImageOps
import io
from telebot import types
import random
from TOKEN import TOKEN

# import os
#
# TOKEN = os.getenv('TOKEN')

# TOKEN = 'your token'


bot = telebot.TeleBot(TOKEN)

user_states = {}  # тут будем хранить информацию о действиях пользователя

# набор символов из которых составляем изображение
ASCII_CHARS_default = '@%#*+=-:. '


def resize_image(image, new_width=100):
    width, height = image.size
    ratio = height / width
    new_height = int(new_width * ratio)
    return image.resize((new_width, new_height))


def grayify(image):
    return image.convert("L")


def image_to_ascii(image_stream, new_width=40, users_character=None):
    # Переводим в оттенки серого
    image = Image.open(image_stream).convert('L')  # конвертим изображение в 8-битовые пиксели ч/б

    # меняем размер сохраняя отношение сторон
    width, height = image.size
    aspect_ratio = height / float(width)
    new_height = int(
        aspect_ratio * new_width * 0.48)  # 0,55 так как буквы выше чем шире !!! Здесь тоже не понятно, почему не 0,5, или не 0,6
    img_resized = image.resize((new_width, new_height))

    img_str = pixels_to_ascii(img_resized, users_character=users_character)
    img_width = img_resized.width

    max_characters = 4000 - (new_width + 1)  # почему 4000?
    max_rows = max_characters // (new_width + 1)

    ascii_art = ""
    for i in range(0, min(max_rows * img_width, len(img_str)), img_width):
        ascii_art += img_str[i:i + img_width] + "\n"

    return ascii_art


def pixels_to_ascii(image, users_character=None):
    global ASCII_CHARS_default
    if users_character is not None:
        ASCII_CHARS_default = users_character

    pixels = image.getdata()
    characters = ""
    for pixel in pixels:
        characters += ASCII_CHARS_default[
            pixel * len(ASCII_CHARS_default) // 256]  # что здесь за магия?)))) почему 256?
    return characters


# Огрубляем изображение
def pixelate_image(image, pixel_size):
    image = image.resize(
        (image.size[0] // pixel_size, image.size[1] // pixel_size),
        Image.NEAREST
    )
    image = image.resize(
        (image.size[0] * pixel_size, image.size[1] * pixel_size),
        Image.NEAREST
    )
    return image


@bot.message_handler(commands=['start', 'help'])  # 1. /start /help и прочие параметры меню
def send_welcome(message):
    bot.reply_to(message, "Send me an image, and I'll provide options for you!\n"
                          "Also I can make you laugh, just send me - 'JOKE'.\n"
                          "If you are upset, I can give you a compliment. Send me 'COMPLIMENT' to get it.\n"
                          "...Why don't we flip a coin? Just send - 'FLIP")


@bot.message_handler(content_types=['photo'])  # 2. Принимает фото от пользователя
def handle_photo(message):
    bot.reply_to(message, "I got your photo! Please choose what you'd like to do with it.",  # говорит получил
                 reply_markup=get_options_keyboard())  # и создает выполняет команду по созданию кнопок
    user_states[message.chat.id] = {'photo': message.photo[-1].file_id}  # ЗДЕСЬ ПРОИСХОДИТ ЧТО-ТО НЕ ПОНЯТНОЕ


@bot.message_handler(content_types='text')
def ascii_users_choise(message):
    users_character = message.text
    if not user_states:
        user_states[message.chat.id] = {'users_character': users_character}
    else:
        user_states[message.chat.id]['users_character'] = users_character

    if users_character.lower() == 'default':
        if 'photo' not in dict.keys(user_states[message.chat.id]):
            bot.send_message(message.chat.id, 'At first send me a pic/photo for processing')
        else:
            bot.send_message(message.chat.id, "Converting your image to ASCII art...")
            ascii_and_send_standart(message)
    elif users_character.lower() == 'new symbols':
        if 'photo' not in dict.keys(user_states[message.chat.id]):
            bot.send_message(message.chat.id, 'At first send me a pic/photo for processing')
        else:
            bot.send_message(message.chat.id, 'Please send your personal character set')
            bot.register_next_step_handler(message, ascii_users_character_set)
    elif users_character.lower() == 'joke':
        JOKES = ['Плохо написанное  ПО одного  — кропотливая  работа другого',
                 'Если девушка попросила  вас починить компьютер не нужно  радоваться, возможно там и нечего чинить',
                 'Код писать надо так , словно человек, который будет его поддерживать  — психопат, который знает, где ты живешь',
                 'Не получилось написать хорошую программу с первого раза , тогда назовите ее “первой версией”',
                 'Есть два основных языка программирования: одним – все недовольны, а  другими никто не пользовался',
                 'Если в очередном обновлении  Java будет создана  функция очищения  программного мусора, основная часть приложений Java будут удалять себя сразу после установки',
                 'Нету плохого когда, есть тот, который неправильно поняли',
                 'Прежде чем удалить файл, посмотри — твой ли он. Надежные компоненты те, которых нету',
                 'Хотел задать вопрос – It это ориентация или все же диагноз?']
        random_joke = random.choice(JOKES)
        bot.send_message(message.chat.id, text=random_joke)
    elif users_character.lower() == 'compliment':
        COMPLIMENTS = ['Какие у вашей собаки губки, глаза и шерсть красивые. Прямо как у вас!',
                       'У вас ноги как бильярдный кий',
                       'Ты у меня быстрее, чем вода в унитазе!',
                       'У тебя очень красивые губы. Где тебе их сделали?',
                       'У вас череп такой правильной формы. Вы не хотите побриться налысо?',
                       'А может, вы не девушка? Память у вас не девичья…',
                       'Твоя харизма может рассмешить даже серьезного клоуна',
                       'С тобой каждый день как смешной комедийный шоу',
                       'Ты всегда находишь выход из любой ситуации! Это не потому что вход в неё ты сам показал?',
                       'Какая ты теперь умница и красотка, со мной ты стала нормальной, не то что раньше']
        random_compliment = random.choice(COMPLIMENTS)
        bot.send_message(message.chat.id, text=random_compliment)
    elif users_character.lower() == 'flip':
        results_of_flip = ["Heads", "Tails"]
        random_side_coin = random.choice(results_of_flip)
        bot.send_message(message.chat.id, text=random_side_coin)
    else:
        bot.send_message(message.chat.id,
                         "Sorry, I cannot handle such kinda message. ENTER /help to see what functions i have")


def ascii_users_character_set(message):
    users_character = message.text
    user_states[message.chat.id]['new_character_set'] = users_character
    bot.send_message(message.chat.id, "Converting your image to ASCII art...")
    ascii_and_send_standart(message, users_character=users_character)


def get_options_keyboard():
    """
    Функция создаёт кнопки вариантов обработки фотографии, высланной пользователем
    :return: Меню с кнопками
    """
    keyboard = types.InlineKeyboardMarkup()  # здесь создаем меню для размещения кнопок, по умолчанию - три в ряд.
    pixelate_btn = types.InlineKeyboardButton("Pixelate", callback_data="pixelate")  # здесь создаём кнопку
    ascii_btn = types.InlineKeyboardButton("ASCII Art", callback_data="ascii")  # здесь создаём еще одну кнопку
    color_inversion_btn = types.InlineKeyboardButton("Inversion of Color", callback_data="inversion")
    mirror_vert_btn = types.InlineKeyboardButton("Mirror vertically", callback_data="mirror_vert")
    mirror_horiz_btn = types.InlineKeyboardButton("Mirror horizontally", callback_data="mirror_horiz")
    build_heat_map_btn = types.InlineKeyboardButton("Build heat map", callback_data="heat_map")
    resize_btn = types.InlineKeyboardButton("Resize to sticker", callback_data="resize")
    keyboard.add(pixelate_btn, ascii_btn, color_inversion_btn, mirror_vert_btn, mirror_horiz_btn, build_heat_map_btn, resize_btn)
    return keyboard


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    """
    Принимает строку, которая написана на кнопке (обработки фото)
    :param call:
    :return:
    """
    call_data_list = ["inversion", "mirror_vert", "mirror_horiz", "heat_map", "resize"]
    if call.data == "pixelate":
        bot.answer_callback_query(call.id, "Pixelating your image...")
        pixelate_and_send(call.message)
    elif call.data == "ascii":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "The DEFAULT character set is - <@%#*+=-:. >, "
                                               "if you want to change its, just send 'new symbols' by first message, "
                                               "and then send me your own character set in next message. "
                                               "If you don't want to change default character set, send me 'default'.")
        bot.register_next_step_handler(call.message, ascii_users_choise)
    elif call.data in call_data_list:
        if call.data == "inversion":
            bot.answer_callback_query(call.id, "I'm inverting your image...")
        elif call.data == "mirror_vert":
            bot.answer_callback_query(call.id, "I'm mirroring vertically your image...")
        elif call.data == "mirror_horiz":
            bot.answer_callback_query(call.id, "I'm mirroring horizontally your image...")
        elif call.data == "heat_map":
            bot.answer_callback_query(call.id, "I'm building a heat map for your image...")
        elif call.data == "resize":
            bot.answer_callback_query(call.id, "I'm changing sizes of your image to stickers size...")
        many_func_handler_of_image(call.message, calldata=call.data)

    # elif call.data == "inversion":
    #     bot.answer_callback_query(call.id, "I'm inverting your image...")
    #     inverting_and_send(call.message)
    # elif call.data == "mirror_vert":
    #     bot.answer_callback_query(call.id, "I'm mirroring vertically your image...")
    #     mirroring_vert_and_send(call.message)
    # elif call.data == "mirror_horiz":
    #     bot.answer_callback_query(call.id, "I'm mirroring horizontally your image...")
    #     mirroring_horiz_and_send(call.message)


def pixelate_and_send(message):
    photo_id = user_states[message.chat.id]['photo']
    file_info = bot.get_file(photo_id)
    downloaded_file = bot.download_file(file_info.file_path)

    image_stream = io.BytesIO(downloaded_file)
    image = Image.open(image_stream)
    pixelated = pixelate_image(image, 20)

    output_stream = io.BytesIO()
    pixelated.save(output_stream, format="JPEG")
    output_stream.seek(0)
    bot.send_photo(message.chat.id, output_stream)


def ascii_and_send_standart(message, users_character=None):
    photo_id = user_states[message.chat.id]['photo']
    file_info = bot.get_file(photo_id)
    downloaded_file = bot.download_file(file_info.file_path)  # не совсем понимаю что желает этот метод .file_path

    image_stream = io.BytesIO(
        downloaded_file)  # что значит необработанные данные? Мы получили фото, но пайтон еще не понимает, что это фото?
    # или переводим фото в какой-то поток информации байтовый?
    ascii_art = image_to_ascii(image_stream, users_character=users_character)
    bot.send_message(message.chat.id, f"```\n{ascii_art}\n```", parse_mode="MarkdownV2")


def many_func_handler_of_image(message, calldata=None):
    photo_id = user_states[message.chat.id]['photo']
    file_info = bot.get_file(photo_id)
    downloaded_file = bot.download_file(file_info.file_path)

    image_stream = io.BytesIO(downloaded_file)
    image = Image.open(image_stream)
    if calldata == "inversion":
        processed_image = ImageOps.invert(image)
    elif calldata == "mirror_vert":
        processed_image = image.transpose(Image.FLIP_LEFT_RIGHT)
    elif calldata == "mirror_horiz":
        processed_image = image.transpose(Image.FLIP_TOP_BOTTOM)
    elif calldata == "heat_map":
        image = grayify(image)
        processed_image = ImageOps.colorize(image, black ="blue", white ="red")
    elif calldata == "resize":
        large_size = 512
        width, height = image.size
        if height > width:
            ratio = height / width
            new_height = large_size
            new_width = int(large_size / ratio)
        elif width > height:
            ratio = width / height
            new_width = large_size
            new_height = int(large_size / ratio)
        else:
            new_height = large_size
            new_width = large_size
        processed_image = image.resize((new_width, new_height))
    output_stream = io.BytesIO()
    processed_image.save(output_stream, format="JPEG")
    output_stream.seek(0)
    bot.send_photo(message.chat.id, output_stream)


# def inverting_and_send(message):
#     photo_id = user_states[message.chat.id]['photo']
#     file_info = bot.get_file(photo_id)
#     downloaded_file = bot.download_file(file_info.file_path)
#
#     image_stream = io.BytesIO(downloaded_file)
#     image = Image.open(image_stream)
#
#     inverted = ImageOps.invert(image)
#     output_stream = io.BytesIO()
#     inverted.save(output_stream, format="JPEG")
#     output_stream.seek(0)
#     bot.send_photo(message.chat.id, output_stream)
#
# def mirroring_vert_and_send(message):
#     photo_id = user_states[message.chat.id]['photo']
#     file_info = bot.get_file(photo_id)
#     downloaded_file = bot.download_file(file_info.file_path)
#
#     image_stream = io.BytesIO(downloaded_file)
#     image = Image.open(image_stream)
#
#     mirrored_vert = image.transpose(Image.FLIP_LEFT_RIGHT)
#     output_stream = io.BytesIO()
#     mirrored_vert.save(output_stream, format="JPEG")
#     output_stream.seek(0)
#     bot.send_photo(message.chat.id, output_stream)
#
# def mirroring_horiz_and_send(message):
#     photo_id = user_states[message.chat.id]['photo']
#     file_info = bot.get_file(photo_id)
#     downloaded_file = bot.download_file(file_info.file_path)
#
#     image_stream = io.BytesIO(downloaded_file)
#     image = Image.open(image_stream)
#
#     mirrored_vert = image.transpose(Image.FLIP_TOP_BOTTOM )
#     output_stream = io.BytesIO()
#     mirrored_vert.save(output_stream, format="JPEG")
#     output_stream.seek(0)
#     bot.send_photo(message.chat.id, output_stream)



bot.polling(none_stop=True)
