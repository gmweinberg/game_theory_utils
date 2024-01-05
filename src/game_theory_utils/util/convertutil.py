#!/usr/bin/env python
"""Utilities for converting formats"""

__all__ = ('tuple_from_dict', 'list2', 'tuple2')

def tuple_from_dict(dict):
    """Create a tuple from a dictionary"""
    return tuple(sorted([(elm, dict[elm]) for elm in dict], key=lambda x: x[0]))

def list2(atuple):
    """Convert a tuple of 2 element tuples into a list of lists."""
    return [[elm[0], elm[1]] for elm in atuple]

def tuple2(alist):
    """Convert a list of 2 element lists into a tuple of tuples."""
    return tuple([(elm[0], elm[1]) for elm in alist])




