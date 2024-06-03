import socket
import string
import random

from util import Retry, SeqID
from config import Settings

characters = string.ascii_letters + string.digits
retry = Retry(timeout=0.1, retry=2)


class UDPClient:
    def __init__(self, server_ip: str = "127.0.0.1", server_port: int = 8000):
        SeqID.reset()

        self.server_addr = (server_ip, server_port)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def _generate_seq(self) -> str:
        return next(SeqID())

    def _generate_ver(self) -> str:
        return "0" * (Settings.VER_NUM * 8 - 1) + "2"

    def _generate_random_content(self) -> str:
        return "".join(random.choice(characters) for _ in range(Settings.CONTENT))

    def _generate_msg(self, syn: bool, fin: bool):
        msg_to_send = [
            self._generate_seq(),
            self._generate_ver(),
            "0",
            "0",
            self._generate_random_content(),
        ]

        if syn:
            msg_to_send[2] = "1"
        if fin:
            msg_to_send[3] = "1"

        return "".join(msg_to_send)

    @retry.timeout()
    def send(self, syn: bool = False, fin: bool = False) -> str:
        msg_to_send = self._generate_msg(syn, fin).encode(Settings.FORMAT)
        self.client.sendto(msg_to_send, self.server_addr)
        print("Message sent: ", msg_to_send)

        self.client.settimeout(0.1)
        try:
            msg, _ = self.client.recvfrom(Settings.BUFF_SIZE)
            msg = msg.decode(Settings.FORMAT)
        except socket.timeout:
            msg = None

        return msg

    def run(self):
        print("Client starts.")
        self.send(syn=True, fin=False)
        self.send()
        self.send(syn=False, fin=True)
        self.client.close()


client = UDPClient()
client.run()
