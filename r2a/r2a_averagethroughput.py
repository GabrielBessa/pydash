from r2a.ir2a import IR2A
from player.parser import *
import time
from statistics import mean

from base.whiteboard import Whiteboard


class R2A_AverageThroughput(IR2A):

    def __init__(self, id):
        IR2A.__init__(self, id)
        #self.throughputs = []
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

    def handle_xml_request(self, msg):
        self.request_time = time.perf_counter()
        self.send_down(msg)

    def handle_xml_response(self, msg):

        parsed_mpd = parse_mpd(msg.get_payload())
        self.qi = parsed_mpd.get_qi()


        t = time.perf_counter() - self.request_time

        #self.throughputs.append(msg.get_bit_length() / t)

        self.vazao = msg.get_bit_length() / t

        

        self.send_up(msg)

    def handle_segment_size_request(self, msg):
        self.buffer.append(self.whiteboard.get_amount_video_to_play())

        print(f"BUFFER {self.buffer}\n")
        print(f"VAZAO {self.vazao} ===================================================\n")

        self.request_time = time.perf_counter()

        if not self.flag:
            self.inicio += 1
            for i in self.qi:
                if (self.vazao * 0.4) > i:
                    self.selected_qi = i
            if self.inicio == 20:
                self.flag = True

        if self.flag:
            tam = len(self.buffer)
            self.estabilidade += 1
            if self.vazao >= self.selected_qi and (self.estabilidade >= 5) and self.pior_caso == False:
                self.estabilidade = 0
                if tam > 1:
                    if self.buffer[-1] > self.buffer[-2] or self.buffer[-1] >= 10:
                        self.libera_aumento = True

                    if self.libera_aumento:
                        if self.buffer[-1] > self.buffer[-2] or self.vazao > self.selected_qi * 2:
                            pos = self.qi.index(self.selected_qi)
                            self.selected_qi = self.qi[pos+4]
                        
                        if self.buffer[-1] >= 15 or self.vazao > self.selected_qi * 1.5:
                            pos = self.qi.index(self.selected_qi)
                            self.selected_qi = self.qi[pos+2]

                    if self.buffer[-1] <= 5:
                        self.libera_aumento = False
                        self.selected_qi = self.qi[2]
                
            else:
                if self.buffer[-1] <= 2:
                    self.libera = False
                    self.selected_qi = self.qi[1]
                    #self.pior_caso = True
                else:
                    if self.buffer[-1] <= 4:
                        self.libera = False
                        self.selected_qi = self.qi[2]
                        #self.pior_caso = True
                    else:
                        if self.buffer[-1] <= 6:
                            self.libera = False
                            self.selected_qi = self.qi[4]
                        else:
                            if self.buffer[-1] <= 7:
                                self.libera = False
                                self.selected_qi = self.qi[5]
                # if self.buffer[-1] >= 12:
                #     self.pior_caso = False
                
        self.soma_qi = self.soma_qi + self.qi.index(self.selected_qi)
        self.media = (self.soma_qi) / self.cont
        self.cont += 1

        self.media = "{:.2f}".format(self.media)

        print(f"MEDIA QI: {self.media} ===================================================\n")

        msg.add_quality_id(self.selected_qi)
        self.send_down(msg)

    def handle_segment_size_response(self, msg):
        t = time.perf_counter() - self.request_time

        #self.throughputs.append(msg.get_bit_length() / t)

        self.vazao = msg.get_bit_length() / t

        self.send_up(msg)

    def initialize(self):
        pass

    def finalization(self):
        pass