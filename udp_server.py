import socket
import random
import datetime

from typing import Tuple

from config import Settings


class UDPServer:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind((Settings.IP, Settings.PORT))

        self.initial_response = self.final_response = None

    @staticmethod
    def __emulate_loss() -> bool:
        return random.random() >= Settings.LOSS

    def _handle_client(self, msg: bytes, addr: Tuple[str, int]):
        def pad_string(s: str) -> str:
            if len(s) < Settings.CONTENT:
                return "".join([s, " " * (Settings.CONTENT - len(s))])
            return s[Settings.CONTENT]

        curr_time = int(datetime.datetime.now().timestamp())

        msg = msg.decode(Settings.FORMAT)
        seq, ver, syn, fin, content = (
            msg[:16],
            msg[16:24],
            int(msg[24]),
            int(msg[25]),
            msg[26::].strip(),
        )

        print("Entering handle client")
        print("seq =", seq, "ver =", ver, "syn =", syn, "fin =", fin)

        if not syn and not self.initial_response:
            self.initial_response = curr_time
        if not syn and not fin:
            self.final_response = curr_time

        if syn:
            msg_to_send = "".join(
                [seq, ver, str(syn), str(fin), pad_string(content)]
            ).encode(Settings.FORMAT)
        elif fin:
            msg_to_send = "".join(
                [seq, ver, str(syn), str(fin), pad_string(Settings.FIN_ACK)]
            ).encode(Settings.FORMAT)
        else:
            msg_to_send = "".join(
                [seq, ver, str(syn), str(fin), pad_string(str(curr_time))]
            ).encode(Settings.FORMAT)

        self.server.sendto(msg_to_send, addr)

        return fin == 1

    def run(self) -> None:
        print(f"Server starts at {Settings.IP} & {Settings.PORT}")
        while True:
            msg, addr = self.server.recvfrom(Settings.BUFF_SIZE)

            print("Message received", msg)
            if UDPServer.__emulate_loss() and self._handle_client(msg, addr):
                break


server = UDPServer()
server.run()
