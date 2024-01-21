#!/usr/bin/env python
import sys
sys.path.append('../src')

from game_theory_utils.coalitions.banzhaf import Banzhaf
from game_theory_utils.coalitions.coalition import *

from game_theory_utils.util.convertutil import tuple_from_dict

def un_security_old(player_counts):
    """According to "old" security council rules for a ruling to pass it needs supprt of all
       5 permanent 'P' members and 2 temporary '2' Members.
       Argument pass to fun will look like (('P', 4), ('T':2))"""
    perms = 0
    temps = 0
    for elm in player_counts:
        if elm[0] == 'P':
            perms = elm[1]
        elif elm[0] == 'T':
            temps = elm[1]
    if perms >= 5 and temps >= 2:
        return 1
    return 0



if __name__ == '__main__':
    from argparse import ArgumentParser
    from ast import literal_eval
    parser = ArgumentParser()
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--voting', action='store_true', help="test voting")
    parser.add_argument('--un', action='store_true', help="test passing un security function")
    parser.add_argument('--types', help='player types dictionary')
    parser.add_argument('--strengths', help='player strengths dictionary')
    parser.add_argument('--vals', help='valuations_dict')
    args = parser.parse_args()
    verbose = args.verbose

    banzhaf = Banzhaf()
    banzhaf.verbose = verbose

    if args.types:
        player_types = literal_eval(args.types)
    if args.strengths:
        strengths = literal_eval(args.strengths)

    if args.voting:
        banzhaf.set_voting_powers(player_types=player_types, type_strength=strengths)
        banzhaf.compute_banzhaf_values()
        print('computed values bz',  banzhaf.get_banzhaf_values())
        cg = create_voting_game(player_types=player_types, type_strengths=strengths, crit=5)
        print('computed values cg',  cg.get_banzhaf_values())

    if args.un:
        player_types = {'P':5, 'T':6}
        banzhaf.set_player_types(player_types)
        banzhaf.set_coalition_valuation(un_security_old)
        banzhaf.compute_banzhaf_values()
        print('computed values bz',  banzhaf.get_banzhaf_values())
        cg0 = CoalitionalGame(player_types, un_security_old)
        print('computed values cg0',  cg0.get_banzhaf_values())
        print('valuation', cg0.get_valuation())

    if args.vals:
        vals = literal_eval(args.vals)
        banzhaf.set_coalition_values(vals, player_types)
        banzhaf.compute_banzhaf_values()
        print('computed values bz',  banzhaf.get_banzhaf_values())



# Computed vals computed different ways must give the same answer

# test voting. 
# Different types with the same strength should have the same value, 1/ total nmber of players.

# ./test_banzhaf.py --voting --types "{0:3, 1:2, 2:2}" --strength "{0:1, 1:1, 2:2}"

# Un security council old, 5 permanent and 6 temporary members Maschler 813
# ./test_banzhaf.py --types "{'P':5, 'T':6}" --vals "{(('P',5),('T',2)):1}"

# ./test_banzhaf.py --un
