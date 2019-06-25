import socket
import time


import peak
import fx_timeline
from frame_format import frame_format

from pythonosc import dispatcher
from pythonosc import osc_server
from threading import Thread

g_dc_sub = 4

new_pix = False
osc_peak_status = False

new_peak = peak.Peak(0, 0, 0, 0)

zigzagov = 10
pix_len = (60*5)

fx_timeline = fx_timeline.fx_timeline_c(pix_len, zigzagov)

'''
OSC callbacks:
'''

def print_peak(unused_addr, args, peak, red, green, blue):
    # print("[{0}] ~ {1}".format(args[0], peak))
    global osc_peak_status
    if not osc_peak_status:
        osc_peak_status = True
        print("OSC peak got")
    global new_peak
    global new_pix
    new_pix = True

    new_peak.rgb = new_peak.byte_normalise(peak - g_dc_sub)
    new_peak.red = new_peak.byte_normalise(red - g_dc_sub)
    new_peak.green = new_peak.byte_normalise(green - g_dc_sub)
    new_peak.blue = new_peak.byte_normalise(blue - g_dc_sub)


def dc_sub_set(unused_addr, args, a_dc_sub):
    # print("[{0}] ~ {1}".format(args[0], peak))
    global g_dc_sub
    g_dc_sub = a_dc_sub

def fx_timeline_direction_set(unused_addr, args, direct):
    # print("[{0}] ~ {1}".format(args[0], peak))
    global fx_timeline
    fx_timeline.set_direction(direct)


localhost_ip = "127.0.0.1"
localhost_OSC_port = 56567

'''
OSC START
'''
dispatcher = dispatcher.Dispatcher()
dispatcher.map("/peak", print_peak, "peak")
dispatcher.map("/settings/dc_sub", dc_sub_set, "dc_sub")
dispatcher.map("/settings/fx_timeline/direction", fx_timeline_direction_set, "direction")

#   dispatcher.map("/logvolume", print_compute_handler, "Log volume", math.log)
# ip = get_ip('apcli0')
server = osc_server.ThreadingOSCUDPServer((localhost_ip, localhost_OSC_port), dispatcher)
print("Serving OSC on {}".format(server.server_address))
# server.serve_forever()

thread_OSC_server = Thread(target=server.serve_forever)

thread_OSC_server.start()
'''
OSC END
'''


target_ip = '192.168.1.133'
target_udp_port = 19997



client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


while True:
    if new_pix:
        new_pix = False

        send_payload = fx_timeline.new_peak_f(new_peak)

        client.sendto(bytes(frame_format(send_payload)), (target_ip, target_udp_port))

    time.sleep(0.05)


client.close()
