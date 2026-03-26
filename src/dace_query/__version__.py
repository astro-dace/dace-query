import subprocess
import sys
import requests

# Check if the current version is the latest
def get_latest_version(pypi_url, package_name):
    try:
        response = requests.get(f'{pypi_url}{package_name}/json', timeout=0.5) # Only wait for 0.5 seconds to avoid blocking the user if there are network issues
        releases = list(response.json()['releases'].keys())
        latest_version = releases[-1]
    except Exception as e:
        latest_version = None
    
    return latest_version

# Extract the major, minor and micro version numbers from a version string
def extract_minor_major_micro_from_version(version):
    try:
        major, minor, micro = map(int, version.split('.'))
    except Exception as e:
        try:
            major, minor, micro = map(str, version.split('.'))
        except Exception as exp:
            major, minor, micro = (0, 0, 0)
    return major, minor, micro

python_major, python_minor, python_micro = sys.version_info.major, sys.version_info.minor, sys.version_info.micro

# Support, will be deprecated
if python_major >= 3 and python_minor >= 8:
    from importlib.metadata import metadata, PackageNotFoundError
else:
    from importlib_metadata import metadata, PackageNotFoundError

# Define the package name
__pkg_name__ = __package__  # Can be replaced by __package__ if root folder and package are the same

try:
    __title__ = metadata(__pkg_name__)['name']
    __version__ = metadata(__pkg_name__)['version']
except PackageNotFoundError:
    __title__ = 'dev'
    __version__ = '0.0.0-dev'

__py_version__ = '.'.join(map(str, [python_major, python_minor, python_micro]))

pypi_url = 'https://pypi.org/pypi/'

# If we are in a pre-release version, we want to warn the user that this version is for testing purposes only and implies no support.
if "dev" in __version__ or "rc" in __version__:
    pypi_url = 'https://test.pypi.org/pypi/'  # Use Test PyPI for pre-releases
    
    WARNING_MSG = (
        f"\n{'!'*60}\n"
        f"DISCLAIMER: You are using a PRE-RELEASE version ({__version__}).\n"
        "This version is for testing purposes only and implies NO SUPPORT. (breaking changes may occur between pre-releases)\n"
        "It is not recommended to use this version of dace-query for any scientific work.\n"
        "You may install the stable version via: pip install dace-query\n"
        f"{'!'*60}\n"
    )
    
    print(WARNING_MSG)
    
    
# Get the latest version available on PyPI and extract the major, minor and micro version numbers
latest = get_latest_version(pypi_url, 'dace-query')
current_major, current_minor, current_micro = extract_minor_major_micro_from_version(__version__)
latest_major, latest_minor, latest_micro = extract_minor_major_micro_from_version(latest)

# Do an int or str comparison depending on the type of the version numbers (pre-releases may contain strings)
if (latest_major, latest_minor, latest_micro) > (current_major, current_minor, current_micro):
    if latest_major == current_major:
        print(f"[dace-query] Update available: {__version__} → {latest}")
    else:
        print(f"[dace-query] Major update available: {__version__} → {latest} (might have breaking changes, check the changelog before updating)")
