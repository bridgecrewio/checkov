import unittest

from checkov.common.util.array_utils import chunk_array


class TestChunkArray(unittest.TestCase):
    def test_chunk_array_with_empty_input_array(self):
        empty_array = []
        chunks = chunk_array(empty_array, 3)
        self.assertListEqual(chunks, [])

    def test_chunk_array_with_last_chunk_not_full(self):
        input_array = [1, 2, 3, 4, 5, 6, 7]
        chunks = chunk_array(input_array, 3)
        expected_chunks = [[1, 2, 3], [4, 5, 6], [7]]
        self.assertListEqual(chunks, expected_chunks)

    def test_chunk_array_with_two_fully_chunks(self):
        input_array = [1, 2, 3, 4, 5, 6]
        chunks = chunk_array(input_array, 3)
        expected_chunks = [[1, 2, 3], [4, 5, 6]]
        self.assertListEqual(chunks, expected_chunks)
