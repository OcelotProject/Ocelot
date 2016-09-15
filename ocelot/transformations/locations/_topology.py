# -*- coding: utf-8 -*-
import functools
import json
import os


class Topology(object):
    fp = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        "..", "..", "data", "faces.json"
    )

    compatibility = [
        ('IAI Area 1', "IAI Area 1, Africa"),
        ('IAI Area 3', "IAI Area 3, South America"),
        ("IAI Area 4&5 without China", 'IAI Area 4&5, without China'),
        ('IAI Area 8', "IAI Area 8, Gulf"),
    ]

    def __init__(self):
        self.data = {key: set(value) for key, value in
                     json.load(open(self.fp, encoding='utf-8'))['data']}
        for old, fixed in self.compatibility:
            self.data[old] = self.data[fixed]

    @functools.lru_cache(maxsize=512)
    def contained(self, location):
        if location in ('GLO', 'RoW'):
            return set()
        faces = self(location)
        return {key
                for key, value in self.data.items()
                if not value.difference(faces)}

    def contains(self, parent, child):
        """Return boolean of whether ``parent`` contains ``child``"""
        return child in self.contained(parent)

    @functools.lru_cache(maxsize=512)
    def intersects(self, location):
        if location in ('GLO', 'RoW'):
            return set()
        faces = self(location)
        return {key
                for key, value in self.data.items()
                if value.intersection(faces)}

    def overlaps(self, group):
        """Return a boolean if any elements in ``group`` overlap each other"""
        if not group:
            return None
        faces = [self(obj) for obj in group]
        return len([o for f in faces for o in f]) != len(set.union(*faces))

    def __call__(self, location):
        if location in ('GLO', 'RoW'):
            return set()
        return self.data[location]
