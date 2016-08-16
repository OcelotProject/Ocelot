# -*- coding: utf-8 -*-


def same_metadata(first, second):
    """All the metadata except for ``exchanges`` should be the same"""
    for key, value in first.items():
        if key == 'exchanges':
            continue
        else:
            assert key in second and second[key] == value
