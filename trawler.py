#!/usr/bin/python3
# encoding: utf-8
'''
trawler -- A test result crawler

trawler is a program creating test result history datasets.

@author:     Petr Muller

@copyright:  2016 Petr Muller. All rights reserved.

@license:    The Apache License 2.0

@contact:    muller@afri.cz
@deffield    updated: Updated
'''

import sys
import os

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.1
__date__ = '2016-07-30'
__updated__ = '2016-07-30'

DEBUG = 1
PROFILE_MODE = 0

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by Petr Muller on %s.
  Copyright 2016 Petr Muller. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license,
                                formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument('-V', '--version', action='version', version=program_version_message)

        # Process arguments
        args = parser.parse_args()

        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception as exc: # pylint: disable=broad-except
        if DEBUG:
            raise exc
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(exc) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-h")
        sys.argv.append("-v")
        sys.argv.append("-r")
    if PROFILE_MODE:
        import cProfile
        import pstats
        PROFILE_FILENAME = 'trawler_profile.txt'
        cProfile.run('main()', PROFILE_FILENAME)
        STATSFILE = open("profile_stats.txt", "wb")
        PROFILE = pstats.Stats(PROFILE_FILENAME, stream=STATSFILE)
        STATS = PROFILE.strip_dirs().sort_stats('cumulative')
        STATS.print_stats()
        STATSFILE.close()
        sys.exit(0)
    sys.exit(main())
