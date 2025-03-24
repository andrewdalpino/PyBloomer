import mmh3
import numpy as np

from nptyping import NDArray

MAX_32_BIT_UNSIGNED_INTEGER = 4294967295


class BloomFilter(object):
    """
    A probabilistic data structure that estimates the prior occurrence
    of a given item with a maximum false positive rate.
    """

    MAX_HASH_DIGEST = MAX_32_BIT_UNSIGNED_INTEGER

    MAX_SLICE_SIZE = MAX_HASH_DIGEST

    MAX_HASH_FUNCTIONS = MAX_SLICE_SIZE // 2

    def __init__(
        self,
        max_false_positive_rate: float = 0.01,
        num_hashes: int = 4,
        layer_size: int = 32000000,
    ) -> None:

        if max_false_positive_rate < 0.0 or max_false_positive_rate > 1.0:
            raise ValueError(
                f"Max false positive rate must be between 0 and 1, {max_false_positive_rate} given."
            )

        if num_hashes < 1 or num_hashes > self.MAX_HASH_FUNCTIONS:
            raise ValueError(
                f"Num hashes must be between 1 and {self.MAX_HASH_FUNCTIONS}, {num_hashes} given."
            )

        if layer_size < num_hashes:
            raise ValueError(
                f"Layer size must be greater than {num_hashes}, {layer_size} given."
            )

        slice_size = layer_size // num_hashes

        if slice_size > self.MAX_SLICE_SIZE:
            raise ValueError(
                f"Slice size must be less than {self.MAX_SLICE_SIZE}, {slice_size} given."
            )

        max_bits_per_layer = round(
            layer_size * max_false_positive_rate ** (1 / num_hashes)
        )

        self._max_false_positive_rate = max_false_positive_rate
        self._num_hashes = num_hashes
        self._layer_size = layer_size
        self._slice_size = slice_size
        self._layers: list[NDArray] = []
        self._max_bits = 0
        self._max_bits_per_layer = max_bits_per_layer
        self._n = 0
        self._m = 0

        self._add_layer()

    @property
    def max_false_positive_rate(self) -> float:
        return self._max_false_positive_rate

    @property
    def num_hashes(self) -> int:
        return self._num_hashes

    @property
    def layer_size(self) -> int:
        return self._layer_size

    @property
    def layers(self) -> list[NDArray]:
        return self._layers

    @property
    def num_layers(self) -> int:
        return len(self._layers)

    @property
    def n(self) -> int:
        """Return the number of items currently stored in the filter."""
        return self._n

    @property
    def m(self) -> int:
        """Return the maximum number of bits that can be stored in the filter."""
        return self._m

    @property
    def utilization(self) -> float:
        """Return the proportion of bits that are currently set."""
        return self._n / self._m

    @property
    def capacity(self) -> float:
        """Return the proportion of bits that are currently not set."""
        return 1.0 - self.utilization

    @property
    def false_positive_rate(self) -> float:
        """Return the estimated probability of recording a false positive."""
        return self.utilization**self._num_hashes

    def insert(self, token: str) -> None:
        """Insert a token into the filter."""

        offsets = self._hash(token)

        layer = self._layers[-1]

        changed = False

        for offset in offsets:
            if not layer[offset]:
                layer[offset] = True

                self._n += 1

                changed = True

        if changed and self._n >= self._max_bits:
            self._add_layer()

    def exists(self, token: str) -> bool:
        """Does the given token exist within the filter?"""

        offsets = self._hash(token)

        for layer in self._layers:
            hits = 0

            for offset in offsets:
                if not layer[offset]:
                    break

                hits += 1

            if hits == self._num_hashes:
                return True

        return False

    def exists_or_insert(self, token: str) -> bool:
        """Does the token exist in the filter? If not, then insert it."""

        offsets = self._hash(token)

        for layer in self._layers[:-1]:
            hits = 0

            for offset in offsets:
                if not layer[offset]:
                    break

                hits += 1

            if hits == self._num_hashes:
                return True

        layer = self._layers[-1]

        exists = True

        for offset in offsets:
            if not layer[offset]:
                layer[offset] = True

                self._n += 1

                exists = False

        if not exists and self._n >= self._max_bits:
            self._add_layer()

        return exists

    def _add_layer(self) -> None:
        """Add another layer to the filter."""

        layer = np.zeros(self._layer_size, dtype="bool")

        self._layers.append(layer)

        self._m += self._layer_size
        self._max_bits += self._max_bits_per_layer

    def _hash(self, token: str) -> list[int]:
        """Return a list of filter offsets for a given token."""

        offsets = []

        for i in range(1, self._num_hashes + 1):
            offset = mmh3.hash(token, seed=i, signed=False)

            offset %= self._slice_size
            offset *= i

            offsets.append(int(offset))

        return offsets
