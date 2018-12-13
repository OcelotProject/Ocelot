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
        # Compatability for ecoinvent 3.3
        ('IAI Area, North America, without Quebec', 'IAI Area 2, without Quebec'),
        ('IAI Area, South America', 'IAI Area 3, South America'),
        ('IAI Area, Russia & RER w/o EU27 & EFTA', 'IAI Area, Europe outside EU & EFTA'),
        ('IAI Area, Asia, without China and GCC', 'IAI Area 4&5, without China'),
        ('IAI Area, Gulf Cooperation Council', 'IAI Area 8, Gulf'),
        ('IAI Area, Africa', 'IAI Area 1, Africa'),
    ]

    def __init__(self):
        self.data = {key: set(value) for key, value in
                     json.load(open(self.fp, encoding='utf-8'))['data']}
        for old, fixed in self.compatibility:
            self.data[old] = self.data[fixed]

    def resolve_row(self, others):
        """Resolve a ``RoW`` against specific regions"""
        return self("__all__").difference(
            set.union(*[self(place) for place in others])
        )

    @functools.lru_cache(maxsize=512)
    def contained(self, location, exclude_self=False, subtract=None,
            resolved_row=None):
        if location == 'RoW' and not resolved_row:
            return set()
        elif location == 'RoW':
            faces = resolved_row
        else:
            faces = self(location)

        if subtract:
            faces = faces.difference(set.union(*[self(place) for place in subtract]))
        return {key
                for key, value in self.data.items()
                if not value.difference(faces)
                and not (key == location and exclude_self)}

    def contains(self, parent, child, subtract=None):
        """Return boolean of whether ``parent`` contains ``child``"""
        return child in self.contained(
            parent,
            tuple(subtract) if subtract else None
        )

    def ordered_dependencies(self, datasets):
        locations = {ds['location'] for ds in datasets}
        contained = {loc: self.contained(loc, exclude_self=True).intersection(locations)
                     for loc in locations}
        print("contained", contained)
        ordered = sorted(contained, key=lambda k: (len(contained[k]), k), reverse=True)
        return ordered

    def tree(self, datasets):
        """Construct a tree of containing geographic relationships.

        ``datasets`` is a list of datasets with the ``locations parameter``.

        Returns a list of nested dictionaries like:

            .. code-block:: python

            {
                "GLO": {
                    "Europe": {
                        "Western Europe": {
                            "France": {},
                            "Belgium": {}
                        }
                    }
                }
            }

        ``GLO`` contains all other locations, including ``RoW``. However, ``RoW`` contains nothing.

        Behavior is not defined if the provided locations make a "diamond" shape where "A" contains "B" and "C", which each contain "D".

        """
        for ds in datasets:
            loc = ds['location']
            contained = self.contained(loc, True)

        locations = {x['location'] for x in datasets}
        filtered = lambda lst: {x for x in lst if x in locations}
        contained = {loc: filtered(self.contained(loc, True)) for loc in locations}

        print(locations)

        # Remove redundant links, e.g. A contains B contains C; don't need A -> C.
        for parent, children in contained.items():
            give_up = []
            for brother in children:
                for sister in children:
                    if brother == sister:
                        continue
                    elif brother in contained[sister]:
                        give_up.append(brother)
            for child in give_up:
                children.discard(child)

        children = {elem for lst in contained.values() for elem in lst}
        parents = locations.difference(children).difference({'GLO', 'RoW'})

        # Depth first search
        def add_children(keys):
            return {key: add_children(contained[key]) for key in keys}

        tree = add_children(parents)
        if 'GLO' and 'RoW' in locations:
            tree['GLO']['RoW'] = {}
        elif 'RoW' in locations:
            tree['RoW'] = {}

        return tree

    @functools.lru_cache(maxsize=512)
    def intersected(self, location, exclude_self=False):
        if location in ('GLO', 'RoW'):
            return set()
        faces = self(location)
        return {key
                for key, value in self.data.items()
                if value.intersection(faces)
                and not (key == location and exclude_self)}

    def intersects(self, parent, child):
        """Return boolean of whether ``parent`` contains ``child``"""
        return child in self.intersected(parent)

    def overlaps(self, group):
        """Return a boolean if any elements in ``group`` overlap each other"""
        if not group:
            return None
        faces = [self(obj) for obj in group]
        return len([o for f in faces for o in f]) != len(set.union(*faces))

    def __call__(self, location):
        if location == 'GLO':
            return self.data['__all__']
        elif location == 'RoW':
            return set()
        else:
            return self.data[location]
