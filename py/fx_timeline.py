
import peak


class FxTimeline:
    direction = None
    payload_pix = []
    zigzag = None
    parts = None
    def __init__(self, pix_len, zigzag):

        self.zigzag = zigzag
        self.parts = 2 * zigzag
        for i in range(pix_len//self.parts):
            self.payload_pix.append(peak.Peak(0, 0, 0, 0))

    def set_direction(self, direction):
        self.direction = direction & 1

    def new_peak_f(self, npeak):
        self.payload_pix.insert(0, peak.Peak(npeak.rgb, npeak.red, npeak.green, npeak.blue))

        self.payload_pix.pop(len(self.payload_pix) - 1)

        send_payload = []

        for dd in range(self.parts):
            if bool(self.direction) ^ bool(self.parts & 1):
                for i in self.payload_pix[::-1]:
                    send_payload.append(i.red)
                    send_payload.append(i.green)
                    send_payload.append(i.blue)

            else:

                for i in self.payload_pix:
                    send_payload.append(i.red)
                    send_payload.append(i.green)
                    send_payload.append(i.blue)

        return send_payload
