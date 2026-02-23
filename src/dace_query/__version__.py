import sys
import warnings

major, minor, micro = sys.version_info.major, sys.version_info.minor, sys.version_info.micro

# Support, will be deprecated
if major >= 3 and minor >= 8:
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

__py_version__ = '.'.join(map(str, [major, minor, micro]))


# If we are in a pre-release version, we want to warn the user that this version is for testing purposes only and implies no support.
if "dev" in __version__ or "rc" in __version__:
    WARNING_MSG = (
        f"\n{'!'*60}\n"
        f"DISCLAIMER: You are using a PRE-RELEASE version ({__version__}).\n"
        "This version is for testing purposes only and implies NO SUPPORT. (breaking changes may occur between pre-releases)\n"
        "It is not recommended to use this version of dace-query for any scientific work.\n"
        "You may install the stable version via: pip install dace-query\n"
        f"{'!'*60}\n"
    )
    
    # UserWarning is standard, but you can use simple print() if you prefer
    warnings.warn(WARNING_MSG, UserWarning, stacklevel=2)