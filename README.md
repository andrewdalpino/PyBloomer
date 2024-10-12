# PyBloomer
PyBloomer is an implementation of the OkBloomer algorithm, an autoscaling [Bloom filter](https://en.wikipedia.org/wiki/Bloom_filter) with ultra-low memory footprint for Python. It employs a novel layered filtering strategy that allows it to expand while maintaining an upper bound on the false positive rate. Each layer is comprised of a bitmap that remembers the hash signatures of the items inserted so far. If an item gets caught in the filter, then it has probably been seen before. However, if an item passes through the filter, then it definitely has never been seen before.

- **Ultra-low** memory footprint
- **Autoscaling** works on streaming data
- **Bounded** maximum false positive rate
- **Open-source** and free to use commercially

### Parameters
| # | Name | Default | Type | Description |
|---|---|---|---|---|
| 1 | max_false_positive_rate | 0.01 | float | The false positive rate to remain below. |
| 2 | num_hashes | 4 | int | The number of hash functions used, i.e. the number of slices per layer. |
| 3 | layer_size | 32000000 | int | The size of each layer of the filter in bits. |

### Example

```python
import pybloomer

filter = pybloomer.BloomFilter(
    max_false_positive_rate=0.01,
    num_hashes=4,
    layer_size=32000000,
)

filter.insert('foo')

print(filter.exists('foo'))

print(filter.existsOrInsert('bar'))

print(filter.exists('bar'))

print(filter.false_positive_rate())
```

```
True 

False

True

3.906249999999999e-27
```

## References
- [1] A. DalPino. (2021). OkBloomer, a novel autoscaling Bloom Filter for PHP [[link](https://github.com/andrewdalpino/OkBloomer)].
