#!/usr/bin/env python

from itertools import chain, combinations, permutations
from collections import defaultdict
from math import factorial
import random
from copy import deepcopy
from game_theory_utils.util import (powerset, distinct_permutations, sequence_counts, sequence_from_types,
                                    subtype_coalitions)

class Shapley:
    def __init__(self, vals=None):
        self.coalition_valuation = None # function giving the value of a coalition
        self.player_type= None # dict giving counts of players of each type
        self.players = set()
        self.shapely_vals = None
        self.verbose = False
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
        """Set dictionary giving counts of player types."""
        self.player_types = player_types

    def set_coalition_valuation(self, fun):
        """Set the valuation function for coalations. The function should take a dict
           of type:count as an input and return a float."""

        self.coalition_valuation = fun

    def set_ungrouped_coalition_values(self, coalition_values):
        """Create the player_types dictionary and evaluation function based on
           a dictionary of coalition valuation. The coalition is "ungrouped" in that each
           player is considered to be a separate type, even if in fact they have identical valuations.
           If a valuation for a coalition is not given, 
           assign the valuation of the highest subcoation with a valuation.
           If none of them have valuations, assign zero.
           Keys of coalation values is a tuple listing the coalition members in sorted order."""
        players = set()
        for key in coalition_values.keys():
            for player in key:
                players.add(player)
        player_types = {player:1 for player in players}
        self.set_player_types(player_types)
        vals = {}
        for key in coalition_values:
            nkey = tuple(sorted(list(key)))
            vals[nkey] = coalition_values[key]
        for elm in powerset(players):
            nkey = tuple(sorted(list(elm)))
            if nkey not in vals:
                if len(nkey) in [0, 1]:
                    vals[nkey] = 0
                else:
                    max_ = 0 # No negative values allowed!
                    for shorter in combinations(nkey, len(nkey) - 1):
                        new = vals[shorter]
                        if new > max_:
                            max_ = new
                    vals[nkey] = max_
        fun = lambda player_counts: vals[tuple(sorted([key for key in player_counts]))]
        self.set_coalition_valuation(fun)

    def set_grouped_coalition_values(self, coalition_values, player_types):
        """Create an evaluation function givn the supplied coalition values and player_types,
           filling in missing values with our standard fill-in rules.
           In the case the key for coalition values is nested tuples, with the innermost
           tuple being count of type e.g. ((0, 2), (1,1)) means 1 player pf type 1 and 2
           of tpe 0. Because the order matters we will sort them by type.
        """
        self.player_types = player_types
        vals = deepcopy(coalition_values)
        vals[tuple()] = 0
        all_player_counts = set()
        for player_type in player_types:
            for count in range(1, player_types[player_type] + 1):
                all_player_counts.add((player_type, count))
        for nkey in subtype_coalitions(player_types):
            #nkey = tuple(sorted(list(elm), key=lambda x:x[0]))
            lol = 'nope'
            if nkey not in vals:
                max_ = 0
                # we must compare to all coalitions with a member type deleted,
                # and all coalitions with one fewer of each member type.
                # I think the powerset ordering means we only have to check one member removed at a time,
                # because we will already have checked an entry with more than one entry removed
                ed = {ptc[0]:ptc[1] for ptc in nkey} # elm dict
                for pt in ed:
                    nd = dict(ed)
                    if ed[pt] > 1:
                        nd[pt] = nd[pt] -1
                    else:
                        del nd[pt]
                    ttypes = sorted([key for key in nd])
                    skey = tuple([(key, nd[key]) for key in ttypes])
                    tval = vals[skey]
                    if tval > max_:
                        max_ = tval
                vals[nkey] = max_
        nkf = lambda player_counts: tuple(sorted(tuple([(key, player_counts[key]) for key in player_counts])))
        fun = lambda player_counts: vals[nkf(player_counts)]
        self.set_coalition_valuation(fun)


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
                counts = sequence_counts(combo[0:ii + 1])
                newval = self.coalition_valuation(counts)
                if self.verbose:
                    print('counts', counts, 'ii', ii, newval, oldval)
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
                counts = sequence_counts(combo[0:ii + 1])
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

