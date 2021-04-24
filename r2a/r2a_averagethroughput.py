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
        self.download_time = 0
        self.arbitrary_qi = 46900

    def handle_xml_request(self, msg):
        self.request_time = time.perf_counter()
        self.send_down(msg)

    def handle_xml_response(self, msg):

        parsed_mpd = parse_mpd(msg.get_payload())
        self.qi = parsed_mpd.get_qi()
        #get_mpd_info
        #print(f"{msg.get_payload()} ===================================================")

        t = time.perf_counter() - self.request_time
        self.throughputs.append(msg.get_bit_length() / t)
        print("")
        # print("MSG: ", msg.get_payload(), "\n")
        self.download_time = t/self.arbitrary_qi
        print("TEMPO DE DOWNLOAD: ", self.download_time, "\n")
        # print("THROUGHPUT: ", self.throughputs)
        # print("BIT LENGTH: ", msg.get_bit_length())
        print("")

        self.send_up(msg)

    def handle_segment_size_request(self, msg):

        print(f"{self.whiteboard.get_amount_video_to_play()} ===================================================")

        self.request_time = time.perf_counter()
        avg = mean(self.throughputs) / 2
        print("THROUGHPUT: ", self.throughputs)
        print("AVERAGE: ", avg)


        selected_qi = self.qi[0]
        for i in self.qi:
            print("QUALITY INSIDE ARRAY: ", i)
            if avg > i:
                selected_qi = i

        msg.add_quality_id(selected_qi)
        self.send_down(msg)

    def handle_segment_size_response(self, msg):
        t = time.perf_counter() - self.request_time
        self.throughputs.append(msg.get_bit_length() / t)
        print("THROUGHPUT: ", self.throughputs)
        print("BIT LENGTH: ", msg.get_bit_length())

        self.send_up(msg)

    def initialize(self):
        pass

    def finalization(self):
        pass