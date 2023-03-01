import requests
import json
import random


alphabet = ['а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф', 'х', 'ч', 'ц', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я']
token = '5189961595:AAFS1oWXVmsUYuYCa0m5haGBti6PF2BnvvY'

def send_message(sender_id, text, token):
        json_request = requests.post(f'https://api.telegram.org/bot{token}/sendMessage?chat_id={sender_id}/&text={text}').json()


def evaluate(words):
    evaluated_words = dict()
    for word in words:
        points = 0
        for letter in word:
            if letter in ["а", "о", "п", "р"]:
                points += 1
            elif letter in ["б", "в", "г", "д", "е", "з", "и", "к", "л", "м", "н", "с", "т", "у"]:
                points += 2
            elif letter in ["ё", "й", "ж", "ф", "х", "ц", "ч", "ш", "щ", "ъ", "ы", "ь", "э", "ю", "я"]:
                points += 3
        evaluated_words[word] = points
    return evaluated_words


def get_word():
    with open("words.json", "r") as fin:
        words = json.load(fin)
    word = random.choice(list(words.keys()))
    points = words[word]
    letters = []
    word = word[:-1]
    for letter in word:
        letters.append('_')

    return word, letters, points


def interpretate_message(state, text, chat_id, sender_id, token, alphabet):
    if (text == '/startnormal' or text == '/startnormal@veshalka259_bot') and state[chat_id]['game'] == 'out':
        word, letters, points = get_word()
        send_message(chat_id, ' '.join(letters), token)
        state[chat_id] = {'game':'in_nm', 'word':word, 'letters':letters, 'attempts':10, 'used':[], 'points':points, 'rating':state[chat_id]['rating']}

    elif text == ('/starthard' or text == '/starthard@veshalka259_bot') and state[chat_id]['game'] == 'out':
        word, letters, points = get_word()
        send_message(chat_id, ' '.join(letters), token)
        state[chat_id] = {'game':'in_hm', 'word':word, 'letters':letters, 'attempts':5, 'used':[], 'points':points, 'rating':state[chat_id]['rating']}
        
    elif text == '/rating' or text == '/rating@veshalka259_bot':
        send_message(chat_id, 'Ваш рейтинг: ' + str(state[sender_id]['rating']) + ' баллов', token)

    elif state[chat_id]['game'] == 'in_nm' or state[chat_id]['game'] == 'in_hm':
        if text in alphabet and text not in state[chat_id]['used']:
            state[chat_id]['used'].append(text)
            if text in state[chat_id]['word']:
                for i in range(len(state[chat_id]['word'])):
                    if state[chat_id]['word'][i] == text:
                        state[chat_id]['letters'][i] = text
                send_message(chat_id, ' '.join(state[chat_id]['letters']), token)
                if '_' not in state[chat_id]['letters']:
                    if state[chat_id]['game'] == 'in_hm':
                        state[chat_id]['points'] *= 2
                    send_message(chat_id, 'Поздравляю с победой!\nБаллов заработано: ' + str(state[chat_id]['points']), token)
                    state[sender_id]['rating'] += state[chat_id]['points']
                    state[chat_id]['game'] = 'out'
            else:
                state[chat_id]['attempts'] -= 1
                send_message(chat_id, ' '.join(state[chat_id]['letters']) + '\nНет такой, попыток осталось: ' + str(state[chat_id]['attempts']), token)
                if state[chat_id]['attempts'] == 0:
                    send_message(chat_id, 'Конец игры! Словом было: ' + state[chat_id]['word'], token)
                    state[sender_id]['rating'] -= state[chat_id]['points']
                    state[chat_id]['game'] = 'out'

    return state


def respond(post_data, state):
    if 'message' not in post_data:
        return state
    message = post_data['message']
    chat_id = str(message['chat']['id'])
    sender_id = str(message['from']['id'])

    if chat_id not in state:
        send_message(chat_id, 'Привет, я Вешалка, бот для игры в виселицу. Буквы "Е", "Ë" и "И", "Й" считаю отдельно. Чтобы начать напишите "/startnormal". Для сложного режима "/starthard", в два раза больше очков! Чтобы узнать свой рейтинг напишите "/rating"', token)
        state[chat_id] = {'game':'out', 'rating':0}
    if sender_id not in state:
        state[sender_id] = {'game':'out', 'rating':0} 
    elif 'text' in message:
        text = message['text'].lower()
        states = interpretate_message(state, text, chat_id, sender_id, token, alphabet)
    
    return state
