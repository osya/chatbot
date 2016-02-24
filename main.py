# -*- coding: utf-8 -*-
import requests
from lxml import html
import time
import argparse


class ChatBotClient:
    __url = ''
    __client_name = 'You'
    __bot_name = 'Mitsuku'

    def __init__(self, _url, _client_name='You', _bot_name='Mitsuku'):
        self.__url = _url
        self.__client_name = _client_name
        self.__bot_name = _bot_name

    def send(self, _message):
        r = requests.post(url, data={'message': _message})
        tree = html.fromstring(r.text)
        line = tree.xpath('./body/p/font/*')
        answer = line[2].tail
        print '%s: %s' % (self.__bot_name, answer)


if __name__ == '__main__':
    client_name = 'You'
    url = 'http://fiddle.pandorabots.com/pandora/talk?botid=9fa364f2fe345a10&skin=demochat'
    client = ChatBotClient(url, client_name, 'Mitsuku')

    p = argparse.ArgumentParser()
    p.add_argument('-m', dest='message', help='your message')
    args = p.parse_args()
    if args.message:
        print '%s: %s' % (client_name, args.message)
        client.send(args.message)
    else:
        print 'Type ''exit''<Enter> to exit'
        while True:
            message = raw_input('You: ')
            if 'exit' == message:
                break
            client.send(message)
            time.sleep(.3)
