from r2a.ir2a import IR2A
from player.parser import *
import time
from statistics import mean

from base.whiteboard import Whiteboard


class R2A_AverageThroughput(IR2A):

    def __init__(self, id):
        IR2A.__init__(self, id)
        # self.throughputs = []
        self.request_time = 0
        self.qi = []
        self.vazao = 0
        self.buffer = 0

    def handle_xml_request(self, msg):
        self.request_time = time.perf_counter()
        self.send_down(msg)

    def handle_xml_response(self, msg):

        parsed_mpd = parse_mpd(msg.get_payload())
        self.qi = parsed_mpd.get_qi()


        t = time.perf_counter() - self.request_time
        # self.throughputs.append(msg.get_bit_length() / t)

        self.vazao = msg.get_bit_length() / t

        

        self.send_up(msg)

    def handle_segment_size_request(self, msg):
        self.buffer = self.whiteboard.get_amount_video_to_play()

        print(f" BUFFER {self.buffer} ===================================================")
        print(f" VAZAO {self.vazao} ===================================================\n")

        self.request_time = time.perf_counter()

        # avg = mean(self.throughputs) / 2

        self.vazao = self.vazao * 0.4

        if self.buffer > 10:
            self.vazao = self.vazao
            print(f" VAZAO TOTAL ===================================================\n")
        else: 
            if self.buffer > 7:
                self.vazao = self.vazao * 0.8
                print(f" VAZAO 90% ===================================================\n")
            else:
                if self.buffer > 5:
                    self.vazao = self.vazao * 0.7
                    print(f" VAZAO 80% ===================================================\n")
                else:
                    if self.buffer > 2:
                        self.vazao = self.vazao * 0.5
                        print(f" VAZAO 60% ===================================================\n")

        if self.buffer > 40 or self.vazao >= self.qi[19]:
            selected_qi = self.qi[19]
        else:
            if self.buffer > 35 or self.vazao >= self.qi[18]:
                selected_qi = self.qi[18]
            else:
                if self.buffer > 30 or self.vazao >= self.qi[16]:
                    selected_qi = self.qi[16]
                else:
                    if self.buffer > 25 or self.vazao >= self.qi[15]:
                        selected_qi = self.qi[15]
                    else:
                        if self.buffer > 20 or self.vazao >= self.qi[14]:
                            selected_qi = self.qi[14]
                        else:
                            if self.buffer > 15 or self.vazao >= self.qi[12]:
                                selected_qi = self.qi[12]
                            else:
                                selected_qi = self.qi[6]
                                for i in self.qi:
                                    if self.vazao > i:
                                        selected_qi = i


        msg.add_quality_id(selected_qi)
        self.send_down(msg)

    def handle_segment_size_response(self, msg):
        t = time.perf_counter() - self.request_time

        # self.throughputs.append(msg.get_bit_length() / t)

        self.vazao = msg.get_bit_length() / t

        self.send_up(msg)

    def initialize(self):
        pass

    def finalization(self):
        pass