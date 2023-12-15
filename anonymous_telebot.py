from datetime import datetime
import time
import telepot
from telepot.loop import MessageLoop
import os
import json
import requests

script_directory = os.path.dirname(os.path.abspath(__file__))
secrets_path = os.path.join(script_directory, 'SECRETS.json')
with open(secrets_path, 'r') as secrets_file:
    secrets = json.load(secrets_file)

chat_id_key = secrets['id']
chat_id_owner = secrets['id_owner']
password = secrets['password']

chat_id_waiting = []
chat_id_verified = {}
inverse_chat_id_verified = {}


def help(chat_id):
    help_text = " /help - For help obviously\n/users - List of users\n\nHow to send message to someone (e.g. USER1):\n/USER1 Hello World\n\nIf you need more help send message to /USEROWNER"
    bot.sendMessage(chat_id, help_text, parse_mode='HTML')


def users(chat_id):
    users_text = "/USEROWNER"
    for i in inverse_chat_id_verified:
        id_user = inverse_chat_id_verified[i]
        users_text += f"\n{id_user}"
    bot.sendMessage(chat_id, users_text, parse_mode='HTML')


def handle(msg):
    chat_id = msg['chat']['id']
    command = msg['text']

    if chat_id in chat_id_verified.values() or chat_id == chat_id_owner:
        if command == "/help":
            help(chat_id)
        if command == "/users":
            users(chat_id)
        # Message from verified
        if chat_id in chat_id_verified.values():
            if command.startswith("/USER"):
                if command.startswith("/USEROWNER"):
                    bot.sendMessage(chat_id_owner, f"From {inverse_chat_id_verified[chat_id]} to {command}", parse_mode='HTML')
                else:
                    for id_verified in chat_id_verified:
                        if command.startswith(id_verified):
                            bot.sendMessage(chat_id_verified[id_verified], f"From {inverse_chat_id_verified[chat_id]} to {command}", parse_mode='HTML')

        # Message from owner
        elif chat_id == chat_id_owner:
            if command == "/waiting":
                bot.sendMessage(chat_id_owner, chat_id_waiting, parse_mode='HTML')
            elif command == "/verified":
                bot.sendMessage(chat_id_owner, chat_id_verified, parse_mode='HTML')
            elif command.startswith("/USER"):
                for id_verified in chat_id_verified:
                    if command.startswith(id_verified):
                        bot.sendMessage(chat_id_verified[id_verified], f"From /USEROWNER to {command}", parse_mode='HTML')

    # Connection to the Anonymous Bot
    elif chat_id not in chat_id_key:
        if chat_id not in chat_id_waiting and chat_id not in chat_id_verified.values():
            chat_id_waiting.append(chat_id)
            message_to_unknown_id = f'Welcome to Anonymous TelegramBot, please enter password.'
            bot.sendMessage(chat_id, message_to_unknown_id)
        else:
            if command == password:
                chat_id_verified["/USER" + str(len(chat_id_verified) + 1)] = chat_id
                inverse_chat_id_verified.update({v: k for k, v in chat_id_verified.items()})
                chat_id_waiting.remove(chat_id)
                message_to_unknown_id = f'Connection done, congratulation. You are {inverse_chat_id_verified[chat_id]}. See /help to know how to use the ChatBot'
                bot.sendMessage(chat_id, message_to_unknown_id)
            else:
                message_to_unknown_id = f'Wrong password.'
                bot.sendMessage(chat_id, message_to_unknown_id)


bot = telepot.Bot(secrets['token'])
MessageLoop(bot, handle).run_as_thread()
print('Im listening...')
for id_user in chat_id_key:
    bot.sendMessage(id_user, 'Anonymous ChatBot open')

while True:
    time.sleep(10)
