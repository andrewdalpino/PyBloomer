import unittest
import random
import string

import okbloomer

class TestBloomFilter(unittest.TestCase):
    def test_insert_and_exists(self):
        filter = okbloomer.BloomFilter()

        self.assertEqual(filter.false_positive_rate, 0)

        self.assertFalse(filter.exists('foo'))

        filter.insert('foo')

        self.assertTrue(filter.exists('foo'))
        self.assertGreater(filter.false_positive_rate, 0)

        self.assertFalse(filter.exists('bar'))

        filter.insert('bar')

        self.assertTrue(filter.exists('bar'))
        self.assertGreater(filter.false_positive_rate, 0)

        self.assertFalse(filter.exists('baz'))

    def test_exists_or_insert(self):
        filter = okbloomer.BloomFilter()

        self.assertFalse(filter.exists_or_insert('foo'))

        self.assertTrue(filter.exists_or_insert('foo'))

        self.assertFalse(filter.exists_or_insert('bar'))

        self.assertTrue(filter.exists_or_insert('bar'))

        self.assertFalse(filter.exists_or_insert('baz'))

        self.assertTrue(filter.exists_or_insert('baz'))

    def test_autoscaling(self):
        random.seed(1)

        filter = okbloomer.BloomFilter(
            max_false_positive_rate=0.001,
            num_hashes=4,
            layer_size=320000,
        )

        self.assertEqual(filter.num_layers, 1)

        filter.insert('foo')

        for i in range(0, 100000):
            filter.insert(''.join(random.choice(string.ascii_letters) for j in range(20)))

        filter.insert('bar')

        self.assertEqual(filter.num_layers, 6)
        self.assertLessEqual(filter.false_positive_rate, 0.001)
        self.assertLessEqual(filter.utilization, 1.0)
        self.assertGreater(filter.capacity, 0.0)

        self.assertTrue(filter.exists('foo'))
        self.assertTrue(filter.exists('bar'))
        self.assertFalse(filter.exists('baz'))
