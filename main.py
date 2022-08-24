import cv2
import datetime
import requests
import telebot
import time
import schedule
import gspread
from pil import Image
from telebot import types
from multiprocessing.context import Process

gc = gspread.service_account()
bot = telebot.TeleBot("BOT_TOKEN")
spread_source = "GSPREAD_TOKEN"


@bot.message_handler(commands=['start', 'help'])
def sendWelcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("LINK_1")
    btn2 = types.KeyboardButton("LINK_2")
    markup.add(btn1, btn2)
    bot.send_message(message.from_user.id, "/link1 - description"
                                           "\n/link2 - description", reply_markup=markup)


@bot.message_handler(commands=['new_user'])
def userRegistration(message):
    user_info = []
    user_info.append(message.from_user.id)
    worksheet = gc.open_by_key(spread_source).sheet1
    worksheet.append_row(user_info)


@bot.message_handler(content_types=['text'])
def getLink(message):
    if message.text == "LINK_1" \
            or message.text == "LINK_2" \
            or message.text == "/link1" \
            or message.text == "/link2":
        now = datetime.datetime.now()
        getPic(now)
        print(str(now.date()) + " " + str(now.time()) + " " + str(message.from_user.id))
        if message.text == "LINK_1" or message.text == "/link1":
            img = cv2.imread("income.jpg")
            result = "Link 1: "
        if message.text == "LINK_2"  or message.text == "/link2":
            img = cv2.imread("outcome.jpg")
            result = "Link 2: "

        detector = cv2.QRCodeDetector()
        data, points, straight_qrcode = detector.detectAndDecode(img)
        if points is not None:
            print(data)

        source = open('source_pic.jpg', 'rb')
        bot.send_photo(message.from_user.id, source)
        bot.send_message(message.from_user.id, result + data)


def getPic(now):
    path = ("SOURCE_PIC_HTML_PAGE")

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


def autoIncomeLink():
    worksheet = gc.open_by_key(spread_source).sheet1
    id_list = worksheet.col_values(1)
    now = datetime.datetime.now()
    getPic(now)
    img = cv2.imread("income.jpg")
    detector = cv2.QRCodeDetector()
    data, points, straight_qrcode = detector.detectAndDecode(img)
    for id in id_list:
        source = open('source_pic.jpg', 'rb')
        bot.send_photo(id, source)
        bot.send_message(id, "Link 1: " + data)


def autoOutcomeLink():
    worksheet = gc.open_by_key(spread_source).sheet1
    id_list = worksheet.col_values(1)
    now = datetime.datetime.now()
    getPic(now)
    img = cv2.imread("outcome.jpg")
    detector = cv2.QRCodeDetector()
    data, points, straight_qrcode = detector.detectAndDecode(img)
    for id in id_list:
        source = open('source_pic.jpg', 'rb')
        bot.send_photo(id, source)
        bot.send_message(id, "Link 2: " + data)


schedule.every().day.at("FIRST TIME").do(autoIncomeLink)
schedule.every().day.at("SECOND TIME").do(autoOutcomeLink)


class ScheduleMessage():
    def try_send_schedule():
        while True:
            schedule.run_pending()
            time.sleep(1)

    def start_process():
        p1 = Process(target=ScheduleMessage.try_send_schedule, args=())
        p1.start()


if __name__ == '__main__':
    ScheduleMessage.start_process()
    for i in range(0, 1):
        while True:
            try:
                bot.polling(none_stop=True, interval=0)
            except:
                print(str(datetime.datetime.now().time()) + " Exception")
                time.sleep(15)
                continue
            break
