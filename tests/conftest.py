import pytest

from merge_script import VCFMerger


@pytest.fixture
def merger():
    """Returns a VCFMerger instance."""
    return VCFMerger()


@pytest.fixture
def simple_vcard():
    """Returns a simple VCF block string."""
    return """BEGIN:VCARD
VERSION:3.0
FN:John Doe
N:Doe;John;;;
TEL;TYPE=CELL:1234567890
EMAIL;TYPE=HOME:john@example.com
END:VCARD"""


@pytest.fixture
def complex_vcard():
    """Returns a VCF block with complex fields (photo, wrapped lines)."""
    return """BEGIN:VCARD
VERSION:3.0
FN:Jane Smith
N:Smith;Jane;;;
TEL;TYPE=WORK:+1 (555) 123-4567
EMAIL;TYPE=WORK:jane.smith@example.corp
PHOTO;ENCODING=b;TYPE=JPEG:
 iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42Y
 AAAAASUVORK5CYII=
NOTE:This is a long note that should be
  unfolded by the parser.
END:VCARD"""
