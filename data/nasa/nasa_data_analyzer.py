#!/usr/bin/env python3
"""
NASA Technology Transfer API Data Analyzer

This script analyzes the data collected by nasa_api_collector.py without directly
viewing the full content. It generates statistical summaries and insights about
NASA's technology transfer data, particularly focusing on defense-related technologies.
"""

import os
import json
import argparse
import logging
from collections import Counter
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
import numpy as np
import re

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nasa_data_analyzer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
RESULTS_DIR = "results"
ANALYSIS_DIR = "analysis"
API_TYPES = ["patent", "software", "spinoff"]

# Ensure analysis directory exists
if not os.path.exists(ANALYSIS_DIR):
    os.makedirs(ANALYSIS_DIR)
    logger.info(f"Created analysis directory: {ANALYSIS_DIR}")

def load_data_file(filepath):
    """
    Load a JSON data file.
    
    Args:
        filepath (str): Path to the JSON file
        
    Returns:
        dict: The loaded data or None if there was an error
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Loaded data from {filepath} ({len(data.get('results', []))} records)")
        return data
    except Exception as e:
        logger.error(f"Error loading data from {filepath}: {e}")
        return None

def load_all_data(combined=True):
    """
    Load all data files for analysis.
    
    Args:
        combined (bool): Whether to load combined result files or individual files
        
    Returns:
        dict: Dictionary with API types as keys and loaded data as values
    """
    all_data = {}
    
    for api_type in API_TYPES:
        if combined:
            # Look for combined results file
            filepath = f"{RESULTS_DIR}/nasa_{api_type}_combined.json"
            if os.path.exists(filepath):
                all_data[api_type] = load_data_file(filepath)
        else:
            # Load all individual files for this API type
            pattern = f"nasa_{api_type}_"
            results = []
            
            for filename in os.listdir(RESULTS_DIR):
                if filename.startswith(pattern) and filename.endswith(".json"):
                    filepath = os.path.join(RESULTS_DIR, filename)
                    data = load_data_file(filepath)
                    if data and 'results' in data:
                        results.extend(data['results'])
            
            if results:
                all_data[api_type] = {
                    "results": results,
                    "count": len(results),
                    "api_type": api_type
                }
                logger.info(f"Combined {len(results)} records for {api_type} from individual files")
    
    return all_data

def analyze_technology_counts(data):
    """
    Analyze the total count of technologies across different API types.
    
    Args:
        data (dict): Loaded data with API types as keys
        
    Returns:
        dict: Analysis results
    """
    results = {
        "total_technologies": 0,
        "counts_by_type": {},
        "date_analyzed": datetime.now().isoformat()
    }
    
    for api_type, api_data in data.items():
        if api_data and 'results' in api_data:
            count = len(api_data['results'])
            results["counts_by_type"][api_type] = count
            results["total_technologies"] += count
    
    return results

def analyze_nasa_centers(data):
    """
    Analyze the distribution of technologies across NASA centers.
    
    Args:
        data (dict): Loaded data with API types as keys
        
    Returns:
        dict: Analysis results with center statistics
    """
    centers = Counter()
    centers_by_type = {api_type: Counter() for api_type in data.keys()}
    total_records = 0
    
    for api_type, api_data in data.items():
        if api_data and 'results' in api_data:
            for result in api_data['results']:
                # Center is typically at index 9 in the result array
                if len(result) > 9 and result[9]:
                    center = result[9]
                    centers[center] += 1
                    centers_by_type[api_type][center] += 1
                    total_records += 1
    
    # Calculate percentages
    center_percentages = {center: count/total_records*100 for center, count in centers.items()}
    
    return {
        "total_records_with_centers": total_records,
        "center_counts": dict(centers.most_common()),
        "center_percentages": center_percentages,
        "centers_by_type": {api_type: dict(counter.most_common()) for api_type, counter in centers_by_type.items()}
    }

def analyze_categories(data):
    """
    Analyze the distribution of technologies across categories.
    
    Args:
        data (dict): Loaded data with API types as keys
        
    Returns:
        dict: Analysis results with category statistics
    """
    categories = Counter()
    categories_by_type = {api_type: Counter() for api_type in data.keys()}
    total_records = 0
    
    for api_type, api_data in data.items():
        if api_data and 'results' in api_data:
            for result in api_data['results']:
                # Category is typically at index 5 in the result array
                if len(result) > 5 and result[5]:
                    category = result[5]
                    categories[category] += 1
                    categories_by_type[api_type][category] += 1
                    total_records += 1
    
    # Calculate percentages
    category_percentages = {category: count/total_records*100 for category, count in categories.items()}
    
    return {
        "total_records_with_categories": total_records,
        "category_counts": dict(categories.most_common()),
        "category_percentages": category_percentages,
        "categories_by_type": {api_type: dict(counter.most_common()) for api_type, counter in categories_by_type.items()}
    }

def analyze_defense_relevance(data):
    """
    Analyze the relevance of technologies to defense applications.
    
    Args:
        data (dict): Loaded data with API types as keys
        
    Returns:
        dict: Analysis results with defense relevance statistics
    """
    # Define defense-related keywords
    defense_keywords = [
        "defense", "military", "weapon", "armor", "missile", 
        "radar", "surveillance", "security", "protection", 
        "stealth", "tactical", "combat", "warfighter"
    ]
    
    # Compile regex pattern for case-insensitive matching
    pattern = re.compile(r'\b(' + '|'.join(defense_keywords) + r')\b', re.IGNORECASE)
    
    defense_counts = {api_type: 0 for api_type in data.keys()}
    defense_relevance_scores = []
    total_technologies = 0
    
    for api_type, api_data in data.items():
        if api_data and 'results' in api_data:
            for result in api_data['results']:
                total_technologies += 1
                
                # Check description (index 3) for defense keywords
                if len(result) > 3 and result[3]:
                    description = result[3]
                    matches = pattern.findall(description)
                    
                    # If defense keywords found, increment count
                    if matches:
                        defense_counts[api_type] += 1
                        
                        # Calculate a simple relevance score based on keyword frequency
                        relevance_score = len(matches) / len(description.split()) * 100
                        
                        # Store relevance data without storing full content
                        defense_relevance_scores.append({
                            "api_type": api_type,
                            "id": result[0] if len(result) > 0 else "unknown",
                            "case_number": result[1] if len(result) > 1 else "unknown",
                            "relevance_score": relevance_score,
                            "keywords_matched": len(set(matches))
                        })
    
    total_defense_related = sum(defense_counts.values())
    
    return {
        "total_technologies": total_technologies,
        "defense_related_count": total_defense_related,
        "defense_percentage": (total_defense_related / total_technologies * 100) if total_technologies > 0 else 0,
        "defense_counts_by_type": defense_counts,
        "top_defense_technologies": sorted(defense_relevance_scores, key=lambda x: x["relevance_score"], reverse=True)[:20],
        "average_relevance_score": sum(item["relevance_score"] for item in defense_relevance_scores) / len(defense_relevance_scores) if defense_relevance_scores else 0
    }

def generate_visualizations(analysis_results, output_dir=ANALYSIS_DIR):
    """
    Generate visualizations based on analysis results.
    
    Args:
        analysis_results (dict): The combined analysis results
        output_dir (str): Directory to save visualization files
    """
    try:
        # Set style for plots
        plt.style.use('ggplot')
        
        # 1. Technology Counts by Type
        technology_counts = analysis_results.get("technology_counts", {}).get("counts_by_type", {})
        if technology_counts:
            fig, ax = plt.subplots(figsize=(10, 6))
            bars = ax.bar(technology_counts.keys(), technology_counts.values())
            
            # Add count labels on top of bars
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{height}',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3),
                           textcoords="offset points",
                           ha='center', va='bottom')
            
            ax.set_title('NASA Technology Transfer: Count by Type')
            ax.set_ylabel('Number of Technologies')
            ax.set_ylim(0, max(technology_counts.values()) * 1.1)  # Add 10% padding
            
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'technology_counts_by_type.png'))
            plt.close()
            logger.info("Generated technology counts visualization")
            
        # 2. Top NASA Centers
        centers = analysis_results.get("nasa_centers", {}).get("center_counts", {})
        if centers:
            # Get top centers
            top_centers = dict(sorted(centers.items(), key=lambda x: x[1], reverse=True)[:10])
            
            fig, ax = plt.subplots(figsize=(12, 8))
            bars = ax.barh(list(top_centers.keys()), list(top_centers.values()))
            
            # Add count labels on bars
            for bar in bars:
                width = bar.get_width()
                ax.annotate(f'{int(width)}',
                           xy=(width, bar.get_y() + bar.get_height() / 2),
                           xytext=(3, 0),
                           textcoords="offset points",
                           ha='left', va='center')
            
            ax.set_title('Top NASA Centers Contributing to Technology Transfer')
            ax.set_xlabel('Number of Technologies')
            ax.invert_yaxis()  # Invert y-axis to show highest count at top
            
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'top_nasa_centers.png'))
            plt.close()
            logger.info("Generated NASA centers visualization")
            
        # 3. Defense-Related Technologies
        defense_data = analysis_results.get("defense_relevance", {})
        if defense_data and "defense_counts_by_type" in defense_data:
            counts_by_type = defense_data["defense_counts_by_type"]
            
            # Create percentage data
            total_by_type = analysis_results.get("technology_counts", {}).get("counts_by_type", {})
            percentages = {}
            
            for api_type, count in counts_by_type.items():
                if api_type in total_by_type and total_by_type[api_type] > 0:
                    percentages[api_type] = count / total_by_type[api_type] * 100
            
            # Create a side-by-side bar chart
            fig, ax = plt.subplots(figsize=(10, 6))
            x = np.arange(len(counts_by_type))
            width = 0.35
            
            bars1 = ax.bar(x - width/2, counts_by_type.values(), width, label='Count')
            bars2 = ax.bar(x + width/2, percentages.values(), width, label='Percentage (%)')
            
            # Add count labels
            for bar in bars1:
                height = bar.get_height()
                ax.annotate(f'{int(height)}',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3),
                           textcoords="offset points",
                           ha='center', va='bottom')
            
            # Add percentage labels
            for bar in bars2:
                height = bar.get_height()
                ax.annotate(f'{height:.1f}%',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3),
                           textcoords="offset points",
                           ha='center', va='bottom')
            
            ax.set_title('Defense-Related Technologies by Type')
            ax.set_xticks(x)
            ax.set_xticklabels(counts_by_type.keys())
            ax.legend()
            
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'defense_technologies.png'))
            plt.close()
            logger.info("Generated defense technologies visualization")
            
        # 4. Top Categories Pie Chart
        categories = analysis_results.get("categories", {}).get("category_counts", {})
        if categories:
            # Get top categories
            top_categories = dict(sorted(categories.items(), key=lambda x: x[1], reverse=True)[:8])
            
            # Add "Other" category for the rest
            other_count = sum(count for category, count in categories.items() 
                             if category not in top_categories)
            if other_count > 0:
                top_categories["Other"] = other_count
            
            fig, ax = plt.subplots(figsize=(10, 8))
            wedges, texts, autotexts = ax.pie(top_categories.values(), 
                                             labels=top_categories.keys(),
                                             autopct='%1.1f%%',
                                             textprops={'fontsize': 9})
            
            # Equal aspect ratio ensures that pie is drawn as a circle
            ax.set_title('Technology Categories Distribution')
            ax.axis('equal')
            
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'category_distribution.png'))
            plt.close()
            logger.info("Generated categories visualization")
            
        logger.info(f"All visualizations saved to {output_dir}")
            
    except Exception as e:
        logger.error(f"Error generating visualizations: {e}")

def save_analysis_results(results, filename="nasa_tech_analysis.json"):
    """
    Save analysis results to a JSON file.
    
    Args:
        results (dict): Analysis results to save
        filename (str): Name of the output file
    """
    filepath = os.path.join(ANALYSIS_DIR, filename)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info(f"Analysis results saved to {filepath}")
    except Exception as e:
        logger.error(f"Error saving analysis results to {filepath}: {e}")

def generate_html_report(analysis_results, filename="nasa_tech_report.html"):
    """
    Generate an HTML report from the analysis results.
    
    Args:
        analysis_results (dict): The analysis results
        filename (str): Name of the output HTML file
    """
    filepath = os.path.join(ANALYSIS_DIR, filename)
    
    try:
        # Create basic report structure
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>NASA Technology Transfer Analysis</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; color: #333; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                h1, h2, h3 {{ color: #0B3D91; }}
                .section {{ margin-bottom: 30px; background-color: #f9f9f9; padding: 20px; border-radius: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
                th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #0B3D91; color: white; }}
                tr:hover {{ background-color: #f5f5f5; }}
                .chart-container {{ margin-top: 20px; text-align: center; }}
                .chart {{ max-width: 100%; height: auto; margin-bottom: 20px; }}
                .summary {{ font-size: 1.1em; line-height: 1.6; }}
                .footer {{ margin-top: 50px; text-align: center; font-size: 0.9em; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>NASA Technology Transfer Analysis Report</h1>
                <p class="summary">Analysis of NASA's Technology Transfer Program data, with focus on defense-related technologies.</p>
                <p>Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                
                <div class="section">
                    <h2>Overall Technology Statistics</h2>
                    <table>
                        <tr>
                            <th>Category</th>
                            <th>Count</th>
                        </tr>
        """
        
        # Add technology counts
        tech_counts = analysis_results.get("technology_counts", {})
        if tech_counts:
            total = tech_counts.get("total_technologies", 0)
            html += f"""
                        <tr>
                            <td>Total Technologies</td>
                            <td>{total}</td>
                        </tr>
            """
            
            for api_type, count in tech_counts.get("counts_by_type", {}).items():
                html += f"""
                        <tr>
                            <td>{api_type.capitalize()}</td>
                            <td>{count}</td>
                        </tr>
                """
                
        html += """
                    </table>
                    <div class="chart-container">
                        <img src="technology_counts_by_type.png" alt="Technology Counts by Type" class="chart">
                    </div>
                </div>
        """
        
        # Add defense relevance section
        defense_data = analysis_results.get("defense_relevance", {})
        if defense_data:
            defense_count = defense_data.get("defense_related_count", 0)
            defense_percent = defense_data.get("defense_percentage", 0)
            
            html += f"""
                <div class="section">
                    <h2>Defense-Related Technologies</h2>
                    <table>
                        <tr>
                            <th>Metric</th>
                            <th>Value</th>
                        </tr>
                        <tr>
                            <td>Defense-Related Technologies</td>
                            <td>{defense_count}</td>
                        </tr>
                        <tr>
                            <td>Percentage of All Technologies</td>
                            <td>{defense_percent:.1f}%</td>
                        </tr>
                    </table>
                    
                    <h3>Defense Technologies by Type</h3>
                    <table>
                        <tr>
                            <th>Type</th>
                            <th>Count</th>
                        </tr>
            """
            
            for api_type, count in defense_data.get("defense_counts_by_type", {}).items():
                html += f"""
                        <tr>
                            <td>{api_type.capitalize()}</td>
                            <td>{count}</td>
                        </tr>
                """
                
            html += """
                    </table>
                    <div class="chart-container">
                        <img src="defense_technologies.png" alt="Defense Technologies by Type" class="chart">
                    </div>
                </div>
            """
        
        # Add NASA centers section
        centers_data = analysis_results.get("nasa_centers", {})
        if centers_data:
            html += """
                <div class="section">
                    <h2>NASA Centers</h2>
                    <h3>Top Contributing Centers</h3>
                    <table>
                        <tr>
                            <th>Center</th>
                            <th>Technologies</th>
                            <th>Percentage</th>
                        </tr>
            """
            
            centers = centers_data.get("center_counts", {})
            percentages = centers_data.get("center_percentages", {})
            
            # Get top 10 centers
            top_centers = sorted(centers.items(), key=lambda x: x[1], reverse=True)[:10]
            
            for center, count in top_centers:
                percent = percentages.get(center, 0)
                html += f"""
                        <tr>
                            <td>{center}</td>
                            <td>{count}</td>
                            <td>{percent:.1f}%</td>
                        </tr>
                """
                
            html += """
                    </table>
                    <div class="chart-container">
                        <img src="top_nasa_centers.png" alt="Top NASA Centers" class="chart">
                    </div>
                </div>
            """
        
        # Add categories section
        categories_data = analysis_results.get("categories", {})
        if categories_data:
            html += """
                <div class="section">
                    <h2>Technology Categories</h2>
                    <h3>Top Categories</h3>
                    <table>
                        <tr>
                            <th>Category</th>
                            <th>Technologies</th>
                            <th>Percentage</th>
                        </tr>
            """
            
            categories = categories_data.get("category_counts", {})
            percentages = categories_data.get("category_percentages", {})
            
            # Get top 15 categories
            top_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:15]
            
            for category, count in top_categories:
                percent = percentages.get(category, 0)
                html += f"""
                        <tr>
                            <td>{category}</td>
                            <td>{count}</td>
                            <td>{percent:.1f}%</td>
                        </tr>
                """
                
            html += """
                    </table>
                    <div class="chart-container">
                        <img src="category_distribution.png" alt="Category Distribution" class="chart">
                    </div>
                </div>
            """
        
        # Close HTML
        html += """
                <div class="footer">
                    <p>This report was generated from NASA Technology Transfer API data.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Write HTML to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
            
        logger.info(f"HTML report saved to {filepath}")
        
    except Exception as e:
        logger.error(f"Error generating HTML report: {e}")

def main():
    """
    Main function to parse arguments and run the analysis.
    """
    parser = argparse.ArgumentParser(description='Analyze NASA Technology Transfer API data')
    parser.add_argument('--individual', action='store_true', 
                        help='Analyze individual result files instead of combined files')
    parser.add_argument('--no-visualizations', action='store_true',
                        help='Skip generating visualizations')
    parser.add_argument('--no-html', action='store_true',
                        help='Skip generating HTML report')
    parser.add_argument('--output-file', type=str, default='nasa_tech_analysis.json',
                        help='Output JSON file name for analysis results')
    args = parser.parse_args()
    
    logger.info("NASA Technology Transfer API Data Analysis Started")
    
    # Load the data
    all_data = load_all_data(not args.individual)
    
    if not all_data:
        logger.error("No data found to analyze. Run nasa_api_collector.py first.")
        return
    
    # Perform analysis
    analysis_results = {
        "technology_counts": analyze_technology_counts(all_data),
        "nasa_centers": analyze_nasa_centers(all_data),
        "categories": analyze_categories(all_data),
        "defense_relevance": analyze_defense_relevance(all_data),
        "date_analyzed": datetime.now().isoformat()
    }
    
    # Save analysis results
    save_analysis_results(analysis_results, args.output_file)
    
    # Generate visualizations
    if not args.no_visualizations:
        generate_visualizations(analysis_results)
    
    # Generate HTML report
    if not args.no_html:
        generate_html_report(analysis_results)
    
    logger.info("Analysis completed successfully")

if __name__ == "__main__":
    main()