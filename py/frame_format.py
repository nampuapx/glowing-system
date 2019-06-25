
CRC_INIT = 0x1d0f


def crc16_ccitt(crc, data):
    msb = (crc >> 8) & 0xff
    lsb = crc & 0xff
    for c in data:
        x = c ^ msb
        x ^= (x >> 4)
        msb = (lsb ^ (x >> 3) ^ (x << 4)) & 0xff
        lsb = (x ^ (x << 5)) & 0xff
    return (msb << 8) + lsb

def int16_2_bytes(intt):
    return [(intt >> i & 0xff) for i in (0, 8)]


def frame_format(payload):
    return int16_2_bytes(len(payload)) + int16_2_bytes(crc16_ccitt(CRC_INIT, payload)) + payload

