#!/usr/bin/env python
"""Utility functions for the game theory utils."""

from collections import defaultdict
from itertools import chain, combinations, permutations, repeat

__all__ = ['powerset', 'distinct_permutations', 'sequence_counts', 'sequence_from_types',
           'one_to_max']

def powerset(iterable):
    """From itertools documentation"""
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


def distinct_permutations(counts):
    total = sum([counts[key] for key in counts])
    positions = [ii for ii in range(total)]
    positions = set(positions)
    assigned = {}
    for tresult in _assign_distinct(assigned, positions, counts):
        # reformat from dict to sequence
        result = [None] * total
        for key in tresult.keys():
            for pos in tresult[key]:
                result[pos] = key
        yield result

def _assign_distinct(assigned, positions, counts):
    if len(counts):
        key0 = sorted(counts.keys())[0]
        count = counts[key0]
        tcounts = dict(counts)
        del tcounts[key0]
        for combo in combinations(positions, count):
            npositions = set(positions)
            npositions -= set(combo)
            assigned =  dict(assigned)
            assigned[key0] = combo
            for result in _assign_distinct(assigned, npositions, tcounts):
                    yield result
    else:
        yield assigned

def sequence_counts(iterable):
    """Get a dict indicating the number of times each element in the sequence occurs."""
    counts = defaultdict(int)
    for elm in iterable:
        counts[elm] += 1
    return dict(counts)

def sequence_from_types(type_counts):
    """Given a type_counts dictionary return a list with counts of each type."""
    result = []
    for key in type_counts.keys():
        result.extend([key] * type_counts[key])
    return result

def subtype_coalitions(type_counts):
    """Given a dictionary of types and counts, generate tuples with 0 up to n of each type"""
    keys = sorted([key for key in type_counts])
    for n in range(1, len(keys)):
        for combo in combinations(keys, n):
            pass

def one_to_max(counts):
    """Given a list of tuples, generate tuples with the first element and one to max of the second
       e.g one_to_max(((0,2), (1,3)) will yield 
       ((0,1),(1,1)), ((0,1), (1,2)), ((0,1),(1,3)),
       ((0,2),(1,1)), ((0,2), (2,2)), ((0,2), (2,3)) so six results."""
    pos = [1] * len(counts)
    while pos:
        yield tuple([(counts[iii][0], pos[iii]) for iii in range(len(counts))])
        pos = _one_to_max_next(counts, pos)


def _one_to_max_next(counts, pos):
    """Helper function for one_to_max"""
    lol = 'nope'
    ii = 0
    while ii < len(counts) and pos[ii] == counts[ii][1]:
        ii += 1
    if ii == len(counts): # we are done
        return
    pos[ii] += 1
    for iii in range(ii):
        pos[iii] = 1
    return pos





