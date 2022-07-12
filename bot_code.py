import requests
import json
import random



def send_message(sender_id, text, token):
        json_request = requests.post(f'https://api.telegram.org/bot{token}/sendMessage?chat_id={sender_id}/&text={text}').json()

def get_word(words):
    word = random.choice(words)
    letters = []
    for letter in word:
        letters.append('_')
    return word, letters


def respond(post_data, states):


    alphabet = ['а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф', 'х', 'ч', 'ц', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я']
    words = ['солнце', 'ведро', 'дождь', 'остров', 'заяц', 'чек', 'лёд', 'водолаз', 'шашлык', 'шрифт', 'мнение', 'понимание', 'часы', 'олицетворение', 'штурм', 'крюк', 'автор', 'чтение', 'стакан',  'жизнь']
    token = '5189961595:AAFS1oWXVmsUYuYCa0m5haGBti6PF2BnvvY'


    message = post_data['message']
    sender_id = str(message['from']['id'])

    if sender_id not in states:
        send_message(sender_id, 'Привет, я Вешалка, бот для игры в виселицу. Буквы "Е", "Ë" и "И", "Й" считаю отдельно. Чтобы начать напиши "начать"', token)
        states[sender_id] = {'state':'out'}

    elif 'text' in message:
        text = message['text'].lower()
        if text == 'начать' and states[sender_id]['state'] == 'out':
            word, letters = get_word(words)
            send_message(sender_id, ' '.join(letters), token)
            states[sender_id] = {'state':'in', 'word':word, 'letters':letters, 'attempts':10, 'used':[]}
        elif states[sender_id]['state'] == 'in':
            if text in alphabet:
                if text not in states[sender_id]['used']:
                    if text in states[sender_id]['word']:
                        for i in range(len(states[sender_id]['word'])):
                            if states[sender_id]['word'][i] == text:
                                states[sender_id]['letters'][i] = text
                        send_message(sender_id, ' '.join(states[sender_id]['letters']), token)
                        if '_' not in states[sender_id]['letters']:
                            send_message(sender_id, 'Поздравляю с победой!', token)
                            states[sender_id] = {'state':'out'}
                    else:
                        states[sender_id]['used'].append(text)
                        states[sender_id]['attempts'] -= 1
                        send_message(sender_id, ' '.join(states[sender_id]['letters']), token)
                        send_message(sender_id, 'Нет такой, попыток осталось: ' + str(states[sender_id]['attempts']), token)
                        if states[sender_id]['attempts'] == 0:
                            send_message(sender_id, 'Конец игры! Словом было: ' + states[sender_id]['word'], token)
                            states[sender_id] = {'state':'out'}
                else:
                    send_message(sender_id, 'Новую букву давай', token)
            else:
                send_message(sender_id, 'Не понимаю', token)

    else:
        send_message(sender_id, 'Не понимаю', token)
    return states
