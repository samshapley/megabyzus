#!/usr/bin/env python3
"""
Script to analyze the NASA data collection results without directly viewing the content.
"""

import os
import json
import sys

def get_file_size_formatted(size_in_bytes):
    """
    Convert bytes to a human-readable format.
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024 or unit == 'GB':
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024

def analyze_result_file(filepath):
    """
    Analyze a result file without viewing its full content directly.
    
    Args:
        filepath: Path to the result file
        
    Returns:
        dict: Analysis of the file
    """
    if not os.path.exists(filepath):
        print(f"Error: File {filepath} does not exist")
        return None
        
    try:
        file_size = os.path.getsize(filepath)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Extract only metadata and counts
        metadata = {
            "file_size": file_size,
            "file_size_formatted": get_file_size_formatted(file_size),
            "record_count": data.get("count", 0),
            "total_expected": data.get("total", 0),
            "api_type": data.get("api_type", "unknown"),
            "date_collected": data.get("date_collected", "unknown"),
        }
        
        return metadata
        
    except Exception as e:
        print(f"Error analyzing {filepath}: {e}")
        return None

def main():
    """
    Main function to analyze NASA data collection results.
    """
    results_dir = "results"
    
    if not os.path.exists(results_dir):
        print(f"Error: Results directory '{results_dir}' not found.")
        sys.exit(1)
    
    # Find result files
    result_files = []
    for filename in os.listdir(results_dir):
        if filename.startswith("nasa_") and filename.endswith(".json"):
            result_files.append(os.path.join(results_dir, filename))
    
    if not result_files:
        print("No NASA data collection result files found.")
        sys.exit(1)
    
    # Analyze each file
    total_records = 0
    total_size = 0
    results_by_type = {}
    
    for filepath in result_files:
        analysis = analyze_result_file(filepath)
        if analysis:
            api_type = analysis["api_type"]
            results_by_type[api_type] = analysis
            total_records += analysis["record_count"]
            total_size += analysis["file_size"]
    
    # Print summary
    print("\n" + "="*50)
    print("NASA TECHNOLOGY TRANSFER DATA COLLECTION SUMMARY")
    print("="*50)
    
    print(f"\nTotal records collected: {total_records}")
    print(f"Total data size: {get_file_size_formatted(total_size)}")
    
    print("\nBreakdown by type:")
    for api_type, data in sorted(results_by_type.items()):
        print(f"\n{api_type.upper()}:")
        print(f"  Records: {data['record_count']}")
        print(f"  Expected total: {data['total_expected']}")
        print(f"  File size: {data['file_size_formatted']}")
        print(f"  Date collected: {data['date_collected']}")
    
    print("\n" + "="*50)

if __name__ == "__main__":
    main()