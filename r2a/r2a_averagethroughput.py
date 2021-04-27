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
        self.vazao = 0
        self.buffer = []
        self.flag = False
        self.selected_qi = 46980

        self.cont = 1
        self.media = 0
        self.soma_qi = 0

        self.inicio = 0

        self.estabilidade = 0

        self.pior_caso = False

        self.libera_aumento = True

        self.porcent = 40

        self.pos_list = []

        self.perigo = 0

        self.b_reduct = 0

        self.banda = 0

        self.banda_menos = 0

        self.menor_vazao = 10000000000.00

    def handle_xml_request(self, msg):
        self.request_time = time.perf_counter()
        self.send_down(msg)

    def handle_xml_response(self, msg):

        parsed_mpd = parse_mpd(msg.get_payload())
        self.qi = parsed_mpd.get_qi()


        t = time.perf_counter() - self.request_time

        self.throughputs.append(msg.get_bit_length() / t)

        self.vazao = msg.get_bit_length() / t

        

        self.send_up(msg)

    def handle_segment_size_request(self, msg):
        self.buffer.append(self.whiteboard.get_amount_video_to_play())

        print(f"BUFFER {self.buffer}\n")
        
        vaz = "{:.2f}".format(self.vazao)

        if self.vazao < self.menor_vazao:
            self.menor_vazao = self.vazao
        
        m_vaz = "{:.2f}".format(self.menor_vazao)

        print(f"VAZAO {vaz} ===================================================\n")
        print(f"MENOR VAZAO {m_vaz} ===================================================\n")

        self.request_time = time.perf_counter()

        if not self.flag:
            for i in self.qi:
                if (self.vazao * 0.8) > i:
                    self.selected_qi = i
            
            self.flag = True
            print(f"goooooooooooooooooooo ===================================================\n")

        if self.flag:
            tam = len(self.buffer)
            tam2 = len(self.throughputs)
            if tam2 > 1:
                if self.throughputs[-1] < self.throughputs[-2]:
                    # x% == 100% * 54261[-1] / 619918[-2] == x% = 8.75% == queda 91.25%
                    self.porcent = (100 * self.throughputs[-1]) / self.throughputs[-2]
            if self.porcent >= 70:
                self.banda += 1
            
            if tam > 1:
                if self.buffer[-1] > self.buffer[-2] and self.banda > 6:
                    self.banda = 0
                    pos = self.qi.index(self.selected_qi)
                    self.selected_qi = self.qi[pos+1]
                    self.estabilidade = 1
                    print(f"BANDA +++ ====================================\n")

            
            if (self.vazao * 0.6) >= self.selected_qi and (self.estabilidade == 1) and self.porcent >= 40 and not self.pior_caso:
                print(f"AUMENTAAAAAAAAAAA ===================================================\n")
                self.estabilidade = 0
                if tam > 1:
                    if self.buffer[-1] > self.buffer[-2] or self.buffer[-1] >= 12:
                        self.libera_aumento = True

                    if self.libera_aumento:
                        if self.buffer[-1] > self.buffer[-2]:
                            self.inicio += 1
                            if self.inicio == 3:
                                self.inicio = 0
                                pos = self.qi.index(self.selected_qi)
                                self.selected_qi = self.qi[pos+1]
                                print(f"BUFFER MAIS + ==========================================\n")
                        else:
                            if self.inicio > 0:
                                self.inicio -= 1
                        
                        if self.buffer[-1] > self.buffer[-2] and self.buffer[-1] > 30:
                            pos = self.qi.index(self.selected_qi)
                            self.selected_qi = self.qi[pos+1]
                
            else:
                if tam > 1:
                    if ( self.buffer[-1] <= 4 and self.buffer[-1] < self.buffer[-2] ):
                        self.libera = False
                        self.selected_qi = self.qi[0]
                        self.pior_caso = True
                        self.perigo += 1
                    # else:
                    #     if ( self.buffer[-1] <= 4 and self.buffer[-1] < self.buffer[-2] ):
                    #         self.libera = False
                    #         pos = self.qi.index(self.selected_qi)
                    #         if pos > 1:
                    #             self.selected_qi = self.qi[pos-1]
                    #         else:
                    #             self.selected_qi = self.qi[0]
                        # else:
                        #     if ( self.buffer[-1] <= 6 and self.buffer[-1] < self.buffer[-2] ):
                        #         self.libera = False
                        #         pos = self.qi.index(self.selected_qi)
                        #         if pos > 0:
                        #             self.selected_qi = self.qi[pos-1]
                        #         else:
                        #             self.selected_qi = self.qi[0]
                        #     else:
                        #         if ( self.buffer[-1] <= 10 and self.buffer[-1] < self.buffer[-2] ):
                        #             self.libera = False
                        #             pos = self.qi.index(self.selected_qi)
                        #             if pos > 0:
                        #                 self.selected_qi = self.qi[pos-1]
                        #             else:
                        #                 self.selected_qi = self.qi[0]
                    if self.buffer[-1] >= 6:
                        self.pior_caso = False
                
                if self.porcent <= 25:
                    self.banda_menos += 1

                if self.banda_menos >= 3:
                    self.banda_menos = 0
                    pos = self.qi.index(self.selected_qi)
                    if pos > 0:
                        self.selected_qi = self.qi[pos-1]
                    else:
                        self.selected_qi = self.qi[0]


        # if tam > 1:
        #     if self.buffer[-1] < self.buffer[-2]:
        #         self.b_reduct += 1
        
        # if self.b_reduct == 8:
        #     self.b_reduct = 0
        #     pos = self.qi.index(self.selected_qi)
        #     if pos > 0:
        #         self.selected_qi = self.qi[pos-1]
        #     else:
        #         self.selected_qi = self.qi[0]
                
        self.soma_qi = self.soma_qi + self.qi.index(self.selected_qi)
        self.media = (self.soma_qi) / self.cont
        self.cont += 1

        self.media = "{:.2f}".format(self.media)

        self.pos_list.append(self.qi.index(self.selected_qi))

        print(f"MEDIA QI: {self.media} e PERIGO {self.perigo} e B_REDUCT {self.b_reduct} ============\n")
        print(f"QUALIDADES SELECIONADAS: {self.pos_list}\n")

        msg.add_quality_id(self.selected_qi)
        self.send_down(msg)

    def handle_segment_size_response(self, msg):
        t = time.perf_counter() - self.request_time

        self.throughputs.append(msg.get_bit_length() / t)

        self.vazao = msg.get_bit_length() / t

        self.send_up(msg)

    def initialize(self):
        pass

    def finalization(self):
        pass