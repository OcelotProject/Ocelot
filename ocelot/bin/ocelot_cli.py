#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Ocelot command line interface. See https://ocelot.space/ for more info.

Commands:

  * run: Run a system model. Uses the default system model (ecoinvent cutoff) if <config> is not specified. <dirpath> is the input files directory.
  * cleanup: Delete all model runs more than one week old.
  * validate: Extract the ecospold2 files in <dirpath> and make sure the extracted data meets the Ocelot internal format. This command doesn't use the extraction cache.
  * xsd: Validate the ecospold2 files in <dirpath> against the default XSD or another XSD specified in <schema>.

See https://docs.ocelot.space/filesystem.html#writing-intermediate-results for information on saving strategies.

Usage:
  ocelot-cli run <dirpath> [--noshow] [--save=<strategy>] [--follow=<filename>]
  ocelot-cli run <dirpath> <config> [--noshow] [--save=<strategy>] [--follow=<filename>]
  ocelot-cli cleanup
  ocelot-cli validate <dirpath>
  ocelot-cli xsd <dirpath> <schema>
  ocelot-cli xsd <dirpath>
  ocelot-cli -l | --list
  ocelot-cli -h | --help
  ocelot-cli --version

Options:
  --list              List the updates needed, but don't do anything
  --noshow            Don't open HTML report in new web browser tab
  --save=<strategy>   Strategy for which intermediate results to save.
  --follow=<filename> Filename to follow during system model execution
  -h --help           Show this screen.
  --version           Show version.

"""
from docopt import docopt
from ocelot import (
    cleanup_data_directory,
    data_dir,
    system_model,
    validate_directory_against_xsd,
    validate_directory,
)
import os
import sys


def main():
    try:
        args = docopt(__doc__, version='Ocelot open source linker CLI 0.2')
        if args['run']:
            system_model(
                args["<dirpath>"],
                args['<config>'],
                show=not args['--noshow'],
                save_strategy=args['--save'],
                follow=args['--follow']
            )
        elif args['validate']:
            validate_directory(args['<dirpath>'])
        elif args['xsd']:
            validate_directory_against_xsd(
              args['<dirpath>'],
              args['<schema>'] or os.path.join(data_dir, 'EcoSpold02.xsd')
            )
        elif args['cleanup']:
            cleanup_data_directory()
        else:
            raise ValueError
    except KeyboardInterrupt:
        print("Terminating Ocelot CLI")
        sys.exit(1)


if __name__ == "__main__":
    main()
