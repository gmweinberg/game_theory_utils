#!/usr/bin/env python

from itertools import chain, combinations, permutations
from collections import defaultdict
from math import factorial

players = set()

def get_shapley_values(vals):
    """Given a dictionary of values of subsets of players, calculate the shapely value for
       each player. The key of vals is a (frozen) set or tuple of player identifiers,
       the value is the value for that subset of
       players. The code will fill in values for subsets not given according to the following rules:
       For any subset not specified, the value is the highest valued subset which is specified.
       If a value for a solo player is not given assign zero."""
    global players
    vals = _filled_vals(vals)
    shapley = defaultdict(float)

    for combo in permutations(players):
        sofar = 0
        for ii, elm in enumerate(combo):
            player = combo[ii]
            if ii == 0:
                shapley[player] += vals[frozenset([player])]
            else:
                prev_players = combo[0:ii -1]
                cur_players = combo[0:ii]
                shapley[player] += vals[frozenset(cur_players)] - vals[frozenset(prev_players)]

    div = factorial(len(players))
    for player in shapley.keys():
        shapley[player] = shapley[player]/div

    print('okey doke')
    return shapley

def _frozen_vals(vals):
    """Transform keys from tuples to frozensets"""
    frozen = {}
    for key in vals.keys():
        frozen[frozenset(key)] = vals[key]
    return frozen


def _filled_vals(vals):
    """Given a dictionary of subset values, fill in any missing values according to the get_shapely_value rules"""
    global players
    vals = _frozen_vals(vals)
    players = set()
    for key in vals.keys():
        for elm in key:
             players.add(elm)
    fv = {}
    for elm in powerset(players):
        frozen = frozenset(elm)
        if len(elm) == 0:
            fv[frozen] = 0
        elif frozen in vals:
            fv[frozen] = vals[frozen]
        elif len(frozen) == 1:
            fv[frozen] = 0
        else:
            max_ = None
            s = list(frozen)
            for shorter in combinations(s, len(frozen) - 1):
                new = fv[frozenset(shorter)]
                if max_ is None:
                    max_ = new
                elif new > max_:
                    max_ = new
            fv[frozen] = max_
    return fv

def powerset(iterable):
    """From itertools documentation"""
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))
