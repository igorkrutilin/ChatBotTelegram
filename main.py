from Chatbot import Chatbot

Bot = Chatbot('Maria')
Bot.conectBanco('AgendaMaria.db')
Bot.enterData('quinta-feira','08:00','joao')
while True:
    frase = Bot.escuta()
    resp = Bot.pensa(frase)
    Bot.fala(resp)
    if resp == 'tchau':
        break