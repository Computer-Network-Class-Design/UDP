import time
import re

from typing import Callable
from config import Settings

pattern = re.compile(r"^\d+(\.\d+)*")


class SeqID:
    seq = 0

    @classmethod
    def reset(cls):
        cls.seq = 0

    def __iter__(self):
        return self

    @staticmethod
    def _to_binary(seq_id: int):
        bin_seq_id = bin(seq_id)[2::]
        seq_length = Settings.SEQ_NUM * 8
        if len(bin_seq_id) < seq_length:
            return "0" * (seq_length - len(bin_seq_id)) + bin_seq_id
        return bin_seq_id

    def __next__(self):
        curr = SeqID.seq
        SeqID.seq += 1
        return SeqID._to_binary(curr)


class Retry:
    def __init__(self, timeout: float = 0.1, retry: int = 2):
        self._timeout = timeout
        self._retry = retry

    def timeout(self):
        def decorator(original_function: Callable):
            def wrapper(*args, **kwargs):
                client = args[0]

                msg, resend = None, None
                retry_count = self._retry + 1

                while retry_count > 0 and not msg:
                    start = time.time()

                    msg, send = original_function(*args, **kwargs, resend=resend)
                    if not resend:
                        resend = send

                    end = time.time()
                    while not msg and end - start < self._timeout:
                        end = time.time()
                    retry_count -= 1

                client.packets_to_send += self._retry - retry_count + 1

                if msg:
                    client.packets_received += 1
                    client.round_trip_time.append(end - start)

                    server_time = float(pattern.match(msg[26::]).group(0))
                    if not client.initial_response:
                        client.initial_response = server_time
                    client.final_response = server_time

                    print("Sequence No:".ljust(15), send[:16])
                    print("Server IP:".ljust(15), Settings.IP)
                    print("Server Port:".ljust(15), Settings.PORT)
                    print("RTT:".ljust(15), end - start)
                else:
                    print("Sequence No:".ljust(15), send[:16], "Request time out.")
                    if send[:16] == b"0" * (Settings.SEQ_NUM * 8):
                        raise ConnectionAbortedError("SYN not responded")
                print("- " * 16)

                return msg

            return wrapper

        return decorator
