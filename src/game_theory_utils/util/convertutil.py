#!/usr/bin/env python
"""Utilities for converting formats"""

"""For coalitions I frequently want to have a type_counts structure where I want to indicate how
   many of each type I have. This can be expressed as a dict, or a tuple of tuple or a list of lists.
   I find the dict most intuitive, and I need the lists because I need to change the values, but I need the
   tuples when I want to use it as dictionary keys.
   For the tuple I may or may not want to include an element for zero of a type."""

__all__ = ('tuple_from_dict', 'dict_from_tuple', 'list2', 'tuple2', 'insert_zeros', 'remove_zeros', 'get_type_count')

def tuple_from_dict(dict):
    """Create a tuple of tuples from a dictionary"""
    return tuple(sorted([(elm, dict[elm]) for elm in dict], key=lambda x: x[0]))

def dict_from_tuple(atuple):
    """Create a tuple of tuples from a dictionary"""
    return {elm[0]:elm[1] for elm in atuple}

def list2(atuple):
    """Convert a tuple of 2 element tuples into a list of lists."""
    return [[elm[0], elm[1]] for elm in atuple]

def tuple2(alist):
    """Convert a list of 2 element lists into a tuple of tuples."""
    return tuple([(elm[0], elm[1]) for elm in alist])

def insert_zeros(counts_tuple, keys):
    """generate a new tuple with zero counts if it not there already"""
    adict = dict_from_tuple(counts_tuple)
    ml = [(key, adict[key]) if key in adict else (key, 0) for key in keys]
    return tuple(ml)

def remove_zeros(counts_tuple):
    ml = [elm for elm in counts_tuple if elm[1] > 0]
    return tuple(ml)

def get_type_count(counts_tuple, type_):
    """Get the count of a particular type from a counts_tuple"""
    for elm in counts_tuple:
        if elm[0] == type_:
            return elm[1]
    return 0



