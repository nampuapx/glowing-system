import socket
import time


# import peak
from peak import Peak
import fx_timeline
from frame_format import frame_format

from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import udp_client
from pythonosc import osc_message_builder

from threading import Thread

LOCALHOST_IP = "127.0.0.1"
LOCALHOST_OSC_PORT = 56567
LOCALHOST_OSC_PORT_FEEDBACK = 56565

TARGET_IP = '192.168.1.255'
TARGET_UDP_PORT = 19997


class AliveIterator:

    value = 0
    max_val = 0

    def __init__(self, max_val):
        self.value = 0
        self.max_val = max_val

    def value_inc(self):
        self.value = self.value + 1
        self.value = self.value % self.max_val
        return self.value


g_dc_sub = 4

new_pix = False
osc_peak_status = False

new_peak_l = Peak(0, 0, 0, 0)
new_peak_r = Peak(0, 0, 0, 0)


zigzagov = 1
pix_len = (60*5)

fx_timeline = fx_timeline.FxTimeline(pix_len, zigzagov)

# client_service = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_service = udp_client.SimpleUDPClient(LOCALHOST_IP, LOCALHOST_OSC_PORT_FEEDBACK)
'''
OSC callbacks:
'''

def print_peak(unused_addr, args, peak_l, peak_r, red_l, red_r, green_l, green_r, blue_l, blue_r_):
    # print("[{0}] ~ {1}".format(args[0], peak))

    global osc_peak_status
    if not osc_peak_status:
        osc_peak_status = True
        print("OSC peak got")

    global new_peak_l
    global new_peak_r
    global new_pix

    new_pix = True

    new_peak_l.rgb = Peak.byte_normalise(peak_l - g_dc_sub)
    new_peak_l.red = Peak.byte_normalise(red_l - g_dc_sub)
    new_peak_l.green = Peak.byte_normalise(green_l - g_dc_sub)
    new_peak_l.blue = Peak.byte_normalise(blue_l - g_dc_sub)


def dc_sub_set(unused_addr, args, a_dc_sub):
    # print("[{0}] ~ {1}".format(args[0], peak))
    global g_dc_sub
    g_dc_sub = a_dc_sub


def fx_timeline_direction_set(unused_addr, args, direct):
    # print("[{0}] ~ {1}".format(args[0], peak))
    global fx_timeline
    fx_timeline.set_direction(direct)


'''
OSC START
'''
dispatcher = dispatcher.Dispatcher()
dispatcher.map("/peak", print_peak, "peak")
dispatcher.map("/settings/dc_sub", dc_sub_set, "dc_sub")
dispatcher.map("/settings/fx_timeline/direction", fx_timeline_direction_set, "direction")

#   dispatcher.map("/logvolume", print_compute_handler, "Log volume", math.log)
# ip = get_ip('apcli0')
server = osc_server.ThreadingOSCUDPServer((LOCALHOST_IP, LOCALHOST_OSC_PORT), dispatcher)
# server.serve_forever()

thread_OSC_server = Thread(target=server.serve_forever)

thread_OSC_server.start()

client = udp_client.SimpleUDPClient(LOCALHOST_IP, LOCALHOST_OSC_PORT)

'''
OSC END
'''


print("Serving OSC on           {}".format(server.server_address))
print("Serving OSC feed back on {}".format([LOCALHOST_IP, LOCALHOST_OSC_PORT_FEEDBACK]))
print("target_device_addr       {}".format([TARGET_IP, TARGET_UDP_PORT]))

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

iterator256 = AliveIterator(256)


while True:
    if new_pix:
        new_pix = False

        send_payload = fx_timeline.new_peak_f(new_peak_l)

        client.sendto(bytes(frame_format(send_payload)), (TARGET_IP, TARGET_UDP_PORT))
        client_service.send_message("/alive", iterator256.value_inc())
    time.sleep(0.05)


client.close()
