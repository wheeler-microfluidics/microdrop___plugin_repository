from itertools import izip


def unique(items, key=None, sort=True):
    '''
    Args
    ----

        items (list-like) : List of items.
        key (function) : Returns key for item (defaults to identity).
        sort (bool) : Implementation requires `items` to be sorted. By default,
            `items` is automatically sorted.  Setting `sort=False` implies
            `items` list is already sorted, so sorting can be skipped to
            improve performance.

    Returns
    -------

        (list) : Returns distinct items in `items` list according to `key`,
            and ordered by `key`.
    '''
    if key is None:
        key = lambda v: v
    if sort:
        items = sorted(items, key=key)
    if not items:
        return items
    else:
        return [items[0]] + [i2 for (i1, i2) in izip(items[:len(items)],
                                                     items[1:])
                             if key(i1) != key(i2)]
