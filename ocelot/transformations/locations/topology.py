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
                     json.load(open(self.fp))['data']}
        for old, fixed in self.compatibility:
            self.data[old] = self.data[fixed]

    @functools.lru_cache(maxsize=512)
    def contained(self, location):
        if location == 'GLO':
            return
        faces = self.data[location]
        return {key
                for key, value in self.data.items()
                if key != location
                and not value.difference(faces)}

    @functools.lru_cache(maxsize=512)
    def intersects(self, location):
        if location == 'GLO':
            return
        faces = self.data[location]
        return {key
                for key, value in self.data.items()
                if key != location
                and value.intersection(faces)}
