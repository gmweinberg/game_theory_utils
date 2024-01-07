#!/usr/bin/env python
import sys
sys.path.append('../src')

from game_theory_utils.coalitions.banzhaf import Banzhaf

if __name__ == '__main__':
    from argparse import ArgumentParser
    from ast import literal_eval
    parser = ArgumentParser()
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--voting', action='store_true', help="test voting")
    parser.add_argument('--ungrouped', action='store_true', help="test set_ungrouped_coalition_values")
    parser.add_argument('--grouped', action='store_true', help="test set_grouped_coalition_values")
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
    if args.vals:
        vals = literal_eval(args.vals)

    if args.voting:
        banzhaf.set_voting_powers(player_types=player_types, type_strength=strengths)
        banzhaf.compute_banzhaf_values()
        print('computed values',  banzhaf.get_banzhaf_values())

    if args.ungrouped:
        banzhaf.set_ungrouped_coalition_values(vals)
        banzhaf.compute_banzhaf_values()
        print('computed values',  banzhaf.get_banzhaf_values())

    if args.grouped:
        banzhaf.set_grouped_coalition_values(coalition_values = vals, player_types=player_types)
        banzhaf.compute_banzhaf_values()
        print('computed values',  banzhaf.get_banzhaf_values())

# Simulated vals should be almost the same as computed vals as long as number of iterations is large.
# Computed vals computed different ways must give the same answer


# test voting. 
# Different types with the same strength should have the same value, 1/ total nmber of players.

# ./test_banzhaf.py --voting --types "{0:3, 1:2, 2:2}" --strength "{0:1, 1:1, 2:2}"
# ./test_banzhaf.py --ungrouped --vals "{(0,1):1, (0,2):1, (1,2):1}"
# ./test_banzhaf.py --grouped --types "{0:3}" --vals "{((0,2),):1}"
# ./test_banzhaf.py --grouped --types "{0:3, 1:2}" --vals "{((0,3),):1, ((0,2),(1,1)):1, ((0,1),(1,2)):1}"

# For the glove game, there are 2 left gloves and 1 right glove. Either glove by itself is worthless
# a left and a right are worth 1.
# See Maschler page 807
#
# glove game gives 1/6, 1/6, 2/3
# ./test_banzhaf.py --ungrouped --vals "{(0,2):1, (1,2):1}"
# ./test_banzhaf.py --grouped --types "{0:2, 1:1}" --vals "{((0,1),(1,1)):1}"

# Un security council old, 5 permanent and 6 temporary members Maschler 813
# ./test_banzhaf.py --grouped --types "{'P':5, 'T':6}" --vals "{(('P',5),('T',2)):1}"
# Un security new
# ./test_banzhaf.py --grouped --types "{'P':5, 'T':10}" --vals "{(('P',5),('T',4)):1}"

