#!/usr/bin/env python
import sys
sys.path.append('../src')

from game_theory_utils.coalitions.shapley import Shapley

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

    shapley = Shapley()
    shapley.verbose = verbose

    if args.types:
        player_types = literal_eval(args.types)
    if args.strengths:
        strengths = literal_eval(args.strengths)
    if args.vals:
        vals = literal_eval(args.vals)

    if args.voting:
        shapley.set_voting_powers(player_types=player_types, type_strength=strengths)
        shapley.compute_shapley_values()
        print('computed values',  shapley.get_shapley_values())
        shapley.simulate_shapley_values(100000)
        print('simulated values',  shapley.get_shapley_values())

    if args.ungrouped:
        shapley.set_ungrouped_coalition_values(vals)
        shapley.compute_shapley_values()
        print('computed values',  shapley.get_shapley_values())

    if args.grouped:
        shapley.set_grouped_coalition_values(coalition_values = vals, player_types=player_types)
        shapley.compute_shapley_values()
        print('computed values',  shapley.get_shapley_values())

# Simulated vals should be almost the same as computed vals as long as number of iterations is large.
# Computed vals computed different ways must give the same answer


# test voting. 
# Different types with the same strength should have the same value, 1/ total nmber of players.

# ./test_shapley.py --voting --types "{0:3, 1:2, 2:2}" --strength "{0:1, 1:1, 2:2}"
# ./test_shapley.py --ungrouped --vals "{(0,1):1, (0,2):1, (1,2):1}"
# ./test_shapley.py --grouped --types "{0:3}" --vals "{((0,2),):1}"
# ./test_shapley.py --grouped --types "{0:3, 1:2}" --vals "{((0,3),):1, ((0,2),(1,1)):1, ((0,1),(1,2)):1}"

# For the glove game, there are 2 left gloves and 1 right glove. Either glove by itself is worthless
# a left and a right are worth 1.
# See Maschler page 807
#
# glove game gives 1/6, 1/6, 2/3
# ./test_shapley.py --ungrouped --vals "{(0,2):1, (1,2):1}"
# ./test_shapley.py --grouped --types "{0:2, 1:1}" --vals "{((0,1),(1,1)):1}"

# Un security council old, 5 permanent and 6 temporary members Maschler 813
# ./test_shapley.py --grouped --types "{'P':5, 'T':6}" --vals "{(('P',5),('T',2)):1}"
# Un security new
# ./test_shapley.py --grouped --types "{'P':5, 'T':10}" --vals "{(('P',5),('T',4)):1}"

