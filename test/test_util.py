#!/usr/bin/env python

"""Test the functions in utils"""
import sys
sys.path.append('../src')

from game_theory_utils.util import *

if __name__ == '__main__':
    from argparse import ArgumentParser
    from ast import literal_eval
    parser = ArgumentParser()
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--distinct', action='store_true', help="show distinct permutations of vals")
    parser.add_argument('--powerset', action='store_true', help="show powerset of elm")
    parser.add_argument('--vals', help='vals dictionary')
    parser.add_argument('--elms', help='elms sequence')
    args = parser.parse_args()

    if args.distinct:
        vals = literal_eval(args.vals)
        for aresult in distinct_permutations(vals):
           print(aresult)

    if args.powerset:
        elms = literal_eval(args.elms)
        for aresult in powerset(elms):
            print(aresult)

#./test_util.py --distinct --vals "{0:5, 1:1}" # should give 5 distinct permutations
#./test_util.py --distinct --vals "{0:3, 1:2}" # should give 10 distinct permutations
#./test_util.py --distinct --vals "{0:2, 1:2, 2:2}" # should give 90 distinct permutations

#./test_util.py --powerset --elms "(1, 2, 3, 4)"

