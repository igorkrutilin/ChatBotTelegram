import telepot
from Chatbot import Chatbot

telegram = telepot.Bot("614899342:AAHQN07RNMDfaCpWN21NJT54DDKkF2mmDzs")

bot = Chatbot("MariaBot")
bot.conectBanco('AgendaMaria.db')
#bot.createTable()
#bot.enterData('quinta-feira','08:00','joao')

def recebendoMsg(msg):
    frase = bot.escuta(frase=msg['text'])
    resp = bot.pensa(frase)
    bot.fala(resp)
    #chatID = msg['chat']['id']
    tipoMsg, tipoChat, chatID = telepot.glance(msg)
    telegram.sendMessage(chatID,resp)

telegram.message_loop(recebendoMsg)

while True:
    pass