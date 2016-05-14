# -*- coding: utf-8 -*-
from .locations import relabel_global_to_row


def dummy_transform(data, report):
    """This is a dummy transform that doesn't do anything.

    Used primarily for testing."""
    return data
