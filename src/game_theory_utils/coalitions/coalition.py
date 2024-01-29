#!/usr/bin/env python
from collections import defaultdict
from math import comb, prod
import random

from itertools import permutations

from game_theory_utils.util.convertutil import (tuple_from_dict, list_from_dict, get_type_count, insert_zeros)
from game_theory_utils.util.iterutil import (powerset, froze_remove_one, sequence_from_types,
                                             distinct_permutations, sequence_counts)

__all__ = ('CoalitionalGame', 'create_voting_game')

class CoalitionalGame:
    """A coalitional game is defined as a set of players and a function giving the value of each subset of
      members, called a coalition.
    """

    def __init__(self, coalition_values, isCost=False):
        self.players = set()
        self.coalition_values = {} # key = frozenset players, val = coalition value
        self.isCost = isCost
        self.verbose = False

        for key in coalition_values:
            for elm in key:
                self.players.add(elm)
            self.coalition_values[frozenset(key)] = coalition_values[key]
        self.fill_coalition_values()

        
    def fill_coalition_values(self):
        """If self.coalition_values dict is mssing values, fill them in by assigning the highest value
           of any subset that has a value."""
        for elm in powerset(self.players):
            elm = frozenset(elm)
            if elm not in self.coalition_values:
                if not elm:
                    self.coalition_values[elm] = 0 # empty coalition has zero value
                    continue
                max_ = None
                for less, removed in froze_remove_one(elm):
                    if max_ is None or self.coalition_values[less] > max_:
                        max_ = self.coalition_values[less]
                self.coalition_values[elm] = max_

    def is_core(self, imputation):
        """The imputation is effectively a payoff assigned to each player. The imputation X is in the core
           if for all coalitions S, x(S) ≥ v(S)"""
        for elm in powerset(self.players):
            elm = frozenset(elm)
            x = sum([imputation[player] for player in elm])
            if self.coalition_values[elm] > x:
                return False
        return True


    def get_banzhaf_values(self):
        """Get the banzhaf values. Note the banzhaf values are only defined for simple games (games where
           all coalitions are values zero or 1."""
        bcounts = defaultdict(int) # key is player type, val is number of distinct coalitions
                                   # where adding one of pt earns success
        for elm in powerset(self.players):
            elm = frozenset(elm)
            if self.coalition_values[elm]:
                for less, removed in froze_remove_one(elm):
                    if not self.coalition_values[less]:
                        bcounts[removed] += 1
        total = sum([bcounts[player] for player in bcounts])
        banzhaf_values = {pt:0 for pt in self.players} # in case bcount is zero
        for player in bcounts:
            banzhaf_values[player] = bcounts[player] / total
        return banzhaf_values


    def get_shapley_values(self):
        """Calculate and retur the shapley values"""
        shapley = defaultdict(float)
        perms = 0
        for perm in permutations(self.players):
            old = 0
            perms += 1
            for ii in range(len(perm)):
                piece = frozenset(perm[:ii + 1])
                new = self.coalition_values[piece]
                player = perm[ii]
                shapley[player] += new - old
                old = new

        for player in shapley.keys():
            shapley[player] = shapley[player]/perms
        return dict(shapley)

    def simulate_shapley_values(self, perms):
        """Get approximate shapley values by looking at random permutations.
           Returns the approximate values."""
        combo = [player for player in self.players]
        shapley = defaultdict(float)
        for jj in range(perms):
            old = 0
            random.shuffle(combo)
            for ii in range(len(combo)):
                piece = frozenset(combo[:ii + 1])
                new = self.coalition_values[piece]
                player = combo[ii]
                shapley[player] += new - old
                old = new

        for player in shapley.keys():
            shapley[player] = shapley[player]/perms
        return dict(shapley)

    def zero_normalize(self):
        """Create straegically equivalent 0 normalized game. A game is 0 normalized if
           the colaition value is zero for all single-member coalitions. The value of the
           grand coalition will be 1, 0, or -1. Returns the pai (game, v) where
           v is the value of the grand coalition in the new game.
        """
        grand = self.coalition_values[frozenset(self.players)]
        offtotal = sum([self.coalition_values[frozenset([player])] for player in self.players])
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
        for elm in powerset(self.players):
            elm = frozenset(elm)
            old = self.coalition_values[elm]
            off = sum([self.coalition_values[frozenset([player])] for player in elm])
            vals[elm] = (old - off) * scale
        theGame = CoalitionalGame(vals)
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
        for elm in powerset(self.players):
            elm = frozenset(elm)
            old = self.coalition_values[elm]
            for less, removed in froze_remove_one(elm):
                if self.coalition_values[less] > old:
                    return False
        return True

    def get_is_superadditive(self):
        """A game is superadditive if for every pair of disjoint coaalitions, the valuation of the union
           is  ≥ the sum of the values of the pair."""
        # this can take a really long time to check
        for elm in powerset(self.players):
            elm = frozenset(elm)
            complement = self.players - elm
            for disjointelm in powerset(complement):
                disjointelm = set(disjointelm)
                sum_ = self.coalition_values[frozenset(disjointelm)] + self.coalition_values[elm]
                if sum_ > self.coalition_values[frozenset(elm | disjointelm)]:
                    return False
        return True


    def get_is_simple(self):
        """For a "simple" coalitional game all valuations are 1 or 0"""
        for val in self.coalition_values.values():
            if val not in (1,0):
                return False
        return True


def create_voting_game(player_strengths, crit):
    """Create a colatitional game from a player strengths dict.
       Return the game.
       A weighted majority voting game has a value of 1 if the sum of player strengths * number of players
       voting for the measure exceeds a critical value."""
    players = set([player for player in player_strengths])
    coalition_values = {}
    for elm in powerset(players):
        key = frozenset(elm)
        strength = sum([player_strengths[player] for player in elm])
        val = int(strength >= crit)
        coalition_values[key] = val

    theGame = CoalitionalGame(coalition_values)
    return theGame

