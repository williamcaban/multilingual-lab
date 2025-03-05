#!/usr/bin/env python3

# # Basic usage - read line 5
# python jsonl_parser.py data.jsonl 5

# # Export parsed JSON to a file
# python jsonl_parser.py data.jsonl 5 -o output.json

# # Show only the parsed metadata
# python jsonl_parser.py data.jsonl 5 -m

import json
import sys
import argparse


def parse_jsonl_line(file_path, line_number):
    """
    Read and parse a specific line from a JSONL file.
    If the JSON contains a 'metadata' field that is a JSON string,
    it will parse that as well.
    
    Args:
        file_path (str): Path to the JSONL file
        line_number (int): Line number to read (1-based indexing)
    
    Returns:
        dict: Parsed JSON object from the specified line with metadata parsed
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Skip to the desired line
            for i, line in enumerate(file, 1):
                if i == line_number:
                    line = line.strip()
                    if not line:  # Skip empty lines
                        print(f"Line {line_number} is empty.")
                        return None

                    try:
                        # Parse the main JSON object
                        json_obj = json.loads(line)

                        # Check if there's a metadata field that's a string
                        if 'metadata' in json_obj and isinstance(json_obj['metadata'], str):
                            try:
                                # Parse the metadata string as JSON
                                json_obj['metadata'] = json.loads(
                                    json_obj['metadata'])
                                print("Successfully parsed nested metadata JSON.")
                            except json.JSONDecodeError as e:
                                print(
                                    f"Warning: Couldn't parse metadata as JSON: {e}")

                        # Print formatted JSON with metadata parsed
                        print(json.dumps(json_obj, indent=2, ensure_ascii=False))

                        return json_obj
                    except json.JSONDecodeError as e:
                        print(f"Error parsing JSON on line {line_number}: {e}")
                        print(f"Raw line content: {line[:100]}..." if len(
                            line) > 100 else line)
                        return None

            # If we get here, the requested line wasn't found
            print(f"Error: Line {line_number} not found in the file.")
            return None

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None


def export_to_file(json_obj, output_file):
    """Export the parsed JSON to a file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(json_obj, f, indent=2, ensure_ascii=False)
    print(f"JSON exported to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Parse a specific line from a JSONL file and handle nested metadata.')
    parser.add_argument('file_path', help='Path to the JSONL file')
    parser.add_argument('line_number', type=int,
                        help='Line number to read (1-based indexing)')
    parser.add_argument(
        '-o', '--output', help='Output file to save the parsed JSON')
    parser.add_argument('-m', '--metadata-only', action='store_true',
                        help='Output only the parsed metadata field')

    args = parser.parse_args()

    if args.line_number < 1:
        print("Error: Line number must be a positive integer.")
        sys.exit(1)

    json_obj = parse_jsonl_line(args.file_path, args.line_number)

    if json_obj and args.metadata_only and 'metadata' in json_obj:
        # If metadata-only flag is set, print only the metadata
        if isinstance(json_obj['metadata'], dict):
            print("\nMetadata only:")
            print(json.dumps(json_obj['metadata'],
                  indent=2, ensure_ascii=False))
        else:
            print("\nMetadata is not a JSON object.")

    if json_obj and args.output:
        export_to_file(json_obj, args.output)


if __name__ == "__main__":
    main()
