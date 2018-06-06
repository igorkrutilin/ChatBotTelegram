import json
import subprocess as s
import sqlite3

#bot = Chatbot("MariaBot")


class Chatbot():
    # função especial
    def __init__(self, nome):
        try:
            memoria = open(nome + '.json', 'r')
        except FileNotFoundError:
            memoria = open(nome + '.json', 'w')
            memoria.write('[["Will","Alfredo"],{"oi": "Olá, qual o seu nome?","tchau":"tchau, até mais..."}]')
            memoria.close()
            memoria = open(nome + '.json', 'r')
        self.nome = nome
        self.conhecidos, self.frases = json.load(memoria)
        memoria.close()
        self.historico = [None,]
        self.resp=0
        self.resp1=0
        self.id=0
        self.diaEscolhido = ['','','','','']

        self.lista_cumprimentar = {'oi', 'ola', 'olá', 'oie', 'bão', 'bao', 'eai', 'opa', 'joia', 'joinha',
                                     'bom', 'dia', 'boa', 'tarde', 'noite'}

        self.agenda = {'atendimento','agendamento','fazer agendamento','marcar atendimento',
                       'marcar agendamento','marcar agendamento', 'consulta','consulta medica','agendar consulta','agendar atendimento' }

        self.horarioAtendimentos = {'horario de atendimentos', 'meus horarios', 'horarios agendado' }

        self.desmarcarAgenda = {'desmarcar', 'desmarcar agendamento', 'desmarcar consulta'}

        self.diaSemana = {   'segunda','terça', 'quarta', 'quinta','sexta',
                             'segunda-feira', 'terça-feria','quarta-feira','quinta-feira', 'sexta-feira'
                         }
        self.diaFDS = {'sabado', 'domingo'}

        self.horarioDisponiveis = {
                                    '08:00','09:00','10:00','11:00','13:00','14:00','15:00','16:00','17:00'
                                    '8','08','9','09','10','11','13','14','15','16','17','18'
                                 }
        self.horarioIndis = { '12:00', '12' }



    def escuta(self, frase=None):
        if frase == None:
            frase = input('>: ')
        frase = str(frase)
        frase = frase.lower()   # tranforma frase em minuscula
        frase = frase.replace('é', 'eh')    # subistituir é por eh
        return frase

    def fim(self,):
        nome = self.nome
        self.__init__("MariaBot")
        self.nome=nome


    def pensa(self,frase):
        if frase in self.frases:
            return self.frases[frase]
        if frase in self.lista_cumprimentar:
            return "Olá, qual o seu nome?"
        if frase in self.agenda:
            diasDaSemana = "Temos dias disponiveis\n\nSegunda-feira\nTerça-feria\nQuarta-feira\nQuinta-feira\nSexta-feira\nQue dia prefere?\n"
            return diasDaSemana
        if frase in self.diaSemana:
            self.diaEscolhido[3]=frase
            horariosDia = "Horarios disponiveis na " + frase.title() + "\n08:00\n09:00\n10:00\n11:00\n13:00\n14:00\n15:00\n16:00\n17:00"
            return horariosDia
        if frase in self.diaFDS:
            return 'Infelismente não trabalhamos nesse dia,\nApenas dias uteis e horarios comecias '

        if frase in self.horarioDisponiveis:
            self.diaEscolhido[4]=frase
            self.conectBanco('AgendaMaria.db')
            print("dia ",self.diaEscolhido[3])
            self.inserirAgendamento(self.id, self.diaEscolhido[3], self.diaEscolhido[4], self.diaEscolhido[1])
            self.disconectBanco()
            self.diaEscolhido =0
            return 'Ok as '+frase+ ' agendado anote seu ID '+str(self.id)+ ' caso precise desmarcar\n mais alguma coisa que posso te ajudar?'

        if frase in self.desmarcarAgenda:
            self.resp=1
            return 'Digite seu ID: '

        if 1 == self.resp:
            self.diaEscolhido = int(frase)
            self.conectBanco('AgendaMaria.db')
            self.deleteAgendamento(int(self.diaEscolhido))
            self.disconectBanco()
            self.resp=0
            self.diaEscolhido=0
            return 'Ok Id numero ' + frase + ' foi desmarcado '

        if frase in self.horarioAtendimentos:
            self.resp1 = 2
            return 'Digite seu ID: '

        if 2 == self.resp1:
            self.diaEscolhido = int(frase)
            #self.conectBanco('AgendaMaria.db')
            tupla = self.searchSpecificData(int(self.diaEscolhido),'AgendaMaria.db')
            self.disconectBanco()
            self.resp1 = 0
            return 'Ok Id numero ' + frase + ' seu ´horario é... ' + str(tupla)


        if frase == 'sim':
            return 'Estou a disposição, o que seria?'
        if frase == 'nao obrigado':
            return 'Tenha um otimo dia, tchau'



        if frase == 'aprende':
            return 'Digite a frase: '

        # Responde frases que dependem do historico
        ultimaFrase = self.historico[-1]
        if ultimaFrase == 'Olá, qual o seu nome?':
            nome = self.pegaNome(frase)
            self.diaEscolhido[1] = nome
            frase = self.respondeNome(nome)
            #self.enterDataCliente(0, frase)
            return frase

        ultimaFrase = self.historico[-3]
        if ultimaFrase == 'Temos dias diposniveis, qual dia?':
            self.chave = frase
            self.conectBanco('AgendaMaria.db')
            self.enterSemana(self.id, frase)
            self.disconectBanco()
            return frase + ' ok'

        if ultimaFrase ==  'Qual Horario':
            self.chave = frase
            return 'Ok ' + frase +' agendando, Mais alguma coisa que posso ajudar?'


        if ultimaFrase == 'Digite a frase: ':
            self.chave = frase
            return 'Digite a resposta: '
        if ultimaFrase == 'Digite a resposta: ':
            resp = frase
            self.frases[self.chave] = resp
            self.gravaMemoria()
            return 'Aprendido'
        if ultimaFrase == 'Temos horarios disponiveis nesse dia ':
            resp = frase
            self.frases[self.chave] = resp
            self.gravaMemoria()
            return 'agendado'
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
        else:
            frase = 'Muito prazer '
            self.conhecidos.append(nome)
            self.gravaMemoria()
        frase2 = ' em que posso te ajudar? \n\nAgendar consulta\nHorarios de atendimentos\nDesmarcar consulta '
        self.contagemClientes('AgendaMaria.db')
        self.disconectBanco()
        self.conectBanco('AgendaMaria.db')
        self.enterDataCliente(self.id, nome)
        self.disconectBanco()
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

    def contagemClientes(self, nomeBanco):
        self.conn = sqlite3.connect(nomeBanco)
        self.c = self.conn.cursor()
        self.c.execute("SELECT COUNT(*) FROM CLIENTE WHERE id>=0")
        id = self.c.fetchone()
        print("numero de seres humanos: ",id[0])
        self.id = id[0]+1

    def disconectBanco(self,):
        self.c = self.conn.close()


    def createTable(self):
        self.c.execute("CREATE TABLE AGENDA_DB(dia TEXT, horario TEXT , nomePessoa TEXT)")

    def enterData(self, dia, horario, nomePessoa):
        self.c.execute("INSERT INTO AGENDA_DB(dia, horario, nomePessoa) VALUES(?, ?, ?)", (dia, horario, nomePessoa))
        self.conn.commit()

    def enterSemana(self, idDia, dia ):
        self.c.execute("INSERT INTO diasemana(idDia, Dia) VALUES(?, ?)", (idDia, dia))
        self.conn.commit()

    def enterDataCliente(self, id, nomePessoa):
        self.c.execute("INSERT INTO CLIENTE(id, nome) VALUES(?, ?)", (id, nomePessoa))
        self.conn.commit()

    def inserirAgendamento(self, id, diaSemana, horarioDia, nomePessoa):
        self.c.execute("INSERT INTO AGENDA_DB(id, dia, horario, cliente) VALUES(?, ?, ?, ?)", (id, diaSemana, horarioDia, nomePessoa))
        self.conn.commit()

    def deleteAgendamento(self, id):
       # self.c.execute("DELETE FROM AGENDA_DB WHERE AGENDA_DB.ID = ?", (id))
        print(id)
        self.c.execute("""DELETE FROM AGENDA_DB WHERE id = ?""", (id,))
        #delete from AGENDA_DB where AGENDA_DB.id = 77
        self.conn.commit()


    def searchSpecificData(self,id,nomeBanco):
        self.conn = sqlite3.connect(nomeBanco)
        self.c = self.conn.cursor()
        self.c.execute("SELECT * FROM AGENDA_DB WHERE id=?",(id,))
        saida = self.c.fetchone()
        tratado = '\n'+str(saida[3])+' esta marcado para '+str(saida[1])+' as '+str(saida[2])
        return tratado


