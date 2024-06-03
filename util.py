import time

from typing import Callable
from config import Settings


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
                msg = None
                retry_count = self._retry + 1

                while retry_count > 0 and not msg:
                    start = time.time()
                    msg = original_function(*args, **kwargs)
                    end = time.time()
                    while not msg and end - start < self._timeout:
                        end = time.time()
                    retry_count -= 1

                return msg

            return wrapper

        return decorator
