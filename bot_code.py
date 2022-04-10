import requests
import json
import random
token = '5189961595:AAFS1oWXVmsUYuYCa0m5haGBti6PF2BnvvY'

alphabet = ['а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф', 'х', 'ч', 'ц', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я']
current = []
words = ['солнце', 'ведро', 'дождь', 'остров', 'заяц', 'чек', 'лёд', 'водолаз', 'шашлык', 'шрифт', 'мнение', 'понимание', 'часы', 'олицетворение', 'штурм', 'крюк', 'автор', 'чтение', 'стакан',  'жизнь']

def send_message(message, text):#функция для отправки сообщений
    id_ = message['from']['id']
    json_request = requests.get(f'https://api.telegram.org/bot{token}/sendMessage?chat_id={id_}/&text={text}').json()

def last_text_message():
    while True:
        json_request = requests.get(f'https://api.telegram.org/bot{token}/getUpdates').json()
        if json_request['ok'] != True:
            raise RuntimeError()
        for i in json_request['result']:
            if 'message' in i:
                if i['message']['message_id'] not in current:
                    current.append(i['message']['message_id'])
                    if 'text' in i['message']:
                        return i['message']
                    else:
                        send_message(i['message'], 'Не понимаю')

def read_all(current):
    json_request = requests.get(f'https://api.telegram.org/bot{token}/getUpdates').json()
    for i in json_request['result']:
            if 'message' in i:
                current.append(i['message']['message_id'])
    return current

def get_word(words):
    word = random.choice(words)
    letters = []
    for letter in word:
        letters.append('_')
    return word, letters

def play(message, words, alphabet):
    counter = 10
    used = []
    word, letters = get_word(words)
    send_message(message, ' '.join(letters))
    while '_' in letters and counter != 0:
        message = last_text_message()
        text = message['text'].lower()
        if text in alphabet and text not in used:
            used.append(text)
            if text in word:
                for i in range(len(word)):
                    if text == word[i]:
                        letters[i] = text
                send_message(message, ' '.join(letters))
            else:
                counter -= 1
                send_message(message, f'Ха, неверно, осталось попыток: {counter}')
        else:
            send_message(message, 'Новую букву давай')
    if counter == 0:
        send_message(message, f'Конец! словом было: ' + ' '.join(word))
    else:
        send_message(message, 'Поздравляю с победой!')

current = read_all(current)

while True:
    message = last_text_message()
    if message['text'] == '/start':
        send_message(message, 'Я Вешалка, бот игры в поле чудес.  Чтобы начать игру напишите "Начать", буквы "ё" и "й" отдельно')
    elif message['text'] == 'Начать':
        play(message, words, alphabet)
    elif message['text'] == 'Black holes':
        send_message(message, 'Solid ground')
    else:
        send_message(message, 'Не понимаю')
