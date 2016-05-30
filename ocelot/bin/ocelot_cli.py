#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Ocelot command line interface. See https://ocelot.space/ for more info.

Usage:
  ocelot-cli run <dirpath> [--noshow]
  ocelot-cli run <dirpath> <config> [--noshow]
  ocelot-cli cleanup
  ocelot-cli validate <dirpath> <schema>
  ocelot-cli validate <dirpath>
  ocelot-cli -l | --list
  ocelot-cli -h | --help
  ocelot-cli --version

Options:
  --list        List the updates needed, but don't do anything
  --noshow      Don't open HTML report in new web browser tab
  -h --help     Show this screen.
  --version     Show version.

"""
from docopt import docopt
from ocelot import (
    cleanup_data_directory,
    data_dir,
    system_model,
    validate_directory,
)
import os
import sys


def main():
    try:
        args = docopt(__doc__, version='Ocelot open source linker CLI 0.1')
        if args['validate']:
            validate_directory(
              args['<dirpath>'],
              args['<schema>'] or os.path.join(data_dir, 'EcoSpold02.xsd')
            )
        elif args['cleanup']:
            cleanup_data_directory()
        elif args['run']:
            system_model(args["<dirpath>"], args['<config>'], show=not args['--noshow'])
        else:
            raise ValueError
    except KeyboardInterrupt:
        print("Terminating Ocelot CLI")
        sys.exit(1)


if __name__ == "__main__":
    main()
