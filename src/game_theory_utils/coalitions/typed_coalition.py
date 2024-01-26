#!/usr/bin/env python
from collections import defaultdict
from math import comb, prod
import random

from game_theory_utils.util.convertutil import (tuple_from_dict, list_from_dict, get_type_count, insert_zeros)
from game_theory_utils.util.iterutil import (zero_to_max, one_less, fill_vals, sequence_from_types,
                                             distinct_permutations, sequence_counts)

__all__ = ('TypedCoalitionalGame', 'create_typed_voting_game',
           'create_typed_game')

class TypedCoalitionalGame:
    """A TypedCoalitionalGame has a dictionary called player_types which gives the count of each  a set of players and a function giving the value of each subset of
      members, called a coalition. In this implementation I support the notion of player "types":
      the value of a coalition depends on the number of types of each player.
      If all players are unique, there is just one player of each type.
      I represent the player types as a dict e.g. {'a': 3, 'b', 4 } means there are 3 players of type a and
      4 of type b.
      The coalition valuation function takes a coalition tuple as an input. Internally it will
      usually just be a dictionary lookup with the coalition tupe as a key. The keys must be sorted since
      (('a',3), ('b',4)) and (('b', 4), ('a',3)) are not the same.
    """

    def __init__(self, player_types, coalition_valuation, isCost=False):
        self.player_types = player_types #
        self.coalition_valuation = coalition_valuation # function
        self.isCost = isCost
        self.verbose = False

        self.simple = None
        self.superadditive = None
        self.monotonic = None
        
        self.shapley_values = None
        self.banzhaf_values = None

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

    def is_equivalent(self, game):
        """Detremine if the passed game is strategically equivalent. This function just checks if the games
           are equivalent as labelled, not if they can be made equivalent by relabelling players."""
        # games must have the same player types to be equivalent.
        if not self.player_types == game.player_types:
            return False
        norm0, grand0 = self.zero_normalize()
        norm1, grand1 = game.zero_normalize()
        return grand0 == grand1

    def get_is_monotonic(self):
        """A game is monotonics if the value of a coalition is ≥ the value of its subcoalitions."""
        for atuple in zero_to_max(tuple_from_dict(self.player_types)):
            bigger = self.coalition_valuation(atuple)
            for less, removed in one_less(atuple):
                if self.coalition_valuation(less) > bigger:
                    return False
        return True

    def get_is_superadditive(self):
        for atuple in zero_to_max(tuple_from_dict(self.player_types)):
            val = self.coalition_valuation(atuple)
            djm = tuple([(elm[0], self.player_types[elm[0]] - elm[1]) for elm in atuple])
            for adisjoint in zero_to_max(djm):
                theUnion = tuple([(atuple[ii][0], atuple[ii][1] + adisjoint[ii][1]) for ii in range(len(atuple))])
                if self.isCost:
                    if self.coalition_valuation(theUnion) > self.coalition_valuation(adisjoint) + val:
                        return False
                else:
                    if self.coalition_valuation(theUnion) < self.coalition_valuation(adisjoint) + val:
                        return False
        return True


    def get_is_simple(self):
        """For a "simple" coalitional game all valuations are 1 or 0"""
        for key in zero_to_max(tuple_from_dict(self.player_types)):
            if self.coalition_valuation(key) not in (1,0):
                return False
        return True


def create_typed_voting_game(player_types, type_strengths, crit):
    """Create a colatitional game from a player strengths tuple and  a tupe_stengs dict.
       Returnthe game.
       A weighted majority voting game has a value of 1 if the sum of player strengths * number of players
       voting for the measure exceeds a critical value."""
    strength = lambda player_counts: sum([type_strengths[pc[0]] * pc[1] for pc in player_counts])
    fun = lambda player_counts: int(strength(player_counts) >= crit)
    theGame = TypedCoalitionalGame(player_types=player_types, coalition_valuation=fun)
    return theGame


def create_typed_game(player_types, coalition_values):
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
    theGame = TypedCoalitionalGame(player_types=player_types, coalition_valuation=fun)
    return theGame
