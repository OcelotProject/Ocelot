# -*- coding: utf-8 -*-
from ocelot.io.ecospold2_meta import REFERENCE_REGULAR_EXPRESSIONS, UUID
import re

test_string = "Ref('b48dfb3c-d9c6-4023-a424-eabcf6141198') Ref('a0d4e28e-d844-430e-8b6c-e62ddbce192f', 'ProductionVolume')  Ref('a0d4e28e-d844-430e-8b6c-e62ddbce192f', 'b48dfb3c-d9c6-4023-a424-eabcf6141198')"

def test_uuid():
    uuid = re.compile(UUID)
    assert uuid.match('b48dfb3c-d9c6-4023-a424-eabcf6141198')
    assert not uuid.match("foo")

def test_references():
    assert REFERENCE_REGULAR_EXPRESSIONS['exchange'].findall(test_string)
    assert REFERENCE_REGULAR_EXPRESSIONS['pv'].findall(test_string)
    assert REFERENCE_REGULAR_EXPRESSIONS['property'].findall(test_string)

    get_list = lambda x: [match.groupdict() for match in x.finditer(test_string)]

    assert get_list(REFERENCE_REGULAR_EXPRESSIONS['exchange']) == [{'uuid': 'b48dfb3c-d9c6-4023-a424-eabcf6141198'}]
    assert get_list(REFERENCE_REGULAR_EXPRESSIONS['pv']) == [{'uuid': 'a0d4e28e-d844-430e-8b6c-e62ddbce192f'}]
    assert get_list(REFERENCE_REGULAR_EXPRESSIONS['property']) == [{
        'first': 'a0d4e28e-d844-430e-8b6c-e62ddbce192f',
        'second': 'b48dfb3c-d9c6-4023-a424-eabcf6141198'
    }]


