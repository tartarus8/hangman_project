"""This module implements getting telegram bot updates 
via webhook. To set webhooks for this server, use
    curl -F "url=https://<YOUR_PUBLIC_IPV4_ADDRESS>/" -F "certificate=@cert.pem" https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook
telegram API call.
To create self-signed SSL certificate, use
   openssl req -newkey rsa:2048 -sha256 -nodes -keyout private.key -x509 -days 3650 -out cert.pem
(taken from https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks).
    In case of bugs use "logging.basicConfig(level=logging.DEBUG)"
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
import json
import requests
import bot_code as bot
import logging


class TelegramWebhookHandler(BaseHTTPRequestHandler):
    states = {}
    def do_GET(self):
        pass

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        self.send_response(200, "OK")
        self.end_headers()

        try:
            self.states = bot.respond(json.loads(post_data.decode('utf-8')), self.states)
        except json.decoder.JSONDecodeError:
            print(post_data.decode('utf-8'))


# 'localhost' adress allows only clients from the same host,
# while '0.0.0.0' exposes the sever to web
server = HTTPServer(('0.0.0.0', 443), TelegramWebhookHandler)
# enable SSL (HTTPS) support using code from
# https://blog.anvileight.com/posts/simple-python-http-server/#example-with-ssl-support
server.socket = ssl.wrap_socket(
    server.socket,
    keyfile='private.key',
    certfile='cert.pem',
    server_side=True
)
server.serve_forever()
