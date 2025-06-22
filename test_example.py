#!/usr/bin/env python3
"""
Example usage of the GVMI (GeneVector Mutual Information) library.

This script demonstrates how to use the Rust-based mutual information
computation with numpy arrays and gene labels through the Python API.
"""

import numpy as np
import gvmi

def create_sample_data():
    """Create sample gene expression data for testing."""
    # Create a 5x100 matrix (5 genes, 100 samples)
    np.random.seed(42)  # For reproducible results
    
    # Gene names
    genes = ['GENE_A', 'GENE_B', 'GENE_C', 'GENE_D', 'GENE_E']
    
    # Create some synthetic gene expression data with known relationships
    n_samples = 100
    
    # GENE_A: random normal distribution
    gene_a = np.random.normal(5.0, 1.0, n_samples)
    
    # GENE_B: correlated with GENE_A (high mutual information expected)
    gene_b = gene_a + np.random.normal(0, 0.5, n_samples)
    
    # GENE_C: independent random data (low mutual information with others)
    gene_c = np.random.normal(3.0, 1.5, n_samples)
    
    # GENE_D: non-linear relationship with GENE_A
    gene_d = np.sin(gene_a) + np.random.normal(0, 0.3, n_samples)
    
    # GENE_E: partially correlated with GENE_C
    gene_e = 0.7 * gene_c + np.random.normal(0, 1.0, n_samples)
    
    # Stack into matrix (genes as rows, samples as columns)
    matrix = np.stack([gene_a, gene_b, gene_c, gene_d, gene_e])
    
    return matrix, genes

def main():
    """Main function to test the mutual information computation."""
    print("Creating sample gene expression data...")
    matrix, genes = create_sample_data()
    
    print(f"Matrix shape: {matrix.shape}")
    print(f"Genes: {genes}")
    print()
    
    print("Computing mutual information between all gene pairs...")
    try:
        mi_results = gvmi.compute_mutual_information(matrix, genes)
        
        print("\\nMutual Information Results:")
        print("=" * 50)
        
        for gene1 in genes:
            for gene2 in genes:
                mi_value = mi_results[gene1][gene2]
                print(f"{gene1} vs {gene2}: {mi_value:.6f}")
        
        print("\\nSymmetric matrix verification:")
        print("=" * 30)
        for i, gene1 in enumerate(genes):
            for j, gene2 in enumerate(genes[i+1:], i+1):
                mi_12 = mi_results[gene1][gene2]
                mi_21 = mi_results[gene2][gene1]
                print(f"{gene1} vs {gene2}: {mi_12:.6f} == {mi_21:.6f} -> {abs(mi_12 - mi_21) < 1e-10}")
        
        print("\\nHighest mutual information pairs:")
        print("=" * 35)
        
        # Find highest MI pairs (excluding self-comparisons)
        mi_pairs = []
        for gene1 in genes:
            for gene2 in genes:
                if gene1 != gene2:
                    mi_pairs.append((gene1, gene2, mi_results[gene1][gene2]))
        
        # Sort by MI value and show top 5
        mi_pairs.sort(key=lambda x: x[2], reverse=True)
        for gene1, gene2, mi_val in mi_pairs[:5]:
            print(f"{gene1} - {gene2}: {mi_val:.6f}")
            
    except Exception as e:
        print(f"Error computing mutual information: {e}")
        return 1
    
    print("\\nTest completed successfully!")
    return 0

if __name__ == "__main__":
    exit(main())
