#!/usr/bin/env python

from itertools import chain, combinations, permutations
from collections import defaultdict
from math import factorial

class Shapley:
    def __init__(self, vals=None):
        self.players = set()
        self.shapely_vals = None
        if vals:
            self.filled_vals = self.get_filled_vals(vals)
            self.compute_shapley_vals()

    def get_filled_vals(self, vals):
        """Given a dictionary of subset values,
            fill in any missing values according to the get_shapely_value rules.
            Fills in players as a side effect."""
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
        self.players = players
        return fv

    def compute_shapley_vals(self):
        shapley = defaultdict(float)
        players = self.players
        vals = self.filled_vals

        for combo in permutations(players):
            for ii, elm in enumerate(combo):
                player = combo[ii]
                if ii == 0:
                    shapley[player] += vals[frozenset([player])]
                else:
                    prev_players = combo[0:ii]
                    cur_players = combo[0:ii + 1]
                    shapley[player] += vals[frozenset(cur_players)] - vals[frozenset(prev_players)]

        div = factorial(len(players))
        for player in shapley.keys():
            shapley[player] = shapley[player]/div

        self.shapley_vals = shapley


    def get_shapley_values(self):
        return self.shapley_vals



def get_shapley_values(vals):
    """Given a dictionary of values of subsets of players, calculate the shapely value for
       each player. The key of vals is a (frozen) set or tuple of player identifiers,
       the value is the value for that subset of
       players. The code will fill in values for subsets not given according to the following rules:
       For any subset not specified, the value is the highest valued subset which is specified.
       If a value for a solo player is not given assign zero."""
    vals, players = _filled_vals(vals)
    shapley = defaultdict(float)

    for combo in permutations(players):
        for ii, elm in enumerate(combo):
            player = combo[ii]
            if ii == 0:
                shapley[player] += vals[frozenset([player])]
            else:
                prev_players = combo[0:ii]
                cur_players = combo[0:ii + 1]
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
    return fv, players

def voting_shapley(vals):
    """Find the shapely power for the simplified case where all players have a voting power and majority wins.
       Vals is a dict identifier: votes"""
    # For this function to be useful the voters have to be grouped into types with the same voting power.
    # we will identify the types just with ints
    types = defaultdict(list) # key = type, val = original players of that type
    powers = dict() # key = type, val = power of that type
    ipower = dict() # inverse of power. key = power, val = type
    newtype = 0
    total = 0 # total voting power
    for key in vals.keys():
        power = val[key]
        total += power
        if power in ipower:
            type_ = ipower[power]
            types[type_].append(key)
        else:
            powers[newtype] = power
            ipower[power] = newtype
            types[newtype].append(key)
            newtype += 1


    pass


def powerset(iterable):
    """From itertools documentation"""
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))
