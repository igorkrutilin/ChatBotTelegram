import json
import subprocess as s
import sqlite3


class Chatbot():
    # função especial
    def __init__(self, nome):
        try:
            memoria = open(nome + '.json', 'r')
        except FileNotFoundError:
            memoria = open(nome + '.json', 'w')
            memoria.write('["Gabriel","Alfredo"]')
            memoria.close()
            memoria = open(nome + '.json', 'r')
        self.nome = nome
        self.conhecidos = json.load(memoria)
        memoria.close()
        self.historico = []
        self.frases = {
            'oi': 'Olá, qual o seu nome?', 'tchau': 'tchau, até mais '
        }
        self.agenda = {
            'atendimento': 'Certo. Que dia gostaria de realizar a consulta?',
                       'ok': 'agendado...'
        }

        self.diaSemana = {
            'segunda': 'pode ser as 8h?', 'sim': 'ok, agendado'
        }


    def escuta(self, frase=None):
        if frase == None:
            frase = input('>: ')
        frase = str(frase)
        frase = frase.lower()   # tranforma frase em minuscula
        frase = frase.replace('é', 'eh')    # subistituir é por eh
        return frase

    def pensa(self, frase):
        if frase in self.frases:
            return self.frases[frase]
        if frase in self.agenda:
            return self.agenda[frase]
        if frase in self.diaSemana:
            return self.diaSemana[frase]

        if frase == 'aprende':
            chave = input('Digite a frase: ')
            resp = input('Digite a resposta: ')
            self.frases[chave] = resp
            self.gravaMemoria()
            return 'Aprendido'
        if self.historico:
            if self.historico[-1] == 'Olá, qual o seu nome?':
                nome = self.pegaNome(frase)
                frase = self.respondeNome(nome)
                return frase

        try:
            resp = str(eval(frase))
            return resp
        except:
            pass
        return 'Não entendi'

    # Trata frases antes do nome
    def pegaNome(self, nome):
        if 'o meu nome eh ' in nome:
            nome = nome[14:]
        elif 'o meu nome é ' in nome:
            nome = nome[13:]

        nome = nome.title()     # trata primeira letra maiuscula
        return nome

    def respondeNome(self, nome):
        if nome in self.conhecidos:
            frase = 'Eaew '
            frase2 =  ' em que posso te ajudar? '
        else:
            frase = 'Muito prazer '
            frase2 = ' em que posso te ajudar? '
            self.conhecidos.append(nome)
            self.gravaMemoria()
        return frase + nome + frase2


    def gravaMemoria(self):
        memoria = open(self.nome + '.json', 'w')
        json.dump([self.conhecidos, self.frases], memoria)
        memoria.close()

    def fala(self, frase):
        if 'executa ' in frase:
            comando = frase.replace('executa ', '')
            try:
                s.Popen(comando)
            except FileNotFoundError:
                s.Popen(['xdg-open', comando])
        else:
            print(frase)
         # append inclue frase no historico
        self.historico.append(frase)


    def conectBanco(self, nomeBanco):
        self.conn = sqlite3.connect(nomeBanco)
        self.c = self.conn.cursor()

    def createTable(self):
        self.c.execute("CREATE TABLE AGENDA_DB(dia TEXT, horario TEXT , nomePessoa TEXT)")

    def enterData(self, dia, horario, nomePessoa):
        self.c.execute("INSERT INTO AGENDA_DB(dia, horario, nomePessoa) VALUES(?, ?, ?)", (dia, horario, nomePessoa))
        self.conn.commit()

    def searchSpecificData(self,horario):
        self.c.execute("SELECT dia FROM AGENDA_DB WHERE horario=?", (horario,))