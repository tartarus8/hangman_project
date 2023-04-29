import requests
import json
import random


alphabet = ['а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф', 'х', 'ч', 'ц', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я']
token = '5189961595:AAFS1oWXVmsUYuYCa0m5haGBti6PF2BnvvY'

def send_message(sender_id, text, token):
        json_request = requests.post(f'https://api.telegram.org/bot{token}/sendMessage?chat_id={sender_id}/&text={text}').json()


def get_leaderboard(state, sender_id):
    scores = []
    place = 1
    leaderboard = ''
    sender_place = 0

    for i in state.keys():
        if i[0] == 's' and state[i]['rating'] > 0:
            scores.append(state[i]['rating'])
    for score in reversed(sorted(scores)):
        for i in state.keys():
            if i[0] == 's' and score == state[i]['rating'] and place <= 10:     
                leaderboard += str(place) + '. ' + state[i]['name'] + ' ' + str(score) + '\n'
        if score == state[sender_id]['rating']:
            sender_place = place
        place += 1
    if sender_place == 0:
        return leaderboard

    return leaderboard + 'Вы на ' + str(sender_place) + ' месте'


def evaluate(word):

    points = 0
    for letter in word:
        if letter in ['а', 'о', 'п', 'р']:
            points += 1
        elif letter in ['б', 'в', 'г', 'д', 'е', 'з', 'и', 'к', 'л', 'м', 'н', 'с', 'т', 'у']:
            points += 2
        elif letter in ['ё', 'й', 'ж', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я']:
                points += 3

    return points


def get_word():
    with open('words.json', 'r') as fin:
        words = json.load(fin)
    word = random.choice(list(words.keys()))
    points = words[word]
    letters = []
    word = word[:-1]
    for letter in word:
        letters.append('_')

    return word, letters, points


def interpretate_message(state, text, chat_id, sender_id, token, alphabet):

    if text in ['/startnormal','/startnormal@veshalka259_bot', '/starthard', '/starthard@veshalka259_bot'] and state[chat_id]['game'] == 'out':
        word, letters, points = get_word()
        send_message(chat_id, ' '.join(letters), token)

        if 'hard' in text:
            attempts = 5
            game = 'in_hm'
        else:
            attempts = 10
            game = 'in_nm'

        state[chat_id] = {'game':game, 'word':word, 'letters':letters, 'attempts':attempts, 'used':[], 'points':points}
    
    elif text == '/rating' or text == '/rating@veshalka259_bot':
        send_message(chat_id, 'Ваш рейтинг: ' + str(state[sender_id]['rating']), token)
    
    elif text == '/leaderboard' or text == '/leaderboard@veshalka259_bot':
        send_message(chat_id, get_leaderboard(state, sender_id), token)

    elif '/add' in text:
        
        with open('words.json', 'r') as fin:
            words = json.load(fin)
        word = text.split('/add ')[1]
        
        if word + '\n' not in words.keys():
            words[word + '\n'] = evaluate(word)
            with open('words.json', 'w') as fout:
                json.dump(words, fout)
            send_message(chat_id, 'OK', token)
        else:
            send_message(chat_id, 'Not OK, word already used', token)

    elif text == '/allwords' or text == '/allwords@veshalka259_bot':

        with open('words.json', 'r') as fin:
            length = len(json.load(fin))
        output = f'Всего {length} слов'
        send_message(chat_id, output, token)

    elif state[chat_id]['game'] == 'in_nm' or state[chat_id]['game'] == 'in_hm':
        
        if text == 'ë':#these letters have different encodings
            text = 'ё'
        
        if text not in alphabet:
            return state
        elif text in state[chat_id]['used']:
            send_message(chat_id, 'Эта уже была', token)
            return state
        
        state[chat_id]['used'].append(text)
        if text not in state[chat_id]['word']:
            state[chat_id]['attempts'] -= 1
            send_message(chat_id, ' '.join(state[chat_id]['letters']) + '\nНет такой, попыток осталось: ' + str(state[chat_id]['attempts']), token)
            if state[chat_id]['attempts'] == 0:
                send_message(chat_id, 'Конец игры! Словом было: ' + state[chat_id]['word'], token)
                state[sender_id]['rating'] -= state[chat_id]['points']
                state[chat_id] = {'game':'out'}
            return state

        for i in range(len(state[chat_id]['word'])):
            if state[chat_id]['word'][i] == text:
                    state[chat_id]['letters'][i] = text
        send_message(chat_id, ' '.join(state[chat_id]['letters']), token)
        if '_' not in state[chat_id]['letters']:
            if state[chat_id]['game'] == 'in_hm':
                state[chat_id]['points'] *= 2
            send_message(chat_id, 'Поздравляю с победой!\nБаллов заработано: ' + str(state[chat_id]['points']), token)
            state[sender_id]['rating'] += state[chat_id]['points']
            state[chat_id] = {'game':'out'}

    return state


def respond(post_data, state):
    if 'message' not in post_data:
        return state

    message = post_data['message']
    chat_id = str(message['chat']['id'])
    sender_id = 's' + str(message['from']['id'])
    name = str(message['from']['first_name'])

    if chat_id not in state:
        send_message(chat_id, 'Привет, я Вешалка, бот для игры в виселицу. Буквы "Е", "Ë" и "И", "Й" считаю отдельно. Чтобы начать напишите "/startnormal". Для сложного режима "/starthard", в два раза больше очков! Чтобы узнать свой рейтинг напишите "/rating"', token)
        state[chat_id] = {'game':'out'}
    if sender_id not in state:
        state[sender_id] = {'rating':0, 'name':name}
    if name != state[sender_id]['name']:
        state[sender_id]['name'] = name
    elif 'text' in message:
        text = message['text'].lower()
        state = interpretate_message(state, text, chat_id, sender_id, token, alphabet)
    
    return state
