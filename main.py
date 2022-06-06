import cv2
import datetime
import requests
import telebot
import time
from pil import Image
from telebot import types

bot = telebot.TeleBot("BOT_TOKEN")

@bot.message_handler(commands=['start', 'help'])
def sendWelcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("LINK_1")
    btn2 = types.KeyboardButton("LINK_2")
    markup.add(btn1, btn2)
    bot.send_message(message.from_user.id, "/link1 - description"
                                           "/link2 - description", reply_markup=markup)


@bot.message_handler(content_types=['text'])
def getLink(message):
    if message.text == "LINK_1" \
            or message.text == "LINK_2" \
            or message.text == "/link1" \
            or message.text == "/link2":
        now = datetime.datetime.now()
        path = ("SOURCE_PIC_HTML_LINK")
        print(str(now.date()) + " " + str(now.time()) + " " + str(message.from_user.id) + "\n" + path)

        with open('source_pic.jpg', 'wb') as handle:
            responce = requests.get(path, stream=True)
            if not responce.ok:
                print(responce)
            for block in responce.iter_content(1024):
                if not block:
                    break
                handle.write(block)

        source = Image.open("source_pic.jpg")
        width, height = source.size
        cropped_width = int(width / 2)
        img = source.crop((0, 0, cropped_width, height))
        img.save('income.jpg')
        img = source.crop((cropped_width, 0, width, height))
        img.save('outcome.jpg')

        if message.text == "LINK_1" or message.text == "/link1":
            img = cv2.imread("income.jpg")
            result = "Link 1: "
        if message.text == "LINK_2" or message.text == "/link2":
            img = cv2.imread("outcome.jpg")
            result = "Link 2: "

        detector = cv2.QRCodeDetector()
        data, points, straight_qrcode = detector.detectAndDecode(img)
        if points is not None:
            print(data)

        source = open('source_pic.jpg', 'rb')
        bot.send_photo(message.from_user.id, source)
        bot.send_message(message.from_user.id, result + data)


for i in range(0, 1):
    while True:
        try:
            bot.polling(none_stop=True, interval=0)
        except:
            print(str(datetime.datetime.now().time()) + " Exception")
            time.sleep(15)
            continue
        break