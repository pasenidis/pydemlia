import binascii
from functools import reduce, total_ordering
from typing import List

@total_ordering
class UID:
    ID_LENGTH = 20  # 160 bits

    def __init__(self, key: str = None, bid: bytes = None):
        if key:
            if len(key) != UID.ID_LENGTH * 2:
                raise ValueError(
                    f"Node ID is not correct length, given string is {len(key)} chars, required {UID.ID_LENGTH * 2} chars"
                )
            self.bid = bytes(int(key[i:i + 2], 16) for i in range(0, len(key), 2))
        elif bid:
            if len(bid) != UID.ID_LENGTH:
                raise ValueError(f"Key must be {UID.ID_LENGTH} bytes")
            self.bid = bid
        else:
            raise ValueError("Either `key` or `bid` must be provided")

    def get_distance(self, k: 'UID') -> int:
        return (UID.ID_LENGTH * 8) - self.xor(k.bid).get_first_set_bit_index()

    def xor(self, k: bytes) -> 'UID':
        if len(k) != UID.ID_LENGTH:
            raise ValueError(f"Key must be {UID.ID_LENGTH} bytes")
        distance = bytes(b1 ^ b2 for b1, b2 in zip(self.bid, k))
        return UID(bid=distance)

    def get_first_set_bit_index(self) -> int:
        prefix_length = 0
        for byte in self.bid:
            if byte == 0:
                prefix_length += 8
            else:
                for i in range(7, -1, -1):
                    if (byte & (1 << i)) == 0:
                        prefix_length += 1
                    else:
                        return prefix_length
                break
        return prefix_length

    def generate_node_id_by_distance(self, distance: int) -> 'UID':
        result = bytearray(UID.ID_LENGTH)

        # Calculate byte and bit offsets
        num_byte_zeroes = ((UID.ID_LENGTH * 8) - distance) // 8
        num_bit_zeroes = (8 - distance % 8) % 8

        # Fill with zero bytes up to the required distance
        for i in range(num_byte_zeroes):
            result[i] = 0

        # Fill the remaining byte with the correct bit pattern
        if num_byte_zeroes < UID.ID_LENGTH:
            for i in range(8):
                if i >= num_bit_zeroes:
                    result[num_byte_zeroes] |= (1 << (7 - i))

        # Fill the rest with max byte values
        for i in range(num_byte_zeroes + 1, UID.ID_LENGTH):
            result[i] = 0xFF

        return self.xor(result)

    def get_bytes(self) -> bytes:
        return self.bid

    def get_int(self) -> int:
        return int.from_bytes(self.bid, byteorder="big")

    def get_binary(self) -> str:
        return ''.join(f'{byte:08b}' for byte in self.bid)

    def get_hex(self) -> str:
        return binascii.hexlify(self.bid).decode('utf-8').upper()

    def __hash__(self) -> int:
        def xor_reduce(array: List[int]):
            return reduce(lambda x, y: x ^ y, array, 0)

        return ((xor_reduce(self.bid[0:5]) & 0xFF) << 24) | \
               ((xor_reduce(self.bid[5:10]) & 0xFF) << 16) | \
               ((xor_reduce(self.bid[10:15]) & 0xFF) << 8) | \
               (xor_reduce(self.bid[15:20]) & 0xFF)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UID):
            return False
        return self.bid == other.bid

    def __str__(self) -> str:
        parts = [
            binascii.hexlify(self.bid[:3]).decode('utf-8'),
            binascii.hexlify(self.bid[3:19]).decode('utf-8'),
            binascii.hexlify(self.bid[19:]).decode('utf-8')
        ]
        return f"{parts[0]} {parts[1]} {parts[2]}"
