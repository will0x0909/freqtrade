#!/usr/bin/env python3
"""
Token Categorization Script

This script categorizes tokens based on correlation analysis features that
correlate with profitability in trading strategies.

Categories:
- High Potential: High positive correlation features
- Medium Potential: Moderate correlation features  
- Low Potential: Low correlation features
- High Risk: High negative correlation features
"""

import json
import pandas as pd
from typing import Dict, List, Any
import numpy as np


class TokenCategorizer:
    def __init__(self, correlation_data_path: str = None):
        """Initialize categorizer with correlation thresholds"""
        self.correlation_data = None
        if correlation_data_path:
            self.load_correlation_data(correlation_data_path)
        
        # Define scoring weights based on latest correlation analysis with profitability
        # These will be updated automatically from correlation data if available
        self.feature_weights = {
            'score': 0.073,
            'liquidity': 0.065, 
            'holders': 0.055,
            'volume_24h': 0.054,
            'market_cap': -0.044,  # negative correlation
            'fdv': -0.080  # negative correlation
        }
        
        # Field name mappings for different data sources
        self.field_mappings = {
            'volume_24h': ['volume24h', 'volume_24h'],
            'market_cap': ['marketCap', 'market_cap'],
            'fdv': ['fdv'],
            'liquidity': ['liquidity'],
            'holders': ['holders'],
            'score': ['score'],
            'symbol': ['symbol'],
            'name': ['name'],
            'price': ['price']
        }
        
        # Category thresholds (adjusted based on actual data distribution)
        self.thresholds = {
            'high_potential': 0.2,    # Top 10-15%
            'medium_potential': 0.0,  # Above average 
            'low_potential': -0.2,    # Below average but not terrible
            'high_risk': -0.4         # Bottom performers
        }
    
    def load_correlation_data(self, file_path: str):
        """Load correlation analysis data and update feature weights"""
        with open(file_path, 'r') as f:
            self.correlation_data = json.load(f)
        
        # Update feature weights from correlation analysis if available
        if 'correlations' in self.correlation_data:
            correlations = self.correlation_data['correlations']
            print("Updating feature weights from correlation analysis:")
            
            # Update weights with latest correlation values
            updated_weights = {}
            for feature in self.feature_weights.keys():
                if feature in correlations:
                    new_weight = correlations[feature]
                    old_weight = self.feature_weights[feature]
                    updated_weights[feature] = new_weight
                    print(f"  {feature}: {old_weight:.3f} -> {new_weight:.3f}")
                else:
                    updated_weights[feature] = self.feature_weights[feature]
            
            self.feature_weights = updated_weights
            print("Feature weights updated successfully\n")
    
    def load_token_data(self, file_path: str):
        """Load token data from JSON file"""
        with open(file_path, 'r') as f:
            data = json.load(f)
            # Handle different data structures
            if isinstance(data, dict):
                if 'data' in data:
                    return data['data']  # Binance API format
                elif 'tokens' in data:
                    return data['tokens']
                else:
                    return list(data.values())[0] if data else []
            elif isinstance(data, list):
                return data
            else:
                return []
    
    def get_field_value(self, token: Dict, field: str) -> float:
        """Get field value using field mappings to handle different data sources"""
        if field in self.field_mappings:
            for mapped_field in self.field_mappings[field]:
                if mapped_field in token and token[mapped_field] is not None:
                    value = token[mapped_field]
                    # Convert string numbers to float
                    if isinstance(value, str):
                        try:
                            return float(value)
                        except ValueError:
                            continue
                    elif isinstance(value, (int, float)):
                        return float(value)
            return 0.0
        return token.get(field, 0.0)
    
    def normalize_value(self, value: float, feature: str, tokens_data: List[Dict]) -> float:
        """Normalize feature values to 0-1 range based on dataset"""
        if not tokens_data:
            return 0.5
        
        values = []
        for token in tokens_data:
            val = self.get_field_value(token, feature)
            if val is not None and val > 0:
                values.append(val)
                
        if not values:
            return 0.5
            
        min_val = min(values)
        max_val = max(values)
        
        if max_val == min_val:
            return 0.5
            
        normalized = (value - min_val) / (max_val - min_val)
        return max(0, min(1, normalized))
    
    def calculate_composite_score(self, token: Dict, tokens_data: List[Dict]) -> float:
        """Calculate composite score based on weighted normalized features"""
        score = 0.0
        
        for feature, weight in self.feature_weights.items():
            value = self.get_field_value(token, feature)
            if value is not None and value > 0:
                normalized_value = self.normalize_value(value, feature, tokens_data)
                
                # For negative correlation features, invert the normalized value
                if weight < 0:
                    normalized_value = 1 - normalized_value
                    weight = abs(weight)
                
                score += normalized_value * weight
        
        # Normalize final score to -1 to 1 range
        max_possible_score = sum(abs(w) for w in self.feature_weights.values())
        return (score / max_possible_score) * 2 - 1
    
    def get_category(self, composite_score: float) -> str:
        """Determine category based on composite score"""
        if composite_score >= self.thresholds['high_potential']:
            return 'High Potential'
        elif composite_score >= self.thresholds['medium_potential']:
            return 'Medium Potential'
        elif composite_score >= self.thresholds['low_potential']:
            return 'Low Potential'
        else:
            return 'High Risk'
    
    def get_category_description(self, category: str) -> str:
        """Get description for each category"""
        descriptions = {
            'High Potential': 'Strong positive correlation features, likely profitable',
            'Medium Potential': 'Moderate correlation features, potential for profit',
            'Low Potential': 'Weak correlation features, uncertain profitability',
            'High Risk': 'Strong negative correlation features, likely unprofitable'
        }
        return descriptions.get(category, 'Unknown category')
    
    def categorize_tokens(self, tokens_data: List[Dict]) -> Dict[str, List[Dict]]:
        """Categorize all tokens and return grouped results"""
        categorized = {
            'High Potential': [],
            'Medium Potential': [],
            'Low Potential': [],
            'High Risk': []
        }
        
        for token in tokens_data:
            composite_score = self.calculate_composite_score(token, tokens_data)
            category = self.get_category(composite_score)
            
            token_with_score = token.copy()
            token_with_score['composite_score'] = composite_score
            token_with_score['category'] = category
            token_with_score['category_description'] = self.get_category_description(category)
            
            categorized[category].append(token_with_score)
        
        # Sort each category by composite score (descending)
        for category in categorized:
            categorized[category].sort(key=lambda x: x['composite_score'], reverse=True)
        
        return categorized
    
    def generate_report(self, categorized_tokens: Dict[str, List[Dict]]) -> str:
        """Generate a summary report of categorization results"""
        report = "TOKEN CATEGORIZATION REPORT\n"
        report += "=" * 50 + "\n\n"
        
        total_tokens = sum(len(tokens) for tokens in categorized_tokens.values())
        report += f"Total tokens analyzed: {total_tokens}\n\n"
        
        for category, tokens in categorized_tokens.items():
            count = len(tokens)
            percentage = (count / total_tokens * 100) if total_tokens > 0 else 0
            
            report += f"{category}: {count} tokens ({percentage:.1f}%)\n"
            report += f"Description: {self.get_category_description(category)}\n"
            
            # Add median statistics for the category
            if tokens:
                profit_values = [t.get('profit_pct', 0) for t in tokens if t.get('profit_pct') is not None]
                mcap_values = [self.get_field_value(t, 'market_cap') for t in tokens]
                liquidity_values = [self.get_field_value(t, 'liquidity') for t in tokens]
                
                if profit_values:
                    median_profit = np.median(profit_values)
                    report += f"Median Profit: {median_profit:.2f}%\n"
                if mcap_values:
                    median_mcap = np.median([v for v in mcap_values if v > 0])
                    if median_mcap > 0:
                        report += f"Median Market Cap: ${median_mcap:,.0f}\n"
                if liquidity_values:
                    median_liquidity = np.median([v for v in liquidity_values if v > 0])
                    if median_liquidity > 0:
                        report += f"Median Liquidity: ${median_liquidity:,.0f}\n"
            
            if tokens:
                # Determine how many tokens to show based on category
                if category == 'High Risk':
                    show_count = min(5, len(tokens))  # Top 5 for High Risk
                    report += f"Top {show_count} tokens in this category:\n"
                elif len(tokens) <= 10:
                    show_count = len(tokens)  # Show all if <= 10
                    report += f"All {show_count} tokens in this category:\n"
                else:
                    show_count = min(10, len(tokens))  # Show top 10 if more than 10
                    report += f"Top {show_count} tokens in this category:\n"
                
                for i, token in enumerate(tokens[:show_count], 1):
                    symbol = self.get_field_value(token, 'symbol') or token.get('symbol', 'Unknown')
                    score = token.get('composite_score', 0)
                    profit = token.get('profit_pct', 'N/A')
                    price = self.get_field_value(token, 'price')
                    market_cap = self.get_field_value(token, 'market_cap')
                    
                    if isinstance(symbol, float):
                        symbol = 'Unknown'
                    
                    price_str = f", Price: ${price:.6f}" if price > 0 else ""
                    mcap_str = f", MCap: ${market_cap:,.0f}" if market_cap > 0 else ""
                    profit_str = f", Profit: {profit}%" if profit != 'N/A' else ""
                    
                    report += f"  {i}. {symbol} (Score: {score:.3f}{price_str}{mcap_str}{profit_str})\n"
            
            report += "\n"
        
        return report
    
    def save_results(self, categorized_tokens: Dict[str, List[Dict]], output_path: str):
        """Save categorization results to JSON file"""
        results = {
            'categorization_metadata': {
                'feature_weights': self.feature_weights,
                'thresholds': self.thresholds,
                'total_tokens': sum(len(tokens) for tokens in categorized_tokens.values())
            },
            'categories': categorized_tokens,
            'summary': {
                category: {
                    'count': len(tokens),
                    'percentage': len(tokens) / sum(len(t) for t in categorized_tokens.values()) * 100,
                    'median_composite_score': np.median([t['composite_score'] for t in tokens]) if tokens else 0,
                    'avg_composite_score': np.mean([t['composite_score'] for t in tokens]) if tokens else 0,
                    'median_profit_pct': np.median([t.get('profit_pct', 0) for t in tokens]) if tokens else 0,
                    'avg_profit_pct': np.mean([t.get('profit_pct', 0) for t in tokens]) if tokens else 0,
                    'median_market_cap': np.median([self.get_field_value(t, 'market_cap') for t in tokens]) if tokens else 0,
                    'median_liquidity': np.median([self.get_field_value(t, 'liquidity') for t in tokens]) if tokens else 0,
                    'median_holders': np.median([self.get_field_value(t, 'holders') for t in tokens]) if tokens else 0
                }
                for category, tokens in categorized_tokens.items()
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)


def main():
    """Main function to run token categorization"""
    # Initialize categorizer
    categorizer = TokenCategorizer()
    
    # Load correlation analysis data
    try:
        categorizer.load_correlation_data('token_correlation_analysis.json')
        print("Loaded correlation analysis data")
    except FileNotFoundError:
        print("Warning: token_correlation_analysis.json not found")
        return
    
    # Load token data from the main dataset
    tokens_data = []
    
    # First try to load the complete token dataset
    try:
        main_tokens = categorizer.load_token_data('token_data.json')
        if main_tokens:
            tokens_data.extend(main_tokens)
            print(f"Loaded main token dataset: {len(main_tokens)} tokens")
    except FileNotFoundError:
        print("Warning: token_data.json not found")
    
    # Add top performers from correlation analysis if available
    if 'top_performers' in categorizer.correlation_data:
        correlation_tokens = categorizer.correlation_data['top_performers']
        # Only add if not already in main dataset (avoid duplicates)
        existing_symbols = {token.get('symbol') for token in tokens_data if token.get('symbol')}
        new_tokens = [token for token in correlation_tokens 
                     if token.get('symbol') not in existing_symbols]
        if new_tokens:
            tokens_data.extend(new_tokens)
            print(f"Added {len(new_tokens)} additional tokens from correlation analysis")
    
    if not tokens_data:
        print("No token data found to categorize")
        return
    
    print(f"Categorizing {len(tokens_data)} tokens...")
    
    # Categorize tokens
    categorized_tokens = categorizer.categorize_tokens(tokens_data)
    
    # Generate and print report
    report = categorizer.generate_report(categorized_tokens)
    print(report)
    
    # Save results
    output_file = 'token_categorization_results.json'
    categorizer.save_results(categorized_tokens, output_file)
    print(f"Results saved to {output_file}")
    
    # Save report
    report_file = 'token_categorization_report.txt'
    with open(report_file, 'w') as f:
        f.write(report)
    print(f"Report saved to {report_file}")


if __name__ == "__main__":
    main()