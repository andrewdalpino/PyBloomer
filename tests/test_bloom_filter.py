import random
import string

from okbloomer import BloomFilter

from unittest import TestCase


class TestBloomFilter(TestCase):
    def test_instantiate(self):
        filter = BloomFilter(
            max_false_positive_rate=0.001,
            num_hashes=16,
            layer_size=64000,
        )

        self.assertEqual(0.001, filter.max_false_positive_rate)
        self.assertEqual(16, filter.num_hashes)
        self.assertEqual(64000, filter.layer_size)
        self.assertEqual(4000, filter.slice_size)

    def test_insert_and_exists(self):
        filter = BloomFilter()

        self.assertEqual(filter.false_positive_rate, 0)

        self.assertFalse(filter.exists("foo"))

        filter.insert("foo")

        self.assertTrue(filter.exists("foo"))
        self.assertGreater(filter.false_positive_rate, 0)

        self.assertFalse(filter.exists("bar"))

        filter.insert("bar")

        self.assertTrue(filter.exists("bar"))
        self.assertGreater(filter.false_positive_rate, 0)

        self.assertFalse(filter.exists("baz"))

    def test_exists_or_insert(self):
        filter = BloomFilter()

        self.assertFalse(filter.exists_or_insert("foo"))
        self.assertTrue(filter.exists_or_insert("foo"))

        self.assertFalse(filter.exists_or_insert("bar"))
        self.assertTrue(filter.exists_or_insert("bar"))

        self.assertFalse(filter.exists_or_insert("baz"))
        self.assertTrue(filter.exists_or_insert("baz"))

        self.assertFalse(filter.exists_or_insert("qux"))
        self.assertTrue(filter.exists_or_insert("qux"))

    def test_autoscaling(self):
        random.seed(1)

        filter = BloomFilter(
            max_false_positive_rate=0.001,
            num_hashes=4,
            layer_size=320000,
        )

        self.assertEqual(filter.num_layers, 1)

        filter.insert("foo")

        for i in range(0, 100000):
            filter.insert(
                "".join(random.choice(string.ascii_letters) for j in range(20))
            )

        filter.insert("bar")

        self.assertTrue(filter.exists("foo"))
        self.assertTrue(filter.exists("bar"))
        self.assertFalse(filter.exists("baz"))

        self.assertEqual(filter.num_layers, 6)
        self.assertLessEqual(filter.false_positive_rate, 0.001)
        self.assertLessEqual(filter.utilization, 1.0)
        self.assertGreater(filter.capacity, 0.0)

    def test_merge(self):
        a = BloomFilter()
        b = BloomFilter()

        a.insert('foo')
        a.insert('bar')

        b.insert('baz')
        b.insert('qux')

        self.assertTrue(a.exists("foo"))
        self.assertTrue(a.exists("bar"))
        self.assertFalse(a.exists("baz"))
        self.assertFalse(a.exists("qux"))

        self.assertFalse(b.exists("foo"))
        self.assertFalse(b.exists("bar"))
        self.assertTrue(b.exists("baz"))
        self.assertTrue(b.exists("qux"))

        a.merge(b)

        self.assertTrue(a.exists("foo"))
        self.assertTrue(a.exists("bar"))
        self.assertTrue(a.exists("baz"))
        self.assertTrue(a.exists("qux"))

        self.assertEqual(a.num_layers, 1)
