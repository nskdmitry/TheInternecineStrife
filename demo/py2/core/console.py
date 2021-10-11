import os
import sys
import random
import curses
import time
import pdb
from argparse import ArgumentParser

def getArgs(scenes = []):
    parser = ArgumentParser()
    parser.add_argument('-a', '--act', default=None, type=str, choice=scenes, help='Scene to show or formation of our soldiers.')
    parser.add_argument('-o', '-opponent_formation', default=None, type=str, choice=scenes, help="Enemy division formation.")
    return parser.parse_args()
