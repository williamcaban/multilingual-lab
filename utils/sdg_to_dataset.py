import json
import pandas as pd
import argparse
import os
import sys

###
# pip install pandas pyarrow
###

def process_jsonl(file_path):
    """
    Process a JSONL file with nested structures including metadata JSON string,
    and convert to a pandas DataFrame with flattened columns.
    
    Args:
        file_path (str): Path to the JSONL file
        
    Returns:
        pd.DataFrame: Processed DataFrame with flattened columns
    """
    # List to hold the processed records
    records = []
    
    # Read the JSONL file line by line
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if not line.strip():
                continue
                
            # Parse the JSON line
            data = json.loads(line)
            
            # Create a record dictionary that will contain all flattened fields
            record = {}
            
            # Process the messages field
            if 'messages' in data:
                for i, message in enumerate(data['messages']):
                    # Add message content with index to maintain order
                    record[f'message_{i}_role'] = message.get('role', '')
                    record[f'message_{i}_content'] = message.get('content', '')
            
            # Process the metadata field - parse the JSON string into a dict
            if 'metadata' in data and data['metadata']:
                try:
                    metadata_dict = json.loads(data['metadata'])
                    
                    # Add each metadata field with the prefix 'metadata_'
                    for key, value in metadata_dict.items():
                        record[f'metadata_{key}'] = value
                except json.JSONDecodeError:
                    # Handle case where metadata is not valid JSON
                    record['metadata_raw'] = data['metadata']
            
            # Add the ID field if it exists
            if 'id' in data:
                record['id'] = data['id']
                
            # Add the record to our collection
            records.append(record)
    
    # Convert the records to a DataFrame
    df = pd.DataFrame(records)
    
    return df

def save_to_parquet(df, output_path):
    """
    Save the DataFrame to a parquet file
    
    Args:
        df (pd.DataFrame): DataFrame to save
        output_path (str): Path where to save the parquet file
    """
    df.to_parquet(output_path, index=False)
    print(f"Data saved to {output_path}")

def save_to_csv(df, output_path):
    """
    Save the DataFrame to a CSV file
    
    Args:
        df (pd.DataFrame): DataFrame to save
        output_path (str): Path where to save the CSV file
    """
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"Data saved to {output_path}")

def parse_arguments():
    """
    Parse command line arguments
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description='Convert JSONL dataset to DataFrame and save as parquet or csv')
    
    parser.add_argument('--input', '-i', type=str, default='dataset.jsonl',
                        help='Input JSONL file path (default: dataset.jsonl)')
    
    parser.add_argument('--output', '-o', type=str, default=None,
                        help='Output file path (default: based on input filename with .parquet extension)')
    
    parser.add_argument('--format', '-f', type=str, choices=['parquet', 'csv'], default='parquet',
                        help='Output file format (default: parquet)')
    
    return parser.parse_args()

def main():
    # Parse command line arguments
    args = parse_arguments()
    
    # Set input file path
    input_file = args.input
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        sys.exit(1)
    
    # Set output file path if not provided
    if args.output is None:
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        args.output = f"{base_name}.{args.format}"
    
    # Process the JSONL file
    print(f"Processing JSONL file: {input_file}...")
    try:
        df = process_jsonl(input_file)
    except Exception as e:
        print(f"Error processing JSONL file: {str(e)}")
        sys.exit(1)
    
    # Display DataFrame information
    print("\nDataFrame Information:")
    print(f"Number of rows: {len(df)}")
    print(f"Columns: {', '.join(df.columns)}")
    
    # Save to specified format
    try:
        if args.format == 'parquet':
            save_to_parquet(df, args.output)
        else:  # csv
            save_to_csv(df, args.output)
    except Exception as e:
        print(f"Error saving file: {str(e)}")
        sys.exit(1)
    
    print("Processing completed successfully.")
    return df.head(2)

if __name__ == "__main__":
    df_sample = main()
    print("\nSample of processed data:")
    print(df_sample)