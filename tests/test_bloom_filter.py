import unittest

import pybloomer

class TestBloomFilter(unittest.TestCase):
    def test_basic(self):
        filter = pybloomer.BloomFilter(
            max_false_positive_rate=0.01,
            num_hashes=4,
            layer_size=32000000,
        )

        self.assertEqual(filter.false_positive_rate(), 0)

        self.assertFalse(filter.exists('foo'))

        filter.insert('foo')

        self.assertTrue(filter.exists('foo'))
        self.assertGreater(filter.false_positive_rate(), 0)

        self.assertFalse(filter.exists('bar'))

        filter.insert('bar')

        self.assertTrue(filter.exists('bar'))
        self.assertGreater(filter.false_positive_rate(), 0)