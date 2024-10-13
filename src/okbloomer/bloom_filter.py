import numpy as np
from nptyping import NDArray

class BloomFilter(object):
    """
    A probabilistic data structure that estimates the prior occurrence
    of a given item with a maximum false positive rate. 
    """
    
    MAX_SLICE_SIZE = 2147483647

    def __init__(self,
                max_false_positive_rate: float = 0.01,
                num_hashes: int = 4,
                layer_size: int = 32000000) -> None:

        if max_false_positive_rate < 0.0 or max_false_positive_rate > 1.0:
            raise ValueError(f'Max false positive rate must be between 0 and 1, {max_false_positive_rate} given.')

        if num_hashes < 1:
            raise ValueError(f'Num hashes must be greater than 1, {num_hashes} given.')

        if layer_size < num_hashes:
            raise ValueError(f'Layer size must be greater than {num_hashes}, {layer_size} given.')

        slice_size = int(round(layer_size / num_hashes))

        if slice_size > self.MAX_SLICE_SIZE:
            raise ValueError(f'Slice size must be less than {self.MAX_SLICE_SIZE}, {slice_size} given.')

        self.max_false_positive_rate = max_false_positive_rate
        self.num_hashes = num_hashes
        self.layer_size = layer_size
        self.slice_size = slice_size
        self.layers: list[NDArray] = []
        self.n = 0 # The number of bits currently stored in the filter.
        self.m = 0 # The maximum number of bits that can be stored in the filter.

        self._add_layer()

    @property
    def num_layers(self) -> int:
        return len(self.layers)

    @property
    def utilization(self) -> float:
        """Return the proportion of bits that are currently set"""
        return self.n / self.m

    @property
    def capacity(self) -> float:
        """Return the proportion of bits that are currently not set"""
        return 1.0 - self.utilization

    @property
    def false_positive_rate(self) -> float:
        """Return the probability of recording a false positive"""
        return self.utilization ** self.num_hashes

    def insert(self, token: str) -> None:
        """Insert a token into the filter"""
        offsets = self._hash(token)

        layer = self.layers[-1]

        changed = False

        for offset in offsets:
            if layer[offset] == False:
                layer[offset] = True

                self.n += 1

                changed = True

        if changed and self.false_positive_rate > self.max_false_positive_rate:
            self._add_layer()

    def exists(self, token: str) -> bool:
        """Does the given token exist within the filter?"""
        offsets = self._hash(token)

        for layer in self.layers:
            hits = 0

            for offset in offsets:
                if layer[offset] == False:
                    break

                hits += 1

            if hits == self.num_hashes:
                return True

        return False

    def exists_or_insert(self, token: str) -> bool:
        """Does the token exist in the filter? If not, then insert it."""
        offsets = self._hash(token)

        for layer in self.layers[:-1]:
            hits = 0

            for offset in offsets:
                if layer[offset] == False:
                    break

                hits += 1

            if hits == self.num_hashes:
                return True

        layer = self.layers[-1]

        exists = True

        for offset in offsets:
            if layer[offset] == False:
                layer[offset] = True

                self.n += 1

                exists = False

        if not exists and self.false_positive_rate > self.max_false_positive_rate:
            self._add_layer()

        return exists

    def _add_layer(self) -> None:
        """
        Add another layer to the filter for maintaining the false positivity rate below the threshold.
        """
        self.layers.append(np.zeros(self.layer_size, dtype='bool'))

        self.m += self.layer_size

    def _hash(self, token: str) -> list:
        """Return a list of filter offsets from a given token."""
        offsets = []

        for i in range(1, self.num_hashes + 1):
            offset = hash(f'{i}{token}')

            offset %= self.slice_size
            offset *= i

            offsets.append(int(offset))

        return offsets
