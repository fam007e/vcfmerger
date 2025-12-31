def test_parse_simple_vcard(merger, simple_vcard):
    """Test parsing a standard VCF block."""
    props = merger.parse_vcard_properties(simple_vcard)

    assert props["FN"] == "John Doe"
    assert props["N"] == "Doe;John;;;"

    # Check sets contain tuple(normalized, original)
    tels = {item[0] for item in props["TEL"]}
    assert "1234567890" in tels

    emails = {item[0] for item in props["EMAIL"]}
    assert "john@example.com" in emails


def test_parse_complex_vcard(merger, complex_vcard):
    """Test parsing complex VCF block with photos and folding."""
    props = merger.parse_vcard_properties(complex_vcard)

    # Phone normalization check
    tels = {item[0] for item in props["TEL"]}
    assert "+15551234567" in tels

    # Photo check
    assert props["PHOTO"] is not None
    assert "ENCODING=b" in props["PHOTO"]

    # Check that other props captured the NOTE (even if folded)
    other_props = "\n".join(props["OTHER_PROPS"])
    assert "NOTE:This is a long note" in other_props


def test_parse_quoted_printable(merger):
    """Test parsing of Quoted-Printable encoded fields."""
    qp_vcard = """BEGIN:VCARD
VERSION:2.1
N;ENCODING=QUOTED-PRINTABLE:M=C3=BCller;Hans;;;
FN;ENCODING=QUOTED-PRINTABLE:Hans M=C3=BCller
END:VCARD"""

    props = merger.parse_vcard_properties(qp_vcard)
    assert props["FN"] == "Hans Müller"
    assert props["N"] == "Müller;Hans;;;"
