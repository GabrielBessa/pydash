# import math
# import time
# from r2a.ir2a import IR2A
# from player.parser import *
# from base.whiteboard import Whiteboard


# class R2A_Knn(IR2A):

#     # download_time = video quality / throughput

#     def __init__(self, id):
#         IR2A.__init__(self, id)
#         self.throughputs  = []
#         self.request_time = 0

#     def handle_xml_request(self, msg):
#         self.request_time = time.perf_counter() # Inicializa o timer com o request
#         self.send_down(msg)

#     def handle_xml_response(self, msg):
        
#         t = time.perf_counter() - self.request_time
#         self.throughputs.append(msg.)
#         self.send_up(msg)

#     def handle_segment_size_request(self, msg):
#         self.send_down(msg)


#     def handle_segment_size_response(self, msg):
#         self.send_up(msg)

#     def initialize(self):
#         pass

#     def finalization(self):
#         pass