#!/usr/bin/env python3
"""
Utility script to inspect pickle files created by mi_cli.py
"""

import argparse
import pickle
import sys
from pathlib import Path


def inspect_pickle(pickle_path, show_top=10, show_genes=False, detailed=False):
    """
    Inspect the contents of a mutual information pickle file.
    
    Args:
        pickle_path: Path to the pickle file
        show_top: Number of top MI pairs to show
        show_genes: Whether to show the gene list
        detailed: Whether to show detailed metadata
    """
    try:
        with open(pickle_path, 'rb') as f:
            data = pickle.load(f)
    except Exception as e:
        print(f"Error loading pickle file: {e}")
        sys.exit(1)
    
    print("=" * 60)
    print(f"Pickle File Inspection: {pickle_path}")
    print("=" * 60)
    
    # Basic information
    print(f"Number of genes: {data['n_genes']}")
    print(f"Number of gene pairs: {data['n_pairs']}")
    print(f"Computation time: {data['computation_time']:.2f} seconds")
    print(f"Created: {data['timestamp']}")
    print()
    
    # File size
    file_size = Path(pickle_path).stat().st_size / 1024 / 1024
    print(f"File size: {file_size:.2f} MB")
    print()
    
    # Extract MI dictionary
    mi_dict = data['mutual_information']
    genes = data['genes']
    
    # Show gene list if requested
    if show_genes:
        print("Genes:")
        for i, gene in enumerate(genes):
            print(f"  {i+1:3d}. {gene}")
        print()
    
    # Extract all pairwise MI values (excluding self-comparisons)
    all_pairs = []
    diagonal_values = []
    
    for gene1 in mi_dict:
        for gene2 in mi_dict[gene1]:
            if gene1 == gene2:
                diagonal_values.append(mi_dict[gene1][gene2])
            else:
                # Only add each pair once (avoid duplicates)
                if gene1 < gene2:  # Lexicographic ordering to avoid duplicates
                    all_pairs.append(((gene1, gene2), mi_dict[gene1][gene2]))
    
    print(f"Self-mutual information (diagonal) statistics:")
    if diagonal_values:
        print(f"  Mean: {sum(diagonal_values) / len(diagonal_values):.4f}")
        print(f"  Min:  {min(diagonal_values):.4f}")
        print(f"  Max:  {max(diagonal_values):.4f}")
    print()
    
    print(f"Cross-gene mutual information statistics:")
    if all_pairs:
        mi_values = [mi for _, mi in all_pairs]
        print(f"  Mean: {sum(mi_values) / len(mi_values):.4f}")
        print(f"  Min:  {min(mi_values):.4f}")
        print(f"  Max:  {max(mi_values):.4f}")
    print()
    
    # Show top pairs
    if all_pairs and show_top > 0:
        sorted_pairs = sorted(all_pairs, key=lambda x: x[1], reverse=True)
        print(f"Top {min(show_top, len(sorted_pairs))} mutual information pairs:")
        for i, ((gene1, gene2), mi_value) in enumerate(sorted_pairs[:show_top], 1):
            print(f"  {i:2d}. {gene1} - {gene2}: {mi_value:.6f}")
        print()
    
    # Show detailed metadata if requested
    if detailed and 'metadata' in data:
        metadata = data['metadata']
        print("Detailed metadata:")
        for key, value in metadata.items():
            print(f"  {key}: {value}")
        print()
    
    print("Data structure:")
    print("  data['mutual_information'] -> nested dict {gene1: {gene2: mi_value}}")
    print("  data['genes'] -> list of gene names")
    print("  data['computation_time'] -> float (seconds)")
    print("  data['n_genes'] -> int")
    print("  data['n_pairs'] -> int")
    print("  data['timestamp'] -> str")
    print("  data['metadata'] -> dict with preprocessing info")
    

def main():
    """Main function for pickle inspection."""
    parser = argparse.ArgumentParser(
        description="Inspect mutual information pickle files created by gvmi",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic inspection
  python inspect_pickle.py results.pkl
  
  # Show top 20 pairs and gene list
  python inspect_pickle.py results.pkl --top 20 --show-genes
  
  # Detailed inspection with metadata
  python inspect_pickle.py results.pkl --detailed
        """
    )
    
    parser.add_argument(
        'pickle_file',
        help='Path to pickle file to inspect'
    )
    
    parser.add_argument(
        '--top',
        type=int,
        default=10,
        help='Number of top MI pairs to show (default: 10, 0 to skip)'
    )
    
    parser.add_argument(
        '--show-genes',
        action='store_true',
        help='Show the list of genes'
    )
    
    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Show detailed metadata'
    )
    
    args = parser.parse_args()
    
    # Validate input file
    pickle_path = Path(args.pickle_file)
    if not pickle_path.exists():
        print(f"Error: Pickle file does not exist: {pickle_path}")
        sys.exit(1)
    
    inspect_pickle(
        pickle_path,
        show_top=args.top,
        show_genes=args.show_genes,
        detailed=args.detailed
    )


if __name__ == '__main__':
    main()
