#!/usr/bin/env python
from collections import defaultdict

"""Class for calculating Banzhaf values.
   Banzhaf values are only defined where all subcoalitions have value 0 or 1 e.g. voting majority.
   See Maschler p828"""

class Banzhaf:
    def __init__(self):
        self.player_types = None
        self.banzhaf_values = None
        self.coalition_values = None

    def compute_banzhaf_values(self):
        bcounts = defaultdict(int) # key is player type, val is number of distinct coalitions where adding one of pt earns success
        



