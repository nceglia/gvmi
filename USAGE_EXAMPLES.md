# Usage Examples

This document provides practical examples of using the gene mutual information CLI tools.

## Quick Start

### 1. Test with small dataset
```bash
# Process first 50 genes from an h5ad file
python mi_cli.py /Users/ceglian/Data/h5ads/mye_with_palantir.h5ad -o test_small.pkl --max-genes 50

# Inspect the results
python inspect_pickle.py test_small.pkl --detailed
```

### 2. Process larger dataset
```bash
# Process first 200 genes with custom filtering
python mi_cli.py /Users/ceglian/Data/h5ads/mye_with_palantir.h5ad -o mye_200genes.pkl \
    --max-genes 200 \
    --min-cells 5 \
    --min-genes-per-cell 200

# Check computation time and top pairs
python inspect_pickle.py mye_200genes.pkl --top 20
```

### 3. Full dataset processing
```bash
# Process all genes (warning: this can take a long time for large datasets!)
python mi_cli.py /Users/ceglian/Data/h5ads/mye_with_palantir.h5ad -o mye_full.pkl

# Or with no filtering
python mi_cli.py /Users/ceglian/Data/h5ads/mye_with_palantir.h5ad -o mye_raw.pkl --no-filter
```

## Available H5AD Files

Based on your data directory, here are some suggested commands for different datasets:

### Myeloid datasets
```bash
# Myeloid with Palantir trajectories
python mi_cli.py /Users/ceglian/Data/h5ads/mye_with_palantir.h5ad -o mye_palantir_mi.pkl --max-genes 100

# Macrophage dataset
python mi_cli.py /Users/ceglian/Data/h5ads/macrophage_v3.h5ad -o macrophage_mi.pkl --max-genes 100

# Annotated myeloid
python mi_cli.py /Users/ceglian/Data/h5ads/annotated_myeloid_v100.h5ad -o annotated_mye_mi.pkl --max-genes 100
```

### T-cell datasets
```bash
# T-cell harmony
python mi_cli.py /Users/ceglian/Data/utility/data/tcell_harmony.h5ad -o tcell_harmony_mi.pkl --max-genes 100

# Raw T-cell entropy
python mi_cli.py /Users/ceglian/Data/utility/data/raw_tcell_entropy.h5ad -o tcell_entropy_mi.pkl --max-genes 100
```

### TCR datasets
```bash
# PBMC with TCR
python mi_cli.py /Users/ceglian/Data/tcri/pbmc_conga.h5ad -o pbmc_tcr_mi.pkl --max-genes 100

# Smith checkpoint dataset
python mi_cli.py /Users/ceglian/Data/tcri/smith_chkpt.h5ad -o smith_chkpt_mi.pkl --max-genes 100
```

## Working with Results

### Loading and analyzing results in Python
```python
import pickle
import numpy as np
import pandas as pd

# Load results
with open('test_small.pkl', 'rb') as f:
    data = pickle.load(f)

mi_dict = data['mutual_information']
genes = data['genes']

# Convert to pandas DataFrame for easier analysis
mi_matrix = pd.DataFrame(index=genes, columns=genes)
for gene1 in genes:
    for gene2 in genes:
        mi_matrix.loc[gene1, gene2] = mi_dict[gene1][gene2]

# Convert to numeric
mi_matrix = mi_matrix.astype(float)

# Find most correlated gene pairs
upper_triangle = np.triu(mi_matrix.values, k=1)  # Exclude diagonal
max_idx = np.unravel_index(np.argmax(upper_triangle), upper_triangle.shape)
max_genes = (mi_matrix.index[max_idx[0]], mi_matrix.columns[max_idx[1]])
max_mi = upper_triangle[max_idx]

print(f"Highest MI pair: {max_genes[0]} - {max_genes[1]} = {max_mi:.4f}")

# Create correlation network
import matplotlib.pyplot as plt
import seaborn as sns

# Plot heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(mi_matrix, annot=False, cmap='viridis', cbar=True)
plt.title('Gene Mutual Information Matrix')
plt.tight_layout()
plt.savefig('mi_heatmap.png', dpi=150)
plt.show()
```

### Filtering high MI pairs
```python
# Extract high MI pairs (excluding diagonal)
high_mi_pairs = []
threshold = 0.1  # Adjust based on your data

for gene1 in genes:
    for gene2 in genes:
        if gene1 != gene2:  # Exclude self-comparisons
            mi_value = mi_dict[gene1][gene2]
            if mi_value > threshold:
                # Only add each pair once
                if gene1 < gene2:  # Lexicographic ordering
                    high_mi_pairs.append((gene1, gene2, mi_value))

# Sort by MI value
high_mi_pairs.sort(key=lambda x: x[2], reverse=True)

# Save to CSV
import csv
with open('high_mi_pairs.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Gene1', 'Gene2', 'MutualInformation'])
    writer.writerows(high_mi_pairs)

print(f"Found {len(high_mi_pairs)} gene pairs with MI > {threshold}")
```

## Performance Guidelines

### Dataset Size Recommendations

| Genes | Estimated Time | Memory Usage | Recommendation |
|-------|---------------|--------------|----------------|
| 50    | < 1 second    | < 1 MB      | Quick testing |
| 100   | < 5 seconds   | < 5 MB      | Small analysis |
| 200   | < 30 seconds  | < 20 MB     | Medium analysis |
| 500   | < 5 minutes   | < 100 MB    | Large analysis |
| 1000  | < 30 minutes  | < 500 MB    | Very large analysis |

### Tips for Large Datasets

1. **Start small**: Always test with `--max-genes 100` first
2. **Filter aggressively**: Use higher `--min-cells` and `--min-genes-per-cell` values
3. **Monitor progress**: The progress bar shows computation status
4. **Check memory**: Large gene sets can use significant memory
5. **Save intermediate results**: Consider processing in chunks for very large datasets

## Troubleshooting

### Common Issues

1. **Out of memory**: Reduce `--max-genes` or increase filtering thresholds
2. **File already exists**: Use `--force` to overwrite
3. **No genes after filtering**: Lower `--min-cells` or `--min-genes-per-cell`
4. **Slow computation**: This is normal for large gene sets (quadratic complexity)

### Getting Help

```bash
# CLI help
python mi_cli.py --help

# Inspection help  
python inspect_pickle.py --help

# Check if library is working
python -c "import gene_mutual_info; print('Library loaded successfully!')"
```
