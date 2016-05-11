#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Ocelot command line interface. See https://ocelot.space/ for more info.

Usage:
  ocelot-cli run <dirpath>
  ocelot-cli run <dirpath> <config>
  ocelot-cli fix <dirpath>
  ocelot-cli validate <dirpath> <schema>
  ocelot-cli validate <dirpath>
  ocelot-cli -l | --list
  ocelot-cli -h | --help
  ocelot-cli --version

Options:
  --list        List the updates needed, but don't do anything
  -h --help     Show this screen.
  --version     Show version.

"""
from docopt import docopt
from ocelot import extract_directory, xmlify_directory, validate_directory, data_dir
import os


def main():
    args = docopt(__doc__, version='Ocelot LCI 0.1')
    if args['fix']:
        xmlify_directory(args['<dirpath>'])
    elif args['validate']:
        validate_directory(
          args['<dirpath>'],
          args['<schema>'] or os.path.join(data_dir, 'EcoSpold02.xsd')
        )
    else:
        data = extract_directory(args["<dirpath>"])


if __name__ == "__main__":
    main()
