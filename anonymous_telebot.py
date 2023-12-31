# Copyright (c) 2023 Minniti Julien

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of Anonymous Telebot and associated documentation files, to deal
# in Anonymous Telebot without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of Anonymous Telebot, and to permit persons to whom Anonymous Telebot is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of Anonymous Telebot.

# Anonymous Telebot IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH Anonymous Telebot OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from datetime import datetime
import time
import telepot
from telepot.loop import MessageLoop
import os
import json
import requests


# Retrieve information of owner, whitelist and bot
def secret():
    script_directory = os.path.dirname(os.path.abspath(__file__))
    secrets_path = os.path.join(script_directory, 'SECRETS.json')
    with open(secrets_path, 'r') as secrets_file:
        secrets = json.load(secrets_file)

    chat_id_key = secrets['id']
    chat_id_owner = secrets['id_owner']
    password = secrets['password']
    token = secrets['token']

    secrets_file.close()

    return chat_id_key, chat_id_owner, password, token


# Change password
def change_password(new_password):
    script_directory = os.path.dirname(os.path.abspath(__file__))
    secrets_path = os.path.join(script_directory, 'SECRETS.json')
    with open(secrets_path, 'r') as secrets_file:
        secrets = json.load(secrets_file)
    secrets['password'] = new_password
    with open(secrets_path, 'w') as secrets_file:
        json.dump(secrets, secrets_file)


# Initializing of Question To Answer
def qta_set(chat_id, answer):
    qta[chat_id] = {'answer': answer}


# Help
def help(chat_id):
    help_text = " /help - For help obviously\n/users - List of users\n/delete_account - To delete your account here\n/REPORT - To report someone. /USEROWNER will contact you.\n\n" \
                "How to send message to someone (e.g. USER1):\n/USER1 Hello World\n\n" \
                "You can also send pictures, photos and videos by adding recipient to caption like for message\n\n" \
                "If you need more help send message to /USEROWNER\n\n"
    bot.sendMessage(chat_id, help_text, parse_mode='HTML')


# Display user list
def users(chat_id):
    users_text = "/USEROWNER"
    for i in inverse_chat_id_verified:
        id_user = inverse_chat_id_verified[i]
        users_text += f"\n{id_user}"
    bot.sendMessage(chat_id, users_text, parse_mode='HTML')


# Main
def handle(msg):
    content_type, _, chat_id = telepot.glance(msg)  # Retrieve information about message

    # Is a Question to Answer ?
    try:
        answer = qta[chat_id]['answer']
    except KeyError:
        answer = '0'

    # Type of message
    if content_type == "text":  # TEXT
        command = msg['text']
    elif content_type == "photo":  # PHOTOS
        if 'caption' in msg:
            command = msg['caption']
            photos = msg["photo"]
            photo = photos[-1]
            photo_id = photo['file_id']
        else:
            command = ''
    elif content_type == 'video':  # VIDEO
        if 'caption' in msg:
            command = msg['caption']
            videos = msg["video"]
            video_id = videos['file_id']
        else:
            command = ""

    # Verify if it's a known user or owner
    if chat_id in chat_id_verified.values() or chat_id == chat_id_owner:

        # Utils
        if command == "/help":  # Send /help
            help(chat_id)

        elif command == "/users":  # Send users list
            users(chat_id)

        elif command == '/delete_account' and chat_id != chat_id_owner:  # Delete your user
            bot.sendMessage(chat_id, f"See you soon {inverse_chat_id_verified[chat_id]}")
            del chat_id_verified[inverse_chat_id_verified[chat_id]]

        elif command == '/REPORT':  # Report a user  (question)
            bot.sendMessage(chat_id, f'Who wanted to report you?')
            answer = 1
            qta_set(chat_id, answer)

        elif answer == 1:  # Report a user (answer)
            del qta[chat_id]
            bot.sendMessage(chat_id,
                            f"/USEROWNER is alerted about your report about {command}. You will be contacted soon by /USEROWNER")
            bot.sendMessage(chat_id_owner, f"REPORT of {command} by {inverse_chat_id_verified[chat_id]}")

        # Message from VERIFIED
        elif command.startswith("/USER") and chat_id != chat_id_owner:

            if command.startswith("/USEROWNER"):  # Send messages to OWNER
                if content_type == 'photo':
                    bot.sendPhoto(chat_id_owner, photo_id, f"From {inverse_chat_id_verified[chat_id]} to {command}")
                elif content_type == 'video':
                    bot.sendVideo(chat_id_owner, video_id, caption=f"From {inverse_chat_id_verified[chat_id]} to {command}")
                else:
                    bot.sendMessage(chat_id_owner, f"From {inverse_chat_id_verified[chat_id]} to {command}")

            else:
                for id_verified in chat_id_verified:  # Send messages to USER
                    if command.startswith(id_verified):
                        if content_type == 'photo':
                            bot.sendPhoto(chat_id_verified[id_verified], photo_id,
                                          f"From {inverse_chat_id_verified[chat_id]} to {command}")
                        elif content_type == 'video':
                            bot.sendVideo(chat_id_verified[id_verified], video_id,
                                          caption=f"From {inverse_chat_id_verified[chat_id]} to {command}")
                        else:
                            bot.sendMessage(chat_id_verified[id_verified],
                                            f"From {inverse_chat_id_verified[chat_id]} to {command}")

        # Message from OWNER
        elif chat_id == chat_id_owner:
            if command == "/waiting":  # Send list of waiting ID
                bot.sendMessage(chat_id_owner, chat_id_waiting)

            elif command == "/verified":  # Send list of verified ID
                bot.sendMessage(chat_id_owner, chat_id_verified)

            elif command == "/banned":  # Send list of banned ID
                bot.sendMessage(chat_id_owner, chat_id_banned)

            elif command.startswith("/USER"):  # Send messages to USER by OWNER
                for id_verified in chat_id_verified:
                    if command.startswith(id_verified):
                        if content_type == 'photo':
                            bot.sendPhoto(chat_id_verified[id_verified], photo_id,
                                          f"From /USEROWNER to {command}")
                        elif content_type == 'video':
                            bot.sendVideo(chat_id_verified[id_verified], video_id,
                                          caption=f"From /USEROWNER to {command}")
                        else:
                            bot.sendMessage(chat_id_verified[id_verified],
                                            f"From /USEROWNER to {command}")

            elif command.startswith("/setpassword "):  # Change password
                new_password = command.split("/setpassword ")[1]
                change_password(new_password)
                _, _, password, _ = secret()
                bot.sendMessage(chat_id_owner, f"Password changed to {password}")

            elif command == "/password":  # Send password to OWNER
                _, _, password, _ = secret()
                bot.sendMessage(chat_id_owner, f"Password: {password}")

            elif command.startswith("/DEL "):  # Ban a user
                user = command.split("/DEL ")[1]
                if user in inverse_chat_id_verified.values():
                    bot.sendMessage(chat_id_verified[user], "Access removed. You are banned.")
                    chat_id_banned.append(chat_id_verified[user])
                    del chat_id_verified[user]
                    bot.sendMessage(chat_id, f"{user} banned.")

    # Connection to the Anonymous Bot
    elif chat_id not in chat_id_key:
        if chat_id not in chat_id_waiting and chat_id not in chat_id_verified.values() and chat_id not in chat_id_banned:  # For new users
            chat_id_waiting.append(chat_id)
            message_to_unknown_id = f'Welcome to Anonymous TelegramBot, please enter password.'
            bot.sendMessage(chat_id, message_to_unknown_id)

        elif chat_id in chat_id_banned:  # Block banned users
            bot.sendMessage(chat_id, f"Access removed. You are banned.")

        else:
            _, _, password, _ = secret()  # Valid or not users access
            if command == password:
                chat_id_verified["/USER" + str(len(chat_id_verified) + 1)] = chat_id
                inverse_chat_id_verified.update({v: k for k, v in chat_id_verified.items()})
                chat_id_waiting.remove(chat_id)
                message_to_unknown_id = f'Connection done, congratulation. You are {inverse_chat_id_verified[chat_id]}. See /help to know how to use the ChatBot'
                bot.sendMessage(chat_id, message_to_unknown_id)
            else:
                message_to_unknown_id = f'Wrong password.'
                bot.sendMessage(chat_id, message_to_unknown_id)


chat_id_waiting = []
chat_id_verified = {}
chat_id_banned = []
inverse_chat_id_verified = {}
qta = {}

chat_id_key, chat_id_owner, _, token = secret()
bot = telepot.Bot(token)
MessageLoop(bot, handle).run_as_thread()
print('Im listening...')
for id_user in chat_id_key:
    bot.sendMessage(id_user, 'Anonymous ChatBot open')

while True:
    time.sleep(1)
