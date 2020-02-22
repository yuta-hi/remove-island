from __future__ import absolute_import

import math
import numpy as np
from scipy import ndimage as ndi
from skimage.measure._regionprops import _RegionProperties
import cc3d
import tqdm


def _labeling(object_label, connectivity=6):
    return cc3d.connected_components(object_label, connectivity=connectivity)


def _regionprop_1d(object_label, island_label):

    assert object_label.ndim == 1
    assert island_label.ndim == 1

    # make the table of area and its index
    n_object = np.max(object_label) + 1
    n_island = np.max(island_label) + 1

    area_table = [[] for _ in range(n_object)]
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
                                cache_active=False)

        area = props.area
        start = sl[0].start
        obj = object_label[start]

        area_table[obj].append(area)
        index_table[obj].append(i + 1)

    return area_table, index_table


def remove_island(object_label, noise_ratio=5., connectivity=6):

    # find the connected components
    island_label = _labeling(object_label, connectivity)

    # reshape to support both 2D and 3D array
    object_label = object_label.ravel()

    ret = object_label.copy()
    ret_shape = island_label.shape

    island_label = island_label.ravel()

    # measure the area
    area_table, index_table = _regionprop_1d(object_label, island_label)

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
            histogram = np.concatenate([histogram, [i]*area])

        threshold = math.ceil(np.percentile(histogram, 100.0 - noise_ratio))
        background = np.concatenate([background, indices[threshold + 1:]])

    mask = np.in1d(island_label, background)
    ret[mask] = 0

    return ret.reshape(ret_shape)
