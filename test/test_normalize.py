#!/usr/bin/env python
import sys
sys.path.append('../src')

from game_theory_utils.coalitions.coalition import *

from game_theory_utils.util.convertutil import tuple_from_dict

if __name__ == '__main__':
    from argparse import ArgumentParser
    from ast import literal_eval
    parser = ArgumentParser()
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--voting', action='store_true', help="test voting")
    parser.add_argument('--types', help='player types dictionary')
    parser.add_argument('--strengths', help='player strengths dictionary')
    parser.add_argument('--vals', help='valuations_dict')
    args = parser.parse_args()
    verbose = args.verbose

    if args.types:
        player_types = literal_eval(args.types)

    if args.vals:
        vals = literal_eval(args.vals)


    cg = create_game_from_typed_players(player_types=player_types, coalition_values=vals)
    cg0, _ =  cg.zero_normalize()
    print(cg0.get_valuation())
    print('original superadditive', cg.get_is_superadditive())
    print('normalized superadditive', cg0.get_is_superadditive()) # superadditive must stay the same after normaliztion
    print('original monotonic', cg.get_is_monotonic())
    print('normalized monotonic', cg0.get_is_monotonic())


# renormalized glove game. I added 2 to the value of coalitions including player 0,
# and made having a pair of gloves worth 2 instead 1. Renormalizing should return the original glove game.
#  ./test_normalize.py --vals "{((0,1), (1,0), (2,0)):2, ((0,1), (1,0), (2,1)):4, ((0,0), (1,1), (2,1)):2}" --types "{0:1, 1:1, 2:1}"

# glove game again, subtracing 2 from player 0. I added 2 to the value of coalitions including player 0,
# and made having a pair of gloves worth 2 instead 1. Renormalizing should return the original glove game.
#  ./test_normalize.py --vals "{((0,1), (1,0), (2,0)):-2, ((0,1), (1,0), (2,1)):0, ((0,0), (1,1), (2,1)):2}" --types "{0:1, 1:1, 2:1}"


