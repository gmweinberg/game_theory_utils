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
    parser.add_argument('--sequence-counts', action='store_true', help="show sequence_counts of elm", 
                        dest='sequence_counts')
    parser.add_argument('--one-to-max', action='store_true', help="show one-to-max of elms",
                        dest='one_to_max')
    parser.add_argument('--vals', help='vals dictionary')
    parser.add_argument('--elms', help='elms sequence')
    args = parser.parse_args()

    if args.elms:
        elms = literal_eval(args.elms)
    if args.vals:
        vals = literal_eval(args.vals)

    if args.distinct:
        vals = literal_eval(args.vals)
        for aresult in distinct_permutations(vals):
           print(aresult)

    if args.powerset:
        elms = literal_eval(args.elms)
        for aresult in powerset(elms):
            print(aresult)

    if args.sequence_counts:
        elms = literal_eval(args.elms)
        print(sequence_counts(elms))

    if args.one_to_max:
        for aresult in one_to_max(elms):
            print(aresult)


#./test_util.py --distinct --vals "{0:5, 1:1}" # should give 5 distinct permutations
#./test_util.py --distinct --vals "{0:3, 1:2}" # should give 10 distinct permutations
#./test_util.py --distinct --vals "{0:2, 1:2, 2:2}" # should give 90 distinct permutations

#./test_util.py --powerset --elms "(1, 2, 3, 4)"

# ./test_util.py --sequence-counts "(0,1,2,3,3,3,0,0)"

# ./test_util.py --one-to-max "((0,3), (1,2))"

