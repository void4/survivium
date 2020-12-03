import twitch
import sys
from threading import Thread
from configparser import SafeConfigParser

parser = SafeConfigParser()
parser.read("config.ini")

def config(key):
    return parser.get("DEFAULT", key)

messages = []

def chat():
    twitch.Chat(channel=config("channel"), nickname=config("nickname"), oauth=config("oauth")).subscribe(
            lambda message: messages.append(message))

thread = Thread(target=chat)
thread.daemon = True
thread.start()


"""
try:
except (KeyboardInterrupt, SystemExit):
    #thread.kill()
    sys.exit()
"""
