#!/usr/bin/env python3
"""
Performance benchmark for the gene mutual information library.
"""

import time
import numpy as np
import gene_mutual_info
import anndata

def benchmark_mutual_info(n_genes, n_samples):
    """Benchmark mutual information computation."""
    print(f"Benchmarking with {n_genes} genes and {n_samples} samples...")
    
    # Create random gene expression data
    np.random.seed(42)
    matrix = np.random.randn(n_genes, n_samples)
    genes = [f"GENE_{i:04d}" for i in range(n_genes)]
    
    # Time the computation
    start_time = time.time()
    result = gene_mutual_info.compute_mutual_information(matrix, genes)
    end_time = time.time()
    
    elapsed = end_time - start_time
    n_pairs = (n_genes * (n_genes + 1)) // 2  # Including diagonal
    
    print(f"  Computed {n_pairs} mutual information pairs in {elapsed:.3f} seconds")
    print(f"  Rate: {n_pairs / elapsed:.1f} pairs/second")
    print(f"  Memory footprint: ~{matrix.nbytes / 1024 / 1024:.1f} MB for input matrix")
    print()
    
    return elapsed, n_pairs

def benchmark_anndata_mutual_info(h5ad_path, max_genes=None):
    """Benchmark mutual information computation on real gene expression data from h5ad file."""
    print(f"Loading AnnData from: {h5ad_path}")
    
    # Load the AnnData object
    start_load = time.time()
    adata = anndata.read_h5ad(h5ad_path)
    end_load = time.time()
    
    print(f"  Loaded in {end_load - start_load:.3f} seconds")
    print(f"  Original shape: {adata.shape}")
    
    # Extract gene expression matrix and gene names
    # AnnData stores data as (n_obs, n_vars) where obs are samples and vars are genes
    # We need to transpose to get (n_genes, n_samples) format
    if hasattr(adata.X, 'toarray'):
        # Handle sparse matrix
        matrix = adata.X.T.toarray()
    else:
        # Handle dense matrix
        matrix = adata.X.T
    
    # Ensure the matrix is a proper numpy array with correct dtype and memory layout
    matrix = np.ascontiguousarray(matrix, dtype=np.float64)
    genes = list(adata.var_names)
    
    # Optionally limit number of genes for faster testing
    if max_genes and len(genes) > max_genes:
        print(f"  Limiting to first {max_genes} genes for faster testing")
        matrix = matrix[:max_genes]
        genes = genes[:max_genes]
    
    print(f"  Final shape: {matrix.shape} (genes × samples)")
    print(f"  Gene names: {genes[:5]}..." if len(genes) > 5 else f"  Gene names: {genes}")
    
    # Time the mutual information computation
    start_time = time.time()
    result = gene_mutual_info.compute_mutual_information(matrix, genes)
    end_time = time.time()
    
    elapsed = end_time - start_time
    n_pairs = (len(genes) * (len(genes) + 1)) // 2  # Including diagonal
    
    print(f"  Computed {n_pairs} mutual information pairs in {elapsed:.3f} seconds")
    print(f"  Rate: {n_pairs / elapsed:.1f} pairs/second")
    print(f"  Memory footprint: ~{matrix.nbytes / 1024 / 1024:.1f} MB for input matrix")
    print()
    
    return elapsed, n_pairs, result

def main():
    """Run benchmarks with different matrix sizes."""
    print("Gene Mutual Information Performance Benchmark")
    print("=" * 50)
    print()
    
    # Test different sizes
    test_cases = [
        (10, 100),    # Small: 10 genes, 100 samples
        (50, 200),    # Medium: 50 genes, 200 samples  
        (100, 500),   # Large: 100 genes, 500 samples
    ]
    
    total_time = 0
    total_pairs = 0
    
    for n_genes, n_samples in test_cases:
        elapsed, n_pairs = benchmark_mutual_info(n_genes, n_samples)
        total_time += elapsed
        total_pairs += n_pairs
    
    print(f"Overall performance: {total_pairs / total_time:.1f} pairs/second")
    print()
    print("Note: Performance scales quadratically with number of genes")
    print("      and linearly with number of samples.")
    print()
    
    # Example of using AnnData h5ad file (uncomment and provide path)
    print("=" * 50)
    print("AnnData h5ad file benchmark example:")
    print("(Uncomment the following lines and provide a valid h5ad file path)")
    
    # Example usage:
    elapsed, n_pairs, mi_dict = benchmark_anndata_mutual_info("/Users/ceglian/Data/tcri/smith_chkpt.h5ad", max_genes=100000)
    
    # Extract all pairwise MI values (excluding self-comparisons)
    all_pairs = []
    for gene1 in mi_dict:
        for gene2 in mi_dict[gene1]:
            if gene1 != gene2:  # Skip diagonal (self-MI)
                all_pairs.append(((gene1, gene2), mi_dict[gene1][gene2]))
    
    # Sort by MI value and show top 5
    sorted_pairs = sorted(all_pairs, key=lambda x: x[1], reverse=True)[:5]
    print(f"Top 5 mutual information pairs (excluding self-comparisons):")
    for (gene1, gene2), mi_value in sorted_pairs:
        print(f"  {gene1} - {gene2}: {mi_value:.4f}")

if __name__ == "__main__":
    main()
