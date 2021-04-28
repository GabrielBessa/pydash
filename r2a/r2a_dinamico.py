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
        self.qi = []
        self.buffer = []
        self.flag = False
        self.selected_qi = 46980
        self.media = 0
        self.lista_qi_selects = []
        self.limite_bff_baixo = 0
        self.inicio = 0

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
            self.inicio += 1
            for i in self.qi:
                if self.throughputs[-1] * 0.8 > i:
                    self.selected_qi = i
            if self.inicio == 2:
                self.flag = True

        if self.flag:
            pos = self.qi.index(self.selected_qi)
            if pos < 19:
                tempo_down_prox = self.qi[pos+1] / self.throughputs[-1]

            min_buffer = 30
            if pos < 5:
                min_buffer = 15

            if tempo_down_prox < 0.60 and self.buffer[-1] >= min_buffer:
                if pos < 19:
                    self.selected_qi = self.qi[pos+1]

            self.temp_dow = self.selected_qi / self.throughputs[-1]

            tam_QIs = len(self.lista_qi_selects)
            if tam_QIs > 1:
                pos = self.qi.index(self.selected_qi)
                tam = len(self.buffer)
                if tam > 1:
                    if self.lista_qi_selects[-1] == pos:
                        if pos > 12:
                            if self.temp_dow > 0.70 and self.buffer[-1] < 20 and self.buffer[-1] < self.buffer[-2]:
                                pos = self.qi.index(self.selected_qi)
                                if pos > 0:
                                    self.selected_qi = self.qi[pos-1]
                                else:
                                    self.selected_qi = self.qi[0]
                        else:
                            if pos > 8:
                                if self.temp_dow > 0.70 and self.buffer[-1] < 15 and self.buffer[-1] < self.buffer[-2]:
                                    pos = self.qi.index(self.selected_qi)
                                    if pos > 0:
                                        self.selected_qi = self.qi[pos-1]
                                    else:
                                        self.selected_qi = self.qi[0]
                            else:
                                if self.temp_dow > 0.60 and self.buffer[-1] < 11 and self.buffer[-1] < self.buffer[-2]:
                                    pos = self.qi.index(self.selected_qi)
                                    if pos > 0:
                                        self.selected_qi = self.qi[pos-1]
                                    else:
                                        self.selected_qi = self.qi[0]

            print(f"Temp Down: {self.temp_dow} ||| Temp Down Prox: {tempo_down_prox} ================================\n")

        self.lista_qi_selects.append(self.qi.index(self.selected_qi))

        self.media = mean(self.lista_qi_selects)
        self.media = "{:.2f}".format(self.media)

        tam_bff = len(self.buffer)
        if tam_bff > 1:
            if self.buffer[-1] < 3 and self.buffer[-1] < self.buffer[-2]:
                self.limite_bff_baixo += 1

        print(f"MEDIA QI: {self.media} ||||||| BUFFER PERTO DE ZERO: {self.limite_bff_baixo} vzs ============\n")
        print(f"QUALIDADES SELECIONADAS: {self.lista_qi_selects}\n")
        
        msg.add_quality_id(self.selected_qi)
        self.send_down(msg)

    def handle_segment_size_response(self, msg):

        t = time.perf_counter() - self.request_time
        self.throughputs.append(msg.get_bit_length() / t)
        self.send_up(msg)

    def initialize(self):
        pass

    def finalization(self):
        pass