#!/usr/bin/env python
import sys
sys.path.append('../src')

from game_theory_utils.coalitions.shapley import Shapley

if __name__ == '__main__':
    from argparse import ArgumentParser
    from ast import literal_eval
    parser = ArgumentParser()
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--voting', action='store_true')
    parser.add_argument('--types', help='player types dictionary')
    parser.add_argument('--strengths', help='player strengths dictionary')
    parser.add_argument('--vals', help='valuations_dict')
    args = parser.parse_args()

    vals = {(0,1):1, (0,2):1, (1,2):1}
    if args.vals:
        vals = literal_eval(args.vals)
        shapley = Shapley(vals)
        sha = shapley.get_shapley_values()
        print(sha)

    if args.types:
        player_types = literal_eval(args.types)
    if args.strengths:
        strengths = literal_eval(args.strengths)

    if args.voting:
        shapley = Shapley()
        shapley.set_voting_powers(player_types=player_types, type_strength=strengths)
        shapley.compute_shapley_vals2()
        print('computed values',  shapley.get_shapley_values())
        shapley.simulate_shapley_values(100000)
        print('simulated values',  shapley.get_shapley_values())


#./test_shapley.py --vals "{(0,1):1, (0,2):1, (1,2):1}" # majority voting gives 1/3, 1/3, 1/3
#./test_shapley.py --vals "{(1,3):1, (2,3):1}" # gloves game should give 1/6, 1/6, 2/3 Maschler p 807


# test voting. 
# Different types with the same strength should have the same value
# ./test_shapley.py --voting --types "{0:3, 1:2, 2:2}" --strength "{0:1, 1:1, 2:2}"
