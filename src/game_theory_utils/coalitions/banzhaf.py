#!/usr/bin/env python
from collections import defaultdict
from math import comb, prod
from game_theory_utils.util.iterutil import zero_to_max, one_less, fill_vals
from game_theory_utils.util.convertutil import tuple_from_dict, get_type_count

"""Class for calculating Banzhaf values.
   Banzhaf values are only defined where all subcoalitions have value 0 or 1 e.g. voting majority.
   See Maschler p828"""

class Banzhaf:
    def __init__(self):
        self.player_types = None
        self.banzhaf_values = None
        self.valuation = None # Function determining if voting power is sufficient
                              # Argument to function is tuple of tuples ((type1, count1), (type2, count2)...)
        self.ungrouped_valuation = None

    def set_player_types(self, player_types):
        self.player_types = player_types

    def set_coalition_valuation(self, fun):
        self.valuation = fun

    def get_banzhaf_values(self):
        return self.banzhaf_values

    def compute_banzhaf_values(self):
        bcounts = defaultdict(int) # key is player type, val is number of distinct coalitions
                                   # where adding one of pt earns success
        for atuple in zero_to_max(tuple_from_dict(self.player_types)):
            if self.valuation(atuple):
                for less, removed in one_less(atuple):
                    if not self.valuation(less):
                        mult = prod([comb(self.player_types[elm[0]], elm[1]) for elm in less])
                        mult *= (self.player_types[removed] - get_type_count(less, removed))
                        # print(atuple, removed, less, mult)

                        bcounts[removed] += mult
        total = sum([bcounts[pt] for pt in bcounts])
        self.banzhaf_values = {pt:0 for pt in self.player_types} # in case bcount is zero
        for type_ in bcounts:
            self.banzhaf_values[type_] = bcounts[type_] / (total * self.player_types[type_])

    def set_coalition_values(self, coalition_values, player_types):
        """Save the player types and a coalition evaluation function.
           The coalition_values has the same format as shapley, but becauseevery coalition
           must have a value of zero or one, we also support just giving a list of coaltions with values 1.
        """
        self.set_player_types(player_types)
        if type(coalition_values) == dict:
            vals = coalition_values
        else:
            vals = {tuple2(key):1 for key in key in coalition_values}
        pt = tuple_from_dict(player_types)
        fill_vals(vals, player_types=pt)
        fun = lambda type_counts: vals[type_counts]
        self.set_coalition_valuation(fun)



    def set_voting_powers(self, player_types, type_strength):
        """A specific coalation value structure such that a coalition wth more than
           half the total voting strength has a coaltion value of 1, and less than or equal
           has a value of zero."""
        self.set_player_types(player_types)
        total = sum([player_types[player] * type_strength[player] for player in player_types])
        crit = total / 2
        strength = lambda player_counts: sum([type_strength[pc[0]] * pc[1] for pc in player_counts])
        fun = lambda player_counts: int(strength(player_counts) > crit)
        self.set_coalition_valuation(fun)


