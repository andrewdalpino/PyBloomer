# Ok Bloomer
An implementation of the OkBloomer algorithm, an autoscaling [Bloom filter](https://en.wikipedia.org/wiki/Bloom_filter) with ultra-low memory footprint for Python. Ok Bloomer employs a novel layered filtering strategy that allows it to expand while maintaining an upper bound on the false positive rate. As such, Ok Bloomer is suitable for streaming data where the size is not known a priori.

- **Ultra-low** memory footprint
- **Autoscaling** works on streaming data
- **Bounded** maximum false positive rate
- **Open-source** and free to use commercially

### Parameters
| # | Name | Default | Type | Description |
|---|---|---|---|---|
| 1 | max_false_positive_rate | 0.01 | float | The upper false positivity rate bounds. |
| 2 | num_hashes | 4 | int | The number of hash functions used, i.e. the number of slices per layer. |
| 3 | layer_size | 32000000 | int | The size of each layer of the filter in bits. |

### Example

```python
import okbloomer

filter = okbloomer.BloomFilter(
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
- [1] A. DalPino. (2021). OkBloomer, a novel autoscaling Bloom Filter [[link](https://github.com/andrewdalpino/OkBloomer)].
