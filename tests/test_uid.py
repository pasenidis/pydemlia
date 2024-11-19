import unittest
from unittest.mock import patch
from pydemlia.utils.uid import UID

class TestUID(unittest.TestCase):

    def setUp(self):
        # Create a UID for testing
        self.uid = UID(key="1" * 40)  # A 160-bit UID
        self.other_uid = UID(key="2" * 40)

    def test_uid_initialization(self):
        # Create a UID object with a known key
        key = "1" * 40
        self.uid = UID(key=key)

        # The expected output should be the hex string of the UID's bid
        expected_hex = "1" * 40
        self.assertEqual(self.uid.get_hex(), expected_hex)

    def test_get_distance(self):
        # Test XOR distance calculation
        distance = self.uid.get_distance(self.other_uid)
        self.assertIsInstance(distance, int)

    def test_xor(self):
        # Test XOR operation between UIDs
        result = self.uid.xor(self.other_uid.bid)
        self.assertIsInstance(result, UID)

    def test_get_first_set_bit_index(self):
        # Test get_first_set_bit_index method
        index = self.uid.get_first_set_bit_index()
        self.assertIsInstance(index, int)

    def test_generate_node_id_by_distance(self):
        # Test ID generation by distance
        generated_uid = self.uid.generate_node_id_by_distance(10)
        self.assertIsInstance(generated_uid, UID)

    def test_get_bytes(self):
        # Test bytes conversion
        self.assertEqual(self.uid.get_bytes(), bytes.fromhex("1" * 40))

    def test_get_int(self):
        # Test integer conversion
        self.assertEqual(self.uid.get_int(), int("1" * 40, 16))

    def test_get_binary(self):
        # Create a UID object with known key (e.g., 20-byte key)
        key = "01" * 20
        self.uid = UID(key=key)

        expected_binary = "00000001" * 20
        self.assertEqual(self.uid.get_binary(), expected_binary)

    def test_uid_equality(self):
        # Test equality between UIDs
        other_uid = UID(key="1" * 40)
        self.assertEqual(self.uid, other_uid)

    def test_uid_hash(self):
        # Test UID hashing
        self.assertIsInstance(hash(self.uid), int)

if __name__ == '__main__':
    unittest.main()
