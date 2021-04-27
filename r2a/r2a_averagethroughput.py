from r2a.ir2a import IR2A
from player.parser import *
import time
from statistics import mean

from base.whiteboard import Whiteboard


class R2A_AverageThroughput(IR2A):

    def __init__(self, id):
        IR2A.__init__(self, id)
        self.throughputs = []
        self.request_time = 0
        self.qi = []
        self.buffer = []
        self.flag = False
        self.selected_qi = 46980

        self.cont = 1
        self.media = 0
        self.soma_qi = 0

        self.buff_flag = 0
        self.estabilidade = 0
        self.pior_caso = False
        self.libera_aumento = True
        self.percent = 40 # %
        self.lista_qi_selects = []
        self.limite_bff_baixo = 0
        self.banda_alta = 0
        self.banda_baixa = 0

    def handle_xml_request(self, msg):
        self.request_time = time.perf_counter()
        self.send_down(msg)

    def handle_xml_response(self, msg):

        parsed_mpd = parse_mpd(msg.get_payload())
        self.qi = parsed_mpd.get_qi()

        t = time.perf_counter() - self.request_time

        self.throughputs.append(msg.get_bit_length() / t)

        self.send_up(msg)

    def handle_segment_size_request(self, msg):

        self.buffer.append(self.whiteboard.get_amount_video_to_play())
        print(f"BUFFER {self.buffer}\n")
        
        vazao = "{:.2f}".format(self.throughputs[-1])

        print(f"VAZAO {vazao} 100% ===================================================\n")

        self.request_time = time.perf_counter()

        if not self.flag:
            for i in self.qi:
                if (self.throughputs[-1] * 0.8) > i:
                    self.selected_qi = i
            self.flag = True

        if self.flag:
            tam_buff = len(self.buffer)
            tam_through = len(self.throughputs)

            if tam_through > 1:
                if self.throughputs[-1] < self.throughputs[-2]:
                    self.percent = (100 * self.throughputs[-1]) / self.throughputs[-2]
                    # Porcentagem da banda, em relação a anterior. Se ela for menor
            
            if self.percent >= 70: # %
                self.banda_alta += 1
            
            if tam_buff > 1:
                if self.buffer[-1] > self.buffer[-2] and self.banda_alta >= 6:
                    self.banda_alta = 0
                    pos = self.qi.index(self.selected_qi)
                    self.selected_qi = self.qi[pos+1]
                    self.estabilidade = 1

            
            if (self.throughputs[-1] * 0.6) >= self.selected_qi and (self.estabilidade == 1) and self.percent >= 40 and not self.pior_caso:
                self.estabilidade = 0
                if tam_buff > 1:
                    if self.buffer[-1] > self.buffer[-2] or self.buffer[-1] >= 12:
                        self.libera_aumento = True

                    if self.libera_aumento:
                        if self.buffer[-1] > self.buffer[-2]:
                            self.buff_flag += 1
                            if self.buff_flag == 3:
                                self.buff_flag = 0
                                pos = self.qi.index(self.selected_qi)
                                self.selected_qi = self.qi[pos+1]
                        else:
                            if self.buff_flag > 0:
                                self.buff_flag -= 1
                        
                        if self.buffer[-1] > self.buffer[-2] and self.buffer[-1] > 30:
                            pos = self.qi.index(self.selected_qi)
                            self.selected_qi = self.qi[pos+1]
                
            else:
                if tam_buff > 1:
                    if self.buffer[-1] <= 4 and self.buffer[-1] < self.buffer[-2]:
                        self.libera = False
                        self.selected_qi = self.qi[0]
                        self.pior_caso = True
                        self.limite_bff_baixo += 1
                    
                    if self.buffer[-1] >= 6:
                        self.pior_caso = False
                
                if self.percent <= 25: # %
                    self.banda_baixa += 1

                if self.banda_baixa >= 3:
                    self.banda_baixa = 0
                    pos = self.qi.index(self.selected_qi)
                    if pos > 0:
                        self.selected_qi = self.qi[pos-1]
                    else:
                        self.selected_qi = self.qi[0]
        
        self.soma_qi = self.soma_qi + self.qi.index(self.selected_qi)
        self.media = (self.soma_qi) / self.cont
        self.cont += 1

        self.media = "{:.2f}".format(self.media)

        self.lista_qi_selects.append(self.qi.index(self.selected_qi))

        print(f"MEDIA QI: {self.media} ||||||| BUFFER PERTO DE ZERO: {self.limite_bff_baixo} vzs ============\n")
        print(f"QUALIDADES SELECIONADAS: {self.lista_qi_selects}\n")

        msg.add_quality_id(self.selected_qi)
        self.send_down(msg)

    def handle_segment_size_response(self, msg):
        t = time.perf_counter() - self.request_time

        self.throughputs.append(msg.get_bit_length() / t)

        self.throughputs[-1] = msg.get_bit_length() / t

        self.send_up(msg)

    def initialize(self):
        pass

    def finalization(self):
        pass