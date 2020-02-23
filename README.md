# Remove small islands from multiple-valued label

## Installation
Install from this repository
```bash
git clone https://github.com/yuta-hi/remove-island
cd remove-island
pip install .
```

## Usage
Let's assume that 5% of the object area is noise, and remove them.
```python
from refine_label import remove_island

ret = remove_island(label_3d,
                    noise_ratio=5., #  [0., ..., 100.]
                    connectivity=6, #  [6, 18, 26]
                    metric='area',  #  ['area', 'bbox_area', 'convex_area', 'filled_area']
                    cval=0,
                    only_largest=False)
```
