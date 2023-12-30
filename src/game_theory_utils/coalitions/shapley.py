#!/usr/bin/env python

from itertools import chain, combinations, permutations
from collections import defaultdict
from math import factorial
import random
from game_theory_utils.util import (powerset, distinct_permutations, sequence_counts, sequence_from_types)

class Shapley:
    def __init__(self, vals=None):
        self.coalition_valuation = None # function giving the value of a coalition
        self.player_type= None # dict giving counts of players of each type
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

    def set_player_types(self,  player_types):
        """Set dictionary fiving counts of player types."""
        self.player_types = player_types

    def set_coalition_valuation(self, fun):
        """Set the valuation function for coalations. The function should take a dict
           of type:count as an input and return a float."""

        self.coalition_valuation = fun

    def set_voting_powers(self, player_types, type_strength):
        """A specific coalation value structure such that a coalition wth more than
           half the total voting strength has a coaltion value of 1, and less than or equal
           has a value of zero."""
        self.set_player_types(player_types)
        total = sum([player_types[player] * type_strength[player] for player in player_types])
        crit = total / 2
        strength = lambda player_counts: sum([player_counts[player] * type_strength[player] for player in player_counts])
        fun = lambda player_counts: int(strength(player_counts) > crit)
        self.set_coalition_valuation(fun)

    def  compute_shapley_vals2(self):
        shapley = defaultdict(float)
        perms = 0.0
        for combo in distinct_permutations(self.player_types):
            perms += 1.0
            for ii, player in enumerate(combo):
                if ii == 0:
                    oldval = 0
                    continue
                counts = sequence_counts(combo[0:ii])
                newval = self.coalition_valuation(counts)
                shapley[player] += newval - oldval
                oldval = newval
        for player in shapley.keys():
            shapley[player] = shapley[player]/(perms * self.player_types[player])

        self.shapley_vals = dict(shapley)

    def simulate_shapley_values(self, perms):
        """Get approximate shapley values by looking at random permutations."""
        shapley = defaultdict(float)
        combo = sequence_from_types(self.player_types)
        for jj in range(perms):
            random.shuffle(combo)
            for ii, player in enumerate(combo):
                if ii == 0:
                    oldval = 0
                    continue
                counts = sequence_counts(combo[0:ii])
                newval = self.coalition_valuation(counts)
                shapley[player] += newval - oldval
                oldval = newval
        for player in shapley.keys():
            shapley[player] = shapley[player]/(perms * self.player_types[player])

        self.shapley_vals = dict(shapley)


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

