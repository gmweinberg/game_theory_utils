#!/usr/bin/env python
from collections import defaultdict
from math import comb, prod
import random

from game_theory_utils.util.convertutil import (tuple_from_dict, list_from_dict, get_type_count, insert_zeros)
from game_theory_utils.util.iterutil import (zero_to_max, one_less, fill_vals, sequence_from_types,
                                             distinct_permutations, sequence_counts)

__all__ = ('CoalitionalGame', 'create_voting_game', 'create_game_from_unique_players',
           'create_game_from_typed_players')

class CoalitionalGame:
    """A coalitional game is defined as a set of players and a function giving the value of each subset of
      members, cakked a coalition. In this implementation I support the notion of player "types":
      the value of a coalition depends on the number of types of each player.
      If all players are unique, there is just one player of each type.
      I represent the player types as a dict e.g. {'a': 3, 'b', 4 } means there are 3 players of type a and
      4 of type b.
      The coalition valuation function takes a coalition tuple as an input. Internally it will
      usually just be a dictionary lookup with the coalition tupe as a key. The keys must be sorted since
      (('a',3), ('b',4)) and (('b', 4), ('a',3)) are not the same.
    """

    def __init__(self, player_types, coalition_valuation):
        self.player_types = player_types #
        self.coalition_valuation = coalition_valuation # function
        self.verbose = False

        typed = False
        for elm in player_types:
            if player_types[elm] > 1:
                typed = True
                break
        self.typed = typed

        self.simple = None
        self.superadditive = None
        self.monotonic = None
        
        self.shapley_values = None
        self.banzhaf_values = None

    def core_exists(self):
        return False

    def get_valuation(self):
        """Return the valuation as a dictionary.
        This may be prohibitivley large."""
        valuation = {}
        for key in zero_to_max(tuple_from_dict(self.player_types)):
            valuation[key] = self.coalition_valuation(key)
        return valuation

    def get_banzhaf_values(self):
        """Get the banzhaf values. Note that the banzhaf values do not exist unless the game is simple
           (all coalition values are one or zero."""
        if self.banzhaf_values is None:
            self.calculate_banzhaf_values()
        return self.banzhaf_values

    def calculate_banzhaf_values(self):
        """Calculate the banzhaf values. Just changes internal members."""
        bcounts = defaultdict(int) # key is player type, val is number of distinct coalitions
                                   # where adding one of pt earns success
        for atuple in zero_to_max(tuple_from_dict(self.player_types)):
            if self.coalition_valuation(atuple):
                for less, removed in one_less(atuple):
                    if not self.coalition_valuation(less):
                        mult = prod([comb(self.player_types[elm[0]], elm[1]) for elm in less])
                        mult *= (self.player_types[removed] - get_type_count(less, removed))
                        # print(atuple, removed, less, mult)

                        bcounts[removed] += mult
        total = sum([bcounts[pt] for pt in bcounts])
        self.banzhaf_values = {pt:0 for pt in self.player_types} # in case bcount is zero
        for type_ in bcounts:
            self.banzhaf_values[type_] = bcounts[type_] / (total * self.player_types[type_])

    def get_shapley_values(self):
        """Get the shapley values. Calculate them if they have not yet been calculated."""
        if self.shapley_values is None:
            self.calculate_shapley_values()
        return self.shapley_values

    def calculate_shapley_values(self):
        """Compute the shapley values and store them as members."""
        keys = [key for key in self.player_types]
        shapley = defaultdict(float)
        perms = 0.0
        for combo in distinct_permutations(self.player_types):
            oldval = 0
            perms += 1.0
            for ii, player in enumerate(combo):
                counts = sequence_counts(combo[0:ii + 1])
                counts_tuple = insert_zeros(tuple_from_dict(counts), keys)
                newval = self.coalition_valuation(counts_tuple)
                if self.verbose:
                    print('counts', counts, 'counts_tuple', counts_tuple, 'ii', ii, 'newval', newval, 'oldval', oldval)
                shapley[player] += newval - oldval
                oldval = newval
        for player in shapley.keys():
            shapley[player] = shapley[player]/(perms * self.player_types[player])
        self.shapley_values = dict(shapley)

    def simulate_shapley_values(self, perms):
        """Get approximate shapley values by looking at random permutations.
           Returns te approximate values, does not update the shapley_values member."""
        keys = [key for key in self.player_types]
        shapley = defaultdict(float)
        combo = sequence_from_types(self.player_types)
        for jj in range(perms):
            random.shuffle(combo)
            for ii, player in enumerate(combo):
                if ii == 0:
                    oldval = 0
                counts = sequence_counts(combo[0:ii + 1])
                counts_tuple = insert_zeros(tuple_from_dict(counts), keys)
                newval = self.coalition_valuation(counts_tuple)
                shapley[player] += newval - oldval
                oldval = newval
        for player in shapley.keys():
            shapley[player] = shapley[player]/(perms * self.player_types[player])

        return dict(shapley)

    def zero_normalize(self):
        """Create straegically equivalent 0 normalized game. A game is 0 normalized if
           the colaition value is zero for all single-member coalitions. The value of the
           grand coalition will be 1, 0, or -1. Returns the pai (game, v) where
           v is the value of the grand coalition in the new game.
        """
        grand = self.coalition_valuation(tuple_from_dict(self.player_types))
        keys = sorted([key for key in self.player_types])
        offsets = {}
        for ii in range(len(keys)):
            ones = tuple([(keys[iii], 1) if iii == ii else (keys[iii], 0) for iii in range(len(keys))])
            offsets[ii] = self.coalition_valuation(ones)
        offtotal = sum([offsets[key] * self.player_types[key] for key in keys])
        if offtotal < grand:
            newgrand = 1
            scale = 1 / (grand - offtotal)
        elif offtotal > grand:
            newgrand = -1
            scale = 1 / (offtotal - grand)
        else:
            newgrand = 0
            scale = 1 # anz nonzero value should work
        vals = {}
        for atuple in zero_to_max(tuple_from_dict(self.player_types)):
            old = self.coalition_valuation(atuple)
            off = sum([offsets[elm[0]] * elm[1] for elm in atuple])
            vals[atuple] = (old - off) * scale
        fun = lambda type_counts: vals[type_counts]
        theGame = CoalitionalGame(player_types=self.player_types, coalition_valuation=fun)
        return theGame, newgrand

    def get_is_simple(self):
        """For a "simple" coalitional game all valuations are 1 or 0"""
        for key in zero_to_max(tuple_from_dict(self.player_types)):
            if self.coalition_valuation(key) not in (1,0):
                return False
        return True


def create_voting_game(player_types, type_strengths, crit):
    """Create a colatitional game from a player strengths tuple and  a tupe_stengs dict.
       Returnthe game.
       A weighted majority voting game has a value of 1 if the sum of player strengths * number of players
       voting for the measure exceeds a critical value."""
    strength = lambda player_counts: sum([type_strengths[pc[0]] * pc[1] for pc in player_counts])
    fun = lambda player_counts: int(strength(player_counts) >= crit)
    theGame = CoalitionalGame(player_types=player_types, coalition_valuation=fun)
    return theGame

def create_game_from_unique_players(vals):
    """Create a coalitional game from a valuation dict where the key is (sorted) player labels in the
        coalition. Because the players are unique (one of each type) we do not need a player_types
        tuple, we can derive it. 
        For any values not given fill in values from the highest values of any 
        sub-coalitions given. The empty set coalition has a value of zero. The fill in logic only makes sense
        for profit games."""
    pts = set()
    for key in vals:
        for elm in key:
            pts.add(elm)
    player_types = {pt:1 for pt in pts}
    # given will be (player types): value because types are unique. We will make a new dict
    # with the ones added
    vals2 = {}
    for key in vals:
        key2 = tuple([(elm, 1) for elm in key])
        key2 = insert_zeros(key2, pts)
        vals2[key2] = vals[key]
    ptt = tuple_from_dict(player_types)
    fill_vals(vals2, ptt)
    fun = lambda type_counts: vals2[type_counts]
    theGame = CoalitionalGame(player_types=player_types, coalition_valuation=fun)
    return theGame

def create_game_from_typed_players(player_types, coalition_values):
    """Create a game from a player_types structure and a dict where keys give the coalition type counts
       and the values are values for the coalition. Fill in any missing values with the highest value fo any
        For any valus not given fill in values from the highest values of any 
        sub-coalitions given. The empty set coalition has a value of zero. The fill in logic only makes sense
        for profit games."""

    keys = [key for key in player_types]
    ptt = tuple_from_dict(player_types)
    vals2 = {insert_zeros(key, keys):coalition_values[key] for key in coalition_values}
    fill_vals(vals2, ptt)
    fun = lambda type_counts: vals2[type_counts]
    theGame = CoalitionalGame(player_types=player_types, coalition_valuation=fun)
    return theGame
