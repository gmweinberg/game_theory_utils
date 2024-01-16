#!/usr/bin/env python
from collections import defaultdict
from math import comb, prod

from game_theory_utils.util.convertutil import tuple_from_dict, get_type_count
from game_theory_utils.util.iterutil import zero_to_max, one_less, fill_vals

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
        
        self.shapley_values = None
        self.banzhaf_values = None

    def core_exists(self):
        return False

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
    player_types = set()
    for key in vals:
        player_types.add(key)
    player_types = {pt:1 for pt in player_types}
    # given will be (player types): value because types are unique. We will make a new dict
    # with the ones added
    vals2 = {}
    for key in vals:
        key2 = tuple([(elm, 0) for elm in keys])
        vals2[key2] = vals[key]
    fill_vals(vals2, player_types)
    fun = lambda type_counts: vals[type_counts]
    theGame = ColitionalGame(player_types=player_types, coalition_valuation=fun)
    return theGame

def create_game_from_typed_players(player_types, vals):
    """Create a game from a player_types structure and a dict where keys give the coalition type counts
       and the values are values fo the coalition. Fill in any missing values with the highest value fo any
        For any valus not given fill in values from the highest values of any 
        sub-coalitions given. The empty set coalition has a value of zero. The fill in logic only makes sense
        for profit games."""

    keys = [key for key in player_types]
    fill_vals(vals, player_types)
    fun = lambda type_counts: vals[type_counts]
    theGame = ColitionalGame(player_types=player_types, coalition_valuation=fun)
    return theGame
