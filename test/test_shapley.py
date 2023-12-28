#!/usr/bin/env python
import sys
sys.path.append('../src')

from game_theory_utils.coalitions.shapley import Shapley

if __name__ == '__main__':
    from argparse import ArgumentParser
    from ast import literal_eval
    parser = ArgumentParser()
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--vals', help='valuations_dict')
    args = parser.parse_args()

    vals = {(0,1):1, (0,2):1, (1,2):1}
    if args.vals:
        vals = literal_eval(args.vals)
        shapley = Shapley(vals)
        sha = shapley.get_shapley_values()
        print(sha)

#./test_shapley.py --vals "{(0,1):1, (0,2):1, (1,2):1}" # majority voting gives 1/3, 1/3, 1/3
#./test_shapley.py --vals "{(1,3):1, (2,3):1}" # gloves game should give 1/6, 1/6, 2/3 Maschler p 807
