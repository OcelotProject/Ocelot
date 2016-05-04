#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Ocelot command line interface. See https://ocelot.space/ for more info.

Usage:
  ocelot-cli <dirpath>
  ocelot-cli fix <dirpath>
  ocelot-cli -l | --list
  ocelot-cli -h | --help
  ocelot-cli --version

Options:
  --list        List the updates needed, but don't do anything
  -h --help     Show this screen.
  --version     Show version.

"""
from docopt import docopt
from ocelot import extract_directory, xmlify_directory


def main():
    args = docopt(__doc__, version='Ocelot LCI 0.1')
    if args['fix']:
        xmlify_directory(args['<dirpath>'])
    else:
        data = extract_directory(args["<dirpath>"])


if __name__ == "__main__":
    main()
