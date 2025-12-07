"""A Python utility for merging and deduplicating VCF contact files."""

__version__ = '1.0.0'
__author__ = 'Faisal Ahmed Moshiur'
__email__ = 'faisalmoshiur+vcfmerger@gmail.com'
__license__ = 'MIT'

# Import main components from merge_script module
try:
    from merge_script import VCFMerger, main
    __all__ = ['VCFMerger', 'main']
except ImportError:
    # Handle case where merge_script might not be available yet
    __all__ = []
