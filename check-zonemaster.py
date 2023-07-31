#!/usr/bin/env python3
import argparse
import re
import sys
from subprocess import PIPE
import subprocess
import json
import textwrap
from pprint import pprint

# Reuse what zonemaster uses. Taken from
# https://github.com/zonemaster/zonemaster-engine/blob/master/lib/Zonemaster/Engine/Logger/Entry.pm
levels = {
        'DEBUG3': -2,
        'DEBUG2': -1,
        'DEBUG': 0,
        'INFO': 1,
        'NOTICE': 2,
        'WARNING': 3,
        'ERROR': 4,
        'CRITICAL': 5
        }

parser = argparse.ArgumentParser(
        description = 'Nagios plugin to test DNS zones. This is a wrapper around the '
        'zonemaster-cli command (https://github.com/zonemaster/zonemaster-cli)')
parser.add_argument('--domain',
                    help = 'Domain to test',
                    required = True)
parser.add_argument('--command',
                    help = 'zonemaster command (default: \'zonemaster-cli\')',
                    default = 'zonemaster-cli')
parser.add_argument('--policy',
                    help = 'Path to a zonemaster policy file. This is only '
                    'supported in zonemaster-cli v1')
parser.add_argument('--profile',
                    help = 'Path to a zonemaster profile file')
parser.add_argument('--critical',
                    help = 'Findings of this severity level trigger a CRITICAL',
                    choices = levels.keys(),
                    default = 'ERROR')
parser.add_argument('--warning',
                    help = 'Findings of this severity level trigger a WARNING',
                    choices = levels.keys(),
                    default = 'WARNING')
parser.add_argument('--level',
                    help = 'Run zonemaster-cli with this --level option. Useful '
                    'for displaying extra/debug information. This defaults to the '
                    '--warning level. It can not be higher than the --warning or '
                    '--critical level',
                    choices = levels.keys(),
                    default = 'INFO')
args = parser.parse_args()

domain = args.domain
command = args.command
critical = args.critical
warning = args.warning
level = args.level
profile = args.profile
policy = args.policy

# Sanity checks
if levels[critical] < levels[warning]:
    parser.error('The level to raise a WARNING can not be higher'
                 'than the level to raise a CRITICAL')

if level is None:
    level = warning

# Functions
def nagios_exit(message, code):
    print(message)
    sys.exit(code)

NOT_WHITESPACE = re.compile(r'\S')
from json import JSONDecoder, JSONDecodeError
def decode_stacked_json(document, pos=0, decoder=JSONDecoder()):
    while True:
        match = NOT_WHITESPACE.search(document, pos)
        if not match:
            return
        pos = match.start()
        try:
            obj, pos = decoder.raw_decode(document, pos)
        except JSONDecodeError:
            # do something sensible if there's some error
            raise
        yield obj

# Possible nagios statuses
# See https://assets.nagios.com/downloads/nagioscore/docs/nagioscore/4/en/pluginapi.html
msg = {
        'ok': [],
        'warning': [],
        'critical': [],
        'unknown': []
        }

# Start building the command
subprocess_args = re.split('\s+', command)

# Set arguments
subprocess_args.extend([
    '--json_stream',
    '--json_translate',  # This is now deprecated
    '--level',
    level,
    domain
    ])

# print(" ".join(subprocess_args))

# Run it
try:
    proc = subprocess.run(
        subprocess_args,
        stdout = PIPE,
        stderr = PIPE,
        universal_newlines = True
        )
except Exception as e:
    nagios_exit("UNKNOWN: " + str(e), 3)

if(proc.returncode != 0):
    # Put errors on one line
    output = " ".join([s.strip() for s in proc.stdout.split("\n")])
    nagios_exit(f"UNKNOWN: {output}", 3)

results = [i for i in decode_stacked_json(proc.stdout)]

oks = [r for r in results if levels[r['level']] < levels[warning]]
warnings = [r for r in results
            if levels[r['level']] >= levels[warning] and
            levels[r['level']] < levels[critical]
            ]
criticals = [r for r in results if levels[r['level']] >= levels[critical]]

# Format the string for the Nagios LONGTEXT
timedecimals = 3
maxtimewidth = len(str(max([int(r['timestamp']) for r in results])))
maxlevelwidth = max([len(r['level']) for r in results])
# The 4 comes from:
# - the decimal point
# - the 's' after the seconds
# - the space between the seconds and the level
# - the space between the level and the message
indent = " " * (maxlevelwidth + maxtimewidth + timedecimals + 4)

wrapper = textwrap.TextWrapper(width=78, subsequent_indent=indent)
longtext = "\n".join([
    f"{r['timestamp']:{maxtimewidth+3}.{timedecimals}f}s {r['level']:{maxlevelwidth}s} { wrapper.fill(text=r['message']) }"
    for r in results])

if(len(criticals) > 0):
    msg['critical'].append("Found {0} issue{1} with severity {2} or higher for {3}\n{4}".format(
        len(criticals),
        's' if len(criticals) > 1 else '',
        critical,
        domain,
        longtext
        )
    )
if(len(warnings) > 0):
    msg['warning'].append("Found {0} issue{1} with severity {2} or higher for {3}\n{4}".format(
        len(warnings),
        's' if len(warnings) > 1 else '',
        warning,
        domain,
        longtext
        )
    )
else:
    msg['ok'].append("Found no issues with severity {0} or higher for {1}\n{2}".format(
        warning,
        domain,
        longtext
        )
    )

# Exit with accumulated message(s)
if len(msg['critical']) > 0:
    nagios_exit("CRITICAL: " + ' '.join(msg['critical']), 2)
elif len(msg['warning']) > 0:
    nagios_exit("WARNING: " + ' '.join(msg['warning']), 1)
else:
    nagios_exit("OK: " + ' '.join(msg['ok']), 0)