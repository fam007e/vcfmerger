#!/usr/bin/env python3
"""
A script to merge and deduplicate VCF contact files.

This script reads multiple VCF (vCard) files, parses their contact information,
and merges them into a single output VCF file. It performs intelligent
deduplication based on normalized full names, phone numbers, and email addresses.
Properties from later-processed files are prioritized for single-value fields,
while multi-value fields are combined.
"""

import re
import sys
import argparse
import logging
import quopri
from typing import Dict, List, Tuple, Any

# Try to get version from installed package, otherwise fallback
if sys.version_info >= (3, 8):
    from importlib import metadata
else:
    import importlib_metadata as metadata

try:
    __version__ = metadata.version("vcf-merger")
except metadata.PackageNotFoundError:
    __version__ = "0.0.0-dev"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class VCFMerger:
    """A class to handle VCF contact file merging and deduplication."""

    def __init__(self):
        """Initialize the VCF merger."""
        self.merged_contacts_data: Dict[Tuple, Dict[str, Any]] = {}

    @staticmethod
    def normalize_phone(phone: str) -> str:
        """
        Normalize a phone number by removing non-digit characters except '+'.

        Args:
            phone: The phone number to normalize

        Returns:
            Normalized phone number string
        """
        return re.sub(r'[^0-9+]', '', phone)

    @staticmethod
    def normalize_email(email: str) -> str:
        """
        Normalize an email address by converting it to lowercase.

        Args:
            email: The email address to normalize

        Returns:
            Normalized email address string
        """
        return email.lower()

    def parse_vcard_properties(self, vcard_block: str) -> Dict[str, Any]:
        """
        Parse a single VCARD block and extract its properties into a dictionary.

        Handles unfolding lines, quoted-printable decoding, and categorizes properties.

        Args:
            vcard_block: Raw vCard block string

        Returns:
            Dictionary containing parsed contact properties
        """
        contact_props = {
            'FN': None,
            'N': None,
            'TEL': set(),  # Stores (normalized_phone, original_line)
            'EMAIL': set(),  # Stores (normalized_email, original_line)
            'URL': set(),
            'ADR': set(),
            'ORG': None,
            'TITLE': None,
            'PHOTO': None,
            'VERSION': None,
            'OTHER_PROPS': set()  # Stores other unique property lines
        }

        # Unfold lines
        unfolded_block = re.sub(r'\r?\n[ \t]', '', vcard_block)

        photo_lines = []
        in_photo_block = False

        for line in unfolded_block.splitlines():
            if not line.strip():
                continue

            if line.startswith('PHOTO;'):
                in_photo_block = True
                photo_lines.append(line)
                continue

            if in_photo_block and (line.startswith(' ') or line.startswith('\t')):
                photo_lines.append(line)
                continue

            if in_photo_block:  # End of photo block
                in_photo_block = False

            parts = line.split(':', 1)
            if len(parts) != 2:
                contact_props['OTHER_PROPS'].add(line)
                continue

            key_part, value = parts
            main_key = key_part.split(';')[0]

            # Decode quoted-printable if present
            if 'ENCODING=QUOTED-PRINTABLE' in key_part:
                try:
                    value = quopri.decodestring(value).decode('utf-8', 'ignore')
                except (TypeError, ValueError):
                    pass  # Keep original value if decoding fails

            self._process_property(contact_props, main_key, value, line)

        if photo_lines:
            contact_props['PHOTO'] = '\n'.join(photo_lines)

        return contact_props

    def _process_property(self, contact_props: Dict[str, Any], main_key: str,
                         value: str, line: str) -> None:
        """
        Process a single vCard property and add it to the contact properties.

        Args:
            contact_props: Dictionary to store contact properties
            main_key: The main property key (e.g., 'FN', 'TEL')
            value: The property value
            line: The original line for preservation
        """
        if main_key == 'FN':
            contact_props['FN'] = value.strip()
        elif main_key == 'N':
            contact_props['N'] = value.strip()
        elif main_key == 'TEL':
            contact_props['TEL'].add((self.normalize_phone(value), line))
        elif main_key == 'EMAIL':
            contact_props['EMAIL'].add((self.normalize_email(value), line))
        elif main_key == 'URL':
            contact_props['URL'].add(line)
        elif main_key == 'ADR':
            contact_props['ADR'].add(line)
        elif main_key == 'ORG':
            contact_props['ORG'] = value.strip()
        elif main_key == 'TITLE':
            contact_props['TITLE'] = value.strip()
        elif main_key == 'VERSION':
            contact_props['VERSION'] = value.strip()
        else:
            contact_props['OTHER_PROPS'].add(line)

    def _get_contact_key(self, contact_props: Dict[str, Any]) -> Tuple:
        """
        Generate a unique key for a contact for duplicate detection.

        Args:
            contact_props: Dictionary containing contact properties

        Returns:
            Tuple representing unique contact key
        """
        normalized_fn = (contact_props['FN'] or contact_props['N'] or '').lower()
        normalized_tels = frozenset(item[0] for item in contact_props['TEL'])
        normalized_emails = frozenset(item[0] for item in contact_props['EMAIL'])
        return (normalized_fn, normalized_tels, normalized_emails)

    def _merge_contact_properties(self, existing_props: Dict[str, Any],
                                 new_props: Dict[str, Any]) -> None:
        """
        Merge properties from a new contact into an existing one.

        Args:
            existing_props: Existing contact properties to merge into
            new_props: New contact properties to merge from
        """
        # Single-value fields: prioritize new_props
        single_value_fields = ['FN', 'N', 'ORG', 'TITLE', 'PHOTO', 'VERSION']
        for prop_name in single_value_fields:
            if new_props[prop_name]:
                existing_props[prop_name] = new_props[prop_name]

        # Multi-value fields: combine sets
        multi_value_fields = ['TEL', 'EMAIL', 'URL', 'ADR', 'OTHER_PROPS']
        for field in multi_value_fields:
            existing_props[field].update(new_props[field])

    def _generate_vcard_output(self, contact_props: Dict[str, Any]) -> str:
        """
        Generate a single VCARD string from contact properties.

        Args:
            contact_props: Dictionary containing contact properties

        Returns:
            Formatted vCard string
        """
        vcard_lines = ['BEGIN:VCARD']
        vcard_lines.append('VERSION:3.0')  # Standardize to VCF 3.0

        if contact_props['FN']:
            vcard_lines.append(f"FN:{contact_props['FN']}")

        if contact_props['N']:
            vcard_lines.append(f"N:{contact_props['N']}")
        elif contact_props['FN']:
            vcard_lines.append(f"N:;{contact_props['FN']};;;")

        if contact_props['ORG']:
            vcard_lines.append(f"ORG:{contact_props['ORG']}")
        if contact_props['TITLE']:
            vcard_lines.append(f"TITLE:{contact_props['TITLE']}")

        # Add phone numbers
        for _, original_line in sorted(contact_props['TEL']):
            vcard_lines.append(original_line)

        # Add email addresses
        for _, original_line in sorted(contact_props['EMAIL']):
            vcard_lines.append(original_line)

        # Add other multi-value properties
        for line in sorted(contact_props['URL']):
            vcard_lines.append(line)
        for line in sorted(contact_props['ADR']):
            vcard_lines.append(line)
        for line in sorted(contact_props['OTHER_PROPS']):
            vcard_lines.append(line)

        if contact_props['PHOTO']:
            vcard_lines.append(contact_props['PHOTO'])

        vcard_lines.append('END:VCARD')
        return '\n'.join(vcard_lines)

    def merge_vcfs(self, vcf_contents_list: List[str]) -> str:
        """
        Merge contacts from a list of VCF content strings.

        Deduplicates based on normalized FN, TELs, and EMAILs.
        Prioritizes properties from later-processed files.

        Args:
            vcf_contents_list: List of VCF file contents as strings

        Returns:
            Merged VCF content as a string
        """
        self.merged_contacts_data = {}
        logger.info("\n--- Starting VCF Merge Process ---")

        for i, vcf_content in enumerate(vcf_contents_list):
            file_info = f"Processing input file {i+1}/{len(vcf_contents_list)}"
            logger.info("\n[INFO] %s...", file_info)
            pattern = r'BEGIN:VCARD.*?END:VCARD'
            vcard_blocks = re.findall(pattern, vcf_content, re.DOTALL)

            for block in vcard_blocks:
                current_contact_props = self.parse_vcard_properties(block)
                contact_key = self._get_contact_key(current_contact_props)
                contact_name = self._get_contact_display_name(current_contact_props)

                if contact_key not in self.merged_contacts_data:
                    self.merged_contacts_data[contact_key] = current_contact_props
                    logger.info("  [INFO] Added new contact: '%s'.", contact_name)
                else:
                    existing_contact_props = self.merged_contacts_data[contact_key]

                    logger.info("  [DUPLICATE DETECTED] Contact '%s' found. "
                                "Merging properties.", contact_name)

                    self._merge_contact_properties(existing_contact_props,
                                                  current_contact_props)

                    logger.info("  [MERGED] Properties for '%s' have been combined.",
                                contact_name)

        logger.info("\n--- VCF Merge Process Complete ---")

        final_vcf_output = []
        for contact_key in sorted(self.merged_contacts_data.keys()):
            contact_props = self.merged_contacts_data[contact_key]
            final_vcf_output.append(self._generate_vcard_output(contact_props))

        return '\n'.join(final_vcf_output)

    def _get_contact_display_name(self, contact_props: Dict[str, Any]) -> str:
        """
        Get a display name for the contact for logging purposes.

        Args:
            contact_props: Dictionary containing contact properties

        Returns:
            Display name string
        """
        return (contact_props['FN'] or
                self._get_contact_key(contact_props)[0] or
                'Unknown Contact')


def read_vcf_files(file_paths: List[str]) -> List[str]:
    """
    Read VCF files and return their contents.

    Args:
        file_paths: List of file paths to read

    Returns:
        List of file contents as strings
    """
    vcf_contents = []
    for path in file_paths:
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as file:
                vcf_contents.append(file.read())
        except FileNotFoundError:
            logger.error("Error: Input file '%s' not found. Skipping this file.", path)
        except IOError as error:
            logger.error("Error reading file '%s': %s. "
                         "Skipping this file.", path, error)

    return vcf_contents


def write_output_file(output_path: str, content: str) -> bool:
    """
    Write merged content to output file.

    Args:
        output_path: Path to output file
        content: Content to write

    Returns:
        True if successful, False otherwise
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(content)
        logger.info("\nSuccessfully merged contacts into '%s'", output_path)
        return True
    except IOError as error:
        logger.error("An IOError occurred while writing the output file: %s", error)
        return False
    except Exception as error:  # pylint: disable=broad-except
        logger.error("An unexpected error occurred while writing the output file: %s",
                     error)
        return False


def main() -> None:
    """Main function to handle command line arguments and execute merge."""
    parser = argparse.ArgumentParser(
        description="Merge and deduplicate VCF contact files."
    )

    parser.add_argument(
        "output_file",
        help="Path to the output VCF file"
    )
    parser.add_argument(
        "input_files",
        nargs="+",
        help="Paths to input VCF files"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )

    args = parser.parse_args()

    # Configure logging based on verbose flag
    if args.verbose:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.WARNING)

    # Read input files
    vcf_contents = read_vcf_files(args.input_files)

    if not vcf_contents:
        logger.error("No valid input VCF files found to merge. Exiting.")
        sys.exit(1)

    # Merge VCF files
    merger = VCFMerger()
    merged_data_output = merger.merge_vcfs(vcf_contents)

    # Write output file
    if not write_output_file(args.output_file, merged_data_output):
        sys.exit(1)


if __name__ == '__main__':
    main()
