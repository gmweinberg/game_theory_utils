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
    parser.add_argument('--keys', help='keys for testing')
    parser.add_argument('--list2', help='test list2', action='store_true')
    parser.add_argument('--tuple2', help='test tuple2', action='store_true')
    parser.add_argument('--tuple-from-dict', help='test tuple_from_dict', action='store_true', dest='tuple_from_dict')
    parser.add_argument('--dict-from-tuple', help='test dict_from_tuple', action='store_true', dest='dict_from_tuple')
    parser.add_argument('--insert-zeros', help='test insert_zeros', action='store_true', dest='insert_zeros')
    parser.add_argument('--remove-zeros', help='test remove_zeros', action='store_true', dest='remove_zeros')
    args = parser.parse_args()

    if args.vals:
        vals = literal_eval(args.vals)

    if args.keys:
        keys = literal_eval(args.keys)

    if args.list2:
        print(list2(vals))

    if args.tuple2:
        print(tuple2(vals))

    if args.tuple_from_dict:
        print(tuple_from_dict(vals))

    if args.dict_from_tuple:
        print(dict_from_tuple(vals))

    if args.insert_zeros:
        print(insert_zeros(vals, keys))

    if args.remove_zeros:
        print(remove_zeros(vals))

# ./test_convertutil.py --list2 --vals "((0,2),(1,3),(4,5))"
# ./test_convertutil.py --tuple2 --vals "[[0,2],[1,3],[4,5]]"
# ./test_convertutil.py --tuple-from-dict --vals "{0:2, 1:3, 4:5}"
# ./test_convertutil.py --dict-from-tuple --vals "((0,2),(1,3),(4,5))"
# ./test_convertutil.py --insert-zeros --vals "((0,2),(1,3),(4,5))" --keys "[0, 1, 2, 3, 4]"
# ./test_convertutil.py --remove-zeros --vals "((0,2),(1,3),(2, 0),(3,0),(4,5))"

