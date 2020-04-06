import argparse
import sys

parser = argparse.ArgumentParser(description="BGP flowspec SDN controller at home. https://github.com/Jamesits/Pilot")
parser.add_argument('--config', type=str, default="", help='Path to the config file')


def parse_args():
    return parser.parse_args()


def print_help():
    return parser.print_help(file=sys.stderr)
