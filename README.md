# GeneVector Mutual Information (gvmi)

High-performance Rust library with Python bindings and CLI for computing mutual information between gene expression profiles.

## Overview

**gvmi** (GeneVector Mutual Information) provides an efficient implementation for calculating mutual information between pairs of genes in gene expression matrices. It uses Rust for computational performance with parallel processing, while providing a convenient Python interface through PyO3 and a powerful command-line tool for bioinformatics workflows.

## Features

- **Fast computation**: Parallel processing using Rayon for efficient mutual information calculation
- **NumPy integration**: Direct support for NumPy arrays as input
- **Flexible output**: Returns a nested dictionary structure for easy access to pairwise MI values
- **Robust discretization**: Uses quantile-based binning for converting continuous gene expression to discrete values
- **Error handling**: Comprehensive error checking for input validation

## Installation

### Prerequisites

- Rust (with Cargo)
- Python 3.10+ (recommended)
- Maturin for building Python extensions

### Building from source

```bash
# Clone the repository
git clone <repository_url>
cd gvmi

# Install maturin if you haven't already
pip install maturin

# Build and install the package
maturin develop --release
```

## Usage

### Basic Example

```python
import numpy as np
import gvmi

# Create sample data: 5 genes x 100 samples
matrix = np.random.randn(5, 100)
genes = ['GENE_A', 'GENE_B', 'GENE_C', 'GENE_D', 'GENE_E']

# Compute mutual information
mi_results = gvmi.compute_mutual_information(matrix, genes)

# Access results
print(f"MI between GENE_A and GENE_B: {mi_results['GENE_A']['GENE_B']}")

# Iterate through all pairs
for gene1 in genes:
    for gene2 in genes:
        mi_value = mi_results[gene1][gene2]
        print(f"{gene1} vs {gene2}: {mi_value:.6f}")
```

### Input Requirements

- **Matrix**: A 2D NumPy array where:
  - Rows represent genes
  - Columns represent samples/conditions
  - Values should be gene expression levels (continuous values)
  
- **Genes**: A list of gene names/identifiers
  - Length must match the number of rows in the matrix
  - Can be strings or any Python objects that convert to strings

### Output Format

The function returns a nested dictionary structure:

```python
{
    'GENE_A': {
        'GENE_A': 1.234,  # Self-mutual information
        'GENE_B': 0.567,
        'GENE_C': 0.123,
        ...
    },
    'GENE_B': {
        'GENE_A': 0.567,  # Symmetric values
        'GENE_B': 1.456,
        ...
    },
    ...
}
```

## Algorithm Details

### Mutual Information Calculation

The library implements the standard mutual information formula:

```
MI(X,Y) = ∑∑ P(x,y) * log(P(x,y) / (P(x) * P(y)))
```

Where:
- `P(x,y)` is the joint probability of observing values x and y
- `P(x)` and `P(y)` are the marginal probabilities

### Discretization

Since mutual information is defined for discrete variables, continuous gene expression values are discretized using:

1. **Quantile-based binning**: Values are sorted and divided into 10 equal-frequency bins
2. **Adaptive binning**: Each gene pair uses its own binning strategy based on the data distribution

This approach is more robust than fixed-width binning for gene expression data, which often has non-uniform distributions.

### Performance Optimizations

- **Parallel processing**: All gene pairs are computed in parallel using Rayon
- **Memory efficiency**: Streaming computation without storing full pairwise matrices
- **Fast discretization**: Optimized quantile calculation and binning

## Command-Line Interface (gvmi)

The project includes `gvmi` (Gene Vector Mutual Information) - a convenient CLI for processing h5ad files.

### Installation

To install `gvmi` to your PATH:

```bash
# Run the installation script (recommended)
./install.sh
```

This will:
1. Create a symlink to `gvmi` in `~/.local/bin/`
2. Add `~/.local/bin` to your PATH in your shell profile
3. Make `gvmi` available from anywhere

#### Manual Installation

Alternatively, you can manually add the project directory to your PATH:

```bash
# Add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
export PATH="/path/to/gvmi:$PATH"

# Or create a symlink
ln -s /path/to/gvmi/gvmi ~/.local/bin/gvmi
```

#### Verify Installation

```bash
# Check if gvmi is available
which gvmi
gvmi --help
```

### Basic Usage

```bash
# Compute MI for all genes in an h5ad file
gvmi input.h5ad -o results.pkl

# Or use the shell wrapper (if not in PATH)
./compute_mi.sh input.h5ad -o results.pkl
```

### CLI Options

```bash
gvmi --help
```

- `--max-genes N`: Limit to first N genes (for testing)
- `--min-cells N`: Filter genes expressed in fewer than N cells (default: 10)
- `--min-genes-per-cell N`: Filter cells with fewer than N genes (default: 100)
- `--no-filter`: Skip all filtering
- `--force`: Overwrite output file if it exists

### Examples

```bash
# Quick test with 100 genes
gvmi data.h5ad -o test.pkl --max-genes 100

# Custom filtering
gvmi data.h5ad -o results.pkl --min-cells 5 --min-genes-per-cell 200

# No filtering (use all genes/cells)
gvmi data.h5ad -o raw_results.pkl --no-filter
```

### Inspecting Results

Use the inspection script to examine pickle files:

```bash
# Basic inspection
python inspect_pickle.py results.pkl

# Detailed view with top 20 pairs
python inspect_pickle.py results.pkl --top 20 --detailed

# Show gene list
python inspect_pickle.py results.pkl --show-genes
```

### Loading Results in Python

```python
import pickle

# Load the results
with open('results.pkl', 'rb') as f:
    data = pickle.load(f)

# Access the MI dictionary
mi_dict = data['mutual_information']
print(f"MI between GENE1 and GENE2: {mi_dict['GENE1']['GENE2']}")

# Get metadata
metadata = data['metadata']
print(f"Source file: {metadata['source_file']}")
print(f"Computation time: {data['computation_time']:.2f} seconds")
```

## Updating GVMI

For updating the gvmi program after making changes:

### Quick Update
```bash
# Automated update script
./update_gvmi.sh
```

### Manual Update
```bash
cd /Users/ceglian/Codebase/GitHub/gvmi
cargo clean  # optional
/Users/ceglian/miniforge3/envs/ml/bin/python -m maturin develop --release
gvmi --help  # verify
```

See [BUILD_AND_INSTALL.md](BUILD_AND_INSTALL.md) for detailed instructions and [QUICK_UPDATE.md](QUICK_UPDATE.md) for a quick reference.

## Testing

Run the example test script:

```bash
python test_example.py
```

This will create synthetic gene expression data with known relationships and demonstrate the mutual information computation.

## Dependencies

### Rust Dependencies
- `pyo3`: Python bindings
- `numpy`: NumPy array support
- `ndarray`: N-dimensional array processing
- `rayon`: Parallel iterators
- `thiserror`: Error handling

### Python Dependencies
- `numpy`: Array operations
- `maturin`: Building (development only)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Add your license information here]

## Performance Notes

- The algorithm complexity is O(n²) for n genes, as it computes all pairwise mutual information values
- Memory usage scales with the number of samples and genes
- For large datasets (>1000 genes), consider chunking or filtering genes of interest
- Parallel processing provides significant speedup on multi-core systems

## Future Improvements

- [ ] Support for different discretization methods
- [ ] Sparse matrix support for large datasets
- [ ] Additional statistical measures (correlation, distance metrics)
- [ ] GPU acceleration for very large matrices
- [ ] Incremental computation for streaming data
