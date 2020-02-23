from __future__ import absolute_import

import math
import numpy as np
from scipy import ndimage as ndi
from skimage.measure._regionprops import _RegionProperties
import cc3d
import tqdm

_supported_metrics = [
    'area',
    'bbox_area',
    'convex_area',
    'filled_area']


def _labeling(object_label, connectivity):
    return cc3d.connected_components(object_label, connectivity=connectivity)


def _regionprop_nd(object_label, island_label, metric, cache=True):

    # make the table of prop and its index
    n_object = np.max(object_label) + 1
    n_island = np.max(island_label) + 1

    prop_table = [[] for _ in range(n_object)]
    index_table = [[] for _ in range(n_object)]

    islands = ndi.find_objects(island_label)

    for i, sl in tqdm.tqdm(enumerate(islands), total=len(islands),
                            ncols=80, leave=False, desc='regionprop'):

        if sl is None:
            continue

        props = _RegionProperties(sl,
                                i + 1,
                                island_label,
                                None,
                                cache_active=cache)

        prop = getattr(props, metric)

        start = props.coords[0]
        start = [slice(s, s + 1) for s in start]
        obj = object_label[tuple(start)]
        obj = int(np.squeeze(obj))

        prop_table[obj].append(prop)
        index_table[obj].append(i + 1)

    return prop_table, index_table


def remove_island(object_label, noise_ratio=5., connectivity=6, metric='area', cval=0):

    ret = object_label.copy()
    ret_shape = object_label.shape

    # find the connected components, and measure the area
    if metric not in _supported_metrics:
        raise KeyError('metric should be in (' \
                        + ','.join(_supported_metrics) + ')' )

    island_label = _labeling(object_label, connectivity)
    area_table, index_table = _regionprop_nd(object_label, island_label, metric)

    # remove small islands
    background = []

    for areas, indices in zip(area_table, index_table):

        if len(areas) == 0:
            continue

        areas_sort_ind = np.argsort(areas)[::-1]
        areas = np.asarray(areas)[areas_sort_ind]
        indices = np.asarray(indices)[areas_sort_ind]

        histogram = []
        for i, area in enumerate(areas):
            histogram.extend([i]*area)

        threshold = math.ceil(np.percentile(histogram, 100.0 - noise_ratio))
        background = np.concatenate([background, indices[threshold + 1:]])


    mask = np.in1d(island_label.ravel(), background)
    mask = mask.reshape(ret_shape)
    ret[mask] = cval

    return ret
