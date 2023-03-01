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
import tg_bot as bot
import logging



logger = logging.getLogger(__name__)



class TelegramWebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        logger.info("New POST request")
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            decoded_data = json.loads(post_data.decode('utf-8'))
            self.server.state = bot.respond(json.loads(post_data.decode('utf-8')), self.server.state)
        except json.decoder.JSONDecodeError:
            logger.exception("Failed to decode data")
        except:
            logger.exception("some other error")
        else:
            logger.info("Request handled successfully")
        finally:
            self.send_response(200, "OK")
            self.end_headers()


class StatedHTTPServer(HTTPServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = dict()
    def save_state(self):
        with open("state.json", "w") as fout:
            json.dump(self.state, fout)

    def load_state(self):
        with open("state.json", "r") as fin:
            self.state = json.load(fin)

# 'localhost' adress allows only clients from the same host,
# while '0.0.0.0' exposes the sever to web
server = StatedHTTPServer(('0.0.0.0', 443), TelegramWebhookHandler)
# enable SSL (HTTPS) support using code from
# https://blog.anvileight.com/posts/simple-python-http-server/#example-with-ssl-support
server.socket = ssl.wrap_socket(
    server.socket,
    keyfile='private.key',
    certfile='cert.pem',
    server_side=True
)
logging.basicConfig(level=logging.INFO)
server.load_state()
try:
    server.serve_forever()
except KeyboardInterrupt:
    pass
finally:
    server.save_state()
