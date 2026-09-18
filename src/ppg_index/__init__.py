"""Portfolio-Paycheck Gap Index."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("ppg-index")
except PackageNotFoundError:  # Source tree imported without installation.
    __version__ = "0+unknown"

__all__ = ["__version__"]
