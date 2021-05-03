""" 
    Gabriel Cunha Bessa Vieira 16/0120811
    Lucas Junior Ribas - 16/0052289
"""

from r2a.ir2a import IR2A
from player.parser import *
import time
from statistics import mean

from base.whiteboard import Whiteboard


class R2A_Dinamico(IR2A):

    def __init__(self, id):
        IR2A.__init__(self, id)

        self.throughputs = []
        self.request_time = 0
        self.qi = []    # lista de qualidades
        self.buffer = [] # lista de buffer
        self.flag = False # auxilia na seleção da primeira qualidade
        self.selected_qi = 46980    # qualidade em QI padrao
        self.media = 0  # media para testes, print
        self.lista_qi_selects = []
        self.limite_bff_baixo = 0   # para testes, para saber se o buffer chegou perto de zero

    def can_upgrade(self, current_throughput, previous_throughputs, current_qi, qi_list):
        # Compara se a vazao atual eh maior que a media das 5 ultimas
        if current_throughput > mean(previous_throughputs[(len(previous_throughputs)-6):-2]):
            # Compara o valor da qualidade atual com as 3 ultimas para ver se pode mandar subir
            if current_qi == mean(qi_list[(len(qi_list)-4):-1]):
                return True
            else:
                return False
        

    def handle_xml_request(self, msg):

        self.request_time = time.perf_counter()
        self.send_down(msg)

    def handle_xml_response(self, msg):

        parsed_mpd = parse_mpd(msg.get_payload())
        self.qi = parsed_mpd.get_qi()
        t = time.perf_counter() - self.request_time
        self.throughputs.append(msg.get_bit_length() / t)   # adiciona a vazao na lista de vazoes
        self.send_up(msg)

    def handle_segment_size_request(self, msg):

        self.buffer.append(self.whiteboard.get_amount_video_to_play()) # armazena o buffer atual na lista de buffer
        print(f"BUFFER {self.buffer}\n")
        
        vazao = "{:.2f}".format(self.throughputs[-1]) # apenas para printar a vazão
        print(f"VAZAO {vazao} 100% ===================================================\n")

        self.request_time = time.perf_counter() # armazena o tempo

        # Flag para controlar qualidade na primeira iteracao
        if not self.flag:                   # com a flag em False, entra apenas uma vez em toda a execução
            self.selected_qi = self.qi[6]   ##          
            self.flag = True                # seta TRUE para nunca mais voltar nesse ponto, usado apenas para setar a primeira qualidade
        # Operacao depois que a primeira qualidade foi setada
        
        if self.flag:                       # agora a flag sempre sera TRUE
            pos = self.qi.index(self.selected_qi)       # armazena a posição Index da qualidade selecionada atualmente
            if pos < 19:    # teste para a posição não passar do tamanho do vetor
                tempo_down_prox = self.qi[pos+1] / self.throughputs[-1]     # tempo necessario para baixar o segmento de video em uma qualidade superior em relação a atual

            min_buffer = 40     # buffer minimo para subir qualidade, quando a posição index da qualidade atual for maior ou igual a 5
            if pos < 5:
                min_buffer = 20 # caso onde a qualidade é menor que 5, o buffer minimo para subir de qualidade se torna 20

            if tempo_down_prox < 0.50 and self.buffer[-1] >= min_buffer:    # se o tempo para baixar o seguimento de video em 1 qualidade acima for menor que 0.5 segundo e se ele tem o buffer minimo para subir de qualidade
                if pos < 19: # teste de segurança, para nao aumentar a qualidade acima do permitido, ha apenas 19 qualidades
                    result = self.can_upgrade(self.throughputs[-1], 
                                                     self.throughputs,
                                                      self.qi.index(self.selected_qi),
                                                        self.lista_qi_selects)
                    # se a funcao retornar True, aumenta a qualidade
                    if result == True:
                        self.selected_qi = self.qi[pos+1] # aumenta a qualidade

            self.temp_dow = self.selected_qi / self.throughputs[-1] # tempo de download do segmento, de acordo com a qualidade atual selecionada

            
            pos = self.qi.index(self.selected_qi) # posiçao index da qualidade atual selecionada
            tam = len(self.buffer) # tamanho da lista de buffer
            if tam > 1: # teste de segurança, para comparar elementos da lista buffer quando ela obtiver pelo menos 2 elementos
                # Comparacao do tempo de download com o tamanho do buffer(19) e os dois ultimos valores do buffer
                if pos > 12:    # se a posição index da qualidade atual selecionada for maior que 12
                    if self.temp_dow > 0.50 and self.buffer[-1] < 20 and (self.buffer[-1] < self.buffer[-2] or self.buffer[-1] <= 5):
                        # se o tempo de download do segmento na qualidade atual selecionada, for maior que 0.5 segundos e o buffer estiver abaixo de 20 e caindo
                        pos = self.qi.index(self.selected_qi) # posiçao index da qualidade atual selecionada
                        if pos > 0:
                            self.selected_qi = self.qi[pos-1] # decremeneta 1 qualidade
                        else:
                            self.selected_qi = self.qi[0] # caso a qualidade seja 1, seta para 0
                else:
                    # Comparacao do tempo de download com o tamanho do buffer(14) e os dois ultimos valores do buffer
                    if pos > 8:     # se a posição index da qualidade atual selecionada for maior que 8
                        if self.temp_dow > 0.50 and self.buffer[-1] < 15 and (self.buffer[-1] < self.buffer[-2] or self.buffer[-1] <= 5):
                            # se o tempo de download do segmento na qualidade atual selecionada, for maior que 0.5 segundos e o buffer estiver abaixo de 15 e caindo
                            pos = self.qi.index(self.selected_qi) # posiçao index da qualidade atual selecionada
                            if pos > 0:
                                self.selected_qi = self.qi[pos-1]   # decremeneta 1 qualidade
                            else:
                                self.selected_qi = self.qi[0] # caso a qualidade seja 1, seta para 0
                    else:
                        # Comparacao do tempo de download com o tamanho do buffer(10) e os dois ultimos valores do buffer
                        if self.temp_dow > 0.50 and self.buffer[-1] < 11 and (self.buffer[-1] < self.buffer[-2] or self.buffer[-1] <= 5):
                            # se o tempo de download do segmento na qualidade atual selecionada, for maior que 0.5 segundos e o buffer estiver abaixo de 11 e caindo
                            pos = self.qi.index(self.selected_qi) # posiçao index da qualidade atual selecionada
                            if pos > 0:
                                self.selected_qi = self.qi[pos-1]   # decremeneta 1 qualidade
                            else:
                                self.selected_qi = self.qi[0] # caso a qualidade seja 1, seta para 0

            print(f"Temp Down: {self.temp_dow} ||| Temp Down Prox: {tempo_down_prox} ================================\n")
            # printa tempo de download do segmento na qualidade atual, e na qualidade superior. ex se estiver na QI 7, printa do tempo de download da QI 7(tem_dow), e da QI 8(tem_down_prox)
        
        self.lista_qi_selects.append(self.qi.index(self.selected_qi)) # armazena a qualidade atual selecionada na lista

        self.media = mean(self.lista_qi_selects)    # media das qualidades selecionadas, para testes em tempo real de execução
        self.media = "{:.2f}".format(self.media)

        tam_bff = len(self.buffer)  # tamanho da lista de buffer
        if tam_bff > 1:# teste de segurança, para comparar elementos da lista buffer quando ela obtiver pelo menos 2 elementos
            if self.buffer[-1] < 3 and self.buffer[-1] < self.buffer[-2]:   # caso o buffer seja menor que 3, ele marca que o buffer chegou perto de zerar
                self.limite_bff_baixo += 1

        print(f"MEDIA QI: {self.media} ||||||| BUFFER PERTO DE ZERO: {self.limite_bff_baixo} vzs ============\n")
        print(f"QUALIDADES SELECIONADAS: {self.lista_qi_selects}\n")
        ## prints de testes, e controle 

        msg.add_quality_id(self.selected_qi) # finalmente, seta a qualidade e da um down na msg
        self.send_down(msg)

    def handle_segment_size_response(self, msg):

        t = time.perf_counter() - self.request_time
        self.throughputs.append(msg.get_bit_length() / t)
        self.send_up(msg)

    def initialize(self):
        pass

    def finalization(self):
        pass