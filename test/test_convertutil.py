#!/usr/bin/env python

"""Test the functions in convertutil"""
import sys
sys.path.append('../src')

from game_theory_utils.util.convertutil import *

if __name__ == '__main__':
    from argparse import ArgumentParser
    from ast import literal_eval
    parser = ArgumentParser()
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--vals', help='values for testing')
    parser.add_argument('--list2', help='test list2', action='store_true')
    parser.add_argument('--tuple2', help='test tuple2', action='store_true')
    parser.add_argument('--tuple-from-dict', help='test tuple_from_dict', action='store_true', dest='tuple_from_dict')
    args = parser.parse_args()

    if args.vals:
        vals = literal_eval(args.vals)

    if args.list2:
        print(list2(vals))

    if args.tuple2:
        print(tuple2(vals))

    if args.tuple_from_dict:
        print(tuple_from_dict(vals))

# ./test_convertutil.py --list2 --vals "((0,2),(1,3),(4,5))"
# ./test_convertutil.py --tuple2 --vals "[[0,2],[1,3],[4,5]]"
# ./test_convertutil.py --tuple-from-dict --vals "{0:2, 1:3, 4:5}"

