import requests
import json



def send_message(sender_id, text, token):
    json_request = requests.post(f'https://api.telegram.org/bot{token}/sendMessage?chat_id={sender_id}/&text={text}').json()

def respond(post_data, states):
    token = '5189961595:AAFS1oWXVmsUYuYCa0m5haGBti6PF2BnvvY'
    message = post_data['message']
    sender_id = str(message['from']['id'])
    if sender_id not in states:
        send_message(sender_id, 'Hello there', token)
        states[sender_id] = 'in'
    elif 'text' in message:
        send_message(sender_id, message['text'], token)
    else:
        send_message(sender_id, 'Cannot understand(', token)
    return states
