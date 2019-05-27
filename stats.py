""" Display browser support stats """

import sys
import json
import argparse
import warnings
import pkg_resources
from pathlib import Path

import requests
import colorama

import config


# Configure colorama for platform
colorama.init()


# Wrap parse_version so that it accepts numbers
def parse_version(version):
    return pkg_resources.parse_version(str(version))


# Handle args
args_parser = argparse.ArgumentParser(description="Display browser support stats")
args_parser.add_argument('--download', action='store_true')
args_parser.add_argument('--debug', action='store_true')
args_parser.add_argument('--sort-region', default='global')
cli_args = args_parser.parse_args()


# Optionally download fresh data
if cli_args.download:
    Path('data').mkdir(exist_ok=True)
    url_base = 'https://github.com/Fyrd/caniuse/raw/master/'
    resp = requests.get(f'{url_base}fulldata-json/data-2.0.json')
    Path('data/data.json').write_text(resp.text)
    for region in config.regions:
        resp = requests.get(f'{url_base}region-usage-json/{region}.json')
        Path(f'data/{region}.json').write_text(resp.text)


# Load data
try:
    agents = json.loads(Path('data/data.json').read_text())['agents']
    usage = {
        'global': {browser: agents[browser]['usage_global'] for browser in agents},
    }
    for region in config.regions:
        usage[region] = json.loads(Path(f'data/{region}.json').read_text())['data']
except FileNotFoundError as exc:
    sys.exit(f"Data not present ({exc.filename}). First run `stats.py --download`")


# Treat global as just another region
regions = ('global',) + config.regions


# Normalise versions for easier processing
for region in regions:
    for browser in usage[region]:
        for version in list(usage[region][browser].keys()):
            # Ensure Safari Tech Preview and op_mini's "all" included at top of versions
            if version in ('TP', 'all'):
                new_version = '9999'
            elif '-' in version:
                # Strip away end range if version is a range
                version.partition('-')[0]
            else:
                continue
            usage[region][browser][new_version] = usage[region][browser].pop(version)


# In regional data, versions for browsers with only one recorded often have key '0'
no_version_tracking = set()
for region in config.regions:
    for browser, versions in usage[region].items():
        if '0' in versions:
            if len(versions) == 1:
                # Likely a catch all version (when distinct version data not available)
                no_version_tracking.add(browser)
            # Assign the max version available, as that is what '0' usually represents
            # See https://github.com/Fyrd/caniuse/issues/1939
            max_global_version = max(iter(usage['global'][browser]), key=parse_version)
            usage[region][browser][max_global_version] = usage[region][browser].pop('0')


# Ensure browsers/versions match for global and regions (when debugging)
if cli_args.debug:
    for region in config.regions:
        different_browsers = set(usage[region].keys()) ^ set(usage['global'].keys())
        if different_browsers:
            warnings.warn(
                f"Browsers different between global and {region}: {different_browsers}")
        for browser in usage['global']:
            different_versions = \
                set(usage[region][browser].keys()) ^ set(usage['global'][browser].keys())
            if different_versions:
                warnings.warn(
                    f"{browser} versions different for global and {region}: {different_versions}")


# Init totals
percent_supported = {}
percent_not_supported = {}
percent_unknown = {}
browser_usage = {}
browser_support = {}


# Per region
for region in regions:

    # Init totals for region
    percent_supported[region] = 0
    percent_not_supported[region] = 0
    browser_usage[region] = {}
    browser_support[region] = {}

    # Apply data per browser
    for browser, versions in usage[region].items():

        # Sum total browser's usage
        browser_usage[region][browser] = sum(filter(None, versions.values()))

        # Unknown support if not specified
        browser_support[region][browser] = 0
        if browser not in config.supported:
            browser_support[region][browser] = '?'
            continue

        # Add to counts per version
        for version, percent in versions.items():
            percent = percent or 0  # Some are None
            if config.supported[browser] is not None and \
                    parse_version(version) >= parse_version(config.supported[browser]):
                percent_supported[region] += percent
                browser_support[region][browser] += percent
            else:
                percent_not_supported[region] += percent

    # Work out the unknown figure
    percent_unknown[region] = 100 - percent_supported[region] - percent_not_supported[region]


# Sort browsers in order of usage
browsers_by_usage = sorted(agents.keys(), reverse=True,
    key=lambda k: browser_usage[cli_args.sort_region][k])


# Helper to wrap a string in color codes
def apply_color(arg, color=None):
    return getattr(colorama.Fore, color.upper()) + arg + colorama.Style.RESET_ALL


# Helper to print a line of data
def print_line(*args, color=None, two_col=None):
    line = ''
    for i, arg in enumerate(args):
        # Extract color if given an (arg, color) tuple
        arg_color = None
        if isinstance(arg, tuple):
            arg, arg_color = arg
        # If a number, format to 1 decimal place
        arg = f"{arg:.1f}%" if isinstance(arg, (float, int)) else arg
        # Apply spacing (more if first arg or two column width)
        if i == 0:
            arg = f"{arg:<28}"
        else:
            arg = f"{arg:>8}"
            if two_col == 'right':
                arg = ' ' * 8 + arg
            if two_col == 'left':
                arg += ' ' * 8
        # Apply the color (after spacing as seems to affect it) and add to line
        line += apply_color(arg, arg_color) if arg_color else arg
    # Print the line with optional color for whole line
    print(apply_color(line, color) if color else line)


# Display results
print_line("Region", "Global", *config.regions, two_col='left')
print('')

print("Browser (total, support)")
for browser in browsers_by_usage:
    # Determine color
    if browser not in config.supported:
        color = 'yellow'
    else:
        color = 'red' if config.supported[browser] is None else 'green'
    # Get real browser name
    name = agents[browser]['browser']
    if browser in no_version_tracking:
        name += '*'
    if browser in config.supported:
        name += f" ({config.supported[browser]}+)"
    name = (name, color)
    # Sort figures and print
    figures = []
    for region in regions:
        figures.append((browser_usage[region][browser]))
        figures.append((browser_support[region][browser], color))
    print_line(name, *figures)
print('')

print("Total")
print_line('Supported', *percent_supported.values(), color='green', two_col='right')
print_line('Unknown', *percent_unknown.values(), color='yellow', two_col='right')
print_line('Not supported', *percent_not_supported.values(), color='red', two_col='right')

if no_version_tracking:
    print('')
    print('* No version tracking (any kind of support will match all versions)')
