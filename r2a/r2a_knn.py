from r2a.ir2a import IR2A
from player.parser import *
import time
from statistics import mean
import math
from base.whiteboard import Whiteboard

""" 
Needed equations
8 - bit rate
3- buffer update
4 - reward calculation
7- q(s,a) update
11- q(s,a) update
"""


class R2A_Knn(IR2A):

    # Constants in experiment

    ETA = 0.3
    GAMMA = 0.95
    EPSILON = 0.3
    ALPHA = 50
    BETA = 0.001
    BETA_M = 10 # seconds
    # train eps = 50
    # test = 150
    # steps = 800

    """ Buffering size Update: """
    # BUFFER SIZE:
    # player.py:162 = handle_video_playback
    # player.py:202 = buffering_video_segment

    """ Reward: """

    def __init__(self, id):
        IR2A.__init__(self, id)
        self.throughputs = []
        self.request_time = 0
        self.qi = []

        self.download_time = 0 
        self.arbitrary_qi = 46900 
        self.current_throughput = -1
        self.encoding_rate = 0
    
    def ssim(self, vazao, enc_rate):
        # coeficientes de complexidade de video WTF(?)
        d1 = -0.0101529 
        d2 = 0.0288832
        d3 = -0.0242726 
        d4 = -0.0041539
        ssim_index = (1 + 
                    d1 * pow(math.log10(vazao/enc_rate), 1) +
                    d2 * pow(math.log10(vazao/enc_rate), 2) +
                    d3 * pow(math.log10(vazao/enc_rate), 3) + 
                    d4 * pow(math.log10(vazao/enc_rate), 4))
        
        print(ssim_index) # aqui eh pra retornar dps

    # def reward(self): 
        # R(t) = qt - ALPHA |qt- qt-1| - phi(t) 

    def handle_xml_request(self, msg):
        self.request_time = time.perf_counter()
        self.send_down(msg)

    def handle_xml_response(self, msg):

        parsed_mpd = parse_mpd(msg.get_payload())
        self.qi = parsed_mpd.get_qi()

        t = time.perf_counter() - self.request_time
        self.throughputs.append(msg.get_bit_length() / t)

        print("")
        # print("MSG: ", msg.get_payload(), "\n")
        
        # print("THROUGHPUT: ", self.throughputs)
        # print("BIT LENGTH: ", msg.get_bit_length())
        print("")

        self.send_up(msg)

    def handle_segment_size_request(self, msg):

        print(f"{self.whiteboard.get_amount_video_to_play()} ===================================================")

        self.request_time = time.perf_counter()
        avg = mean(self.throughputs) / 2
        # print("THROUGHPUT: ", self.throughputs)
        # print("AVERAGE: ", avg)


        selected_qi = self.qi[0]
        for i in self.qi:
            # print("QUALITY INSIDE ARRAY: ", i)
            if avg > i:
                selected_qi = i

        msg.add_quality_id(selected_qi)
        self.send_down(msg)

    def handle_segment_size_response(self, msg):
        t = time.perf_counter() - self.request_time
        self.current_throughput = (msg.get_bit_length() / t )
        self.encoding_rate = (msg.get_bit_length()/8)
        self.download_time = self.arbitrary_qi/self.current_throughput
        print("TEMPO DE DOWNLOAD: ", self.download_time)
        print("ENCODING RATE: ", self.encoding_rate)
        self.ssim(self.current_throughput, self.encoding_rate)
        # exit()
        self.throughputs.append(msg.get_bit_length() / t)
        # print("THROUGHPUT: ", self.throughputs)
        # print("BIT LENGTH: ", msg.get_bit_length())

        self.send_up(msg)

    def initialize(self):
        pass

    def finalization(self):
        pass