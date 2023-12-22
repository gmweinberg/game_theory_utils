#!/usr/bin/env python
import sys
sys.path.append('../src')

from game_theory_utils.coalitions.shapley import get_shapley_values

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
    sha = get_shapley_values(vals)
    print(sha)
