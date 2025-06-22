use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use numpy::PyReadonlyArray2;
use rayon::prelude::*;
use std::collections::HashMap;
use thiserror::Error;
use indicatif::{ProgressBar, ProgressStyle};
use std::sync::Mutex;

#[derive(Error, Debug)]
pub enum MutualInfoError {
    #[error("Matrix and gene labels have different lengths: matrix has {matrix_rows} rows, but {gene_count} genes provided")]
    DimensionMismatch { matrix_rows: usize, gene_count: usize },
    #[error("Empty input: matrix or gene list is empty")]
    EmptyInput,
}

impl std::convert::From<MutualInfoError> for PyErr {
    fn from(err: MutualInfoError) -> PyErr {
        PyErr::new::<pyo3::exceptions::PyValueError, _>(err.to_string())
    }
}

/// Compute mutual information between two discrete random variables
fn mutual_information(x: &[f64], y: &[f64]) -> f64 {
    let n = x.len();
    if n == 0 { return 0.0; }
    
    // Create joint and marginal frequency maps
    let mut joint_freq: HashMap<(i32, i32), usize> = HashMap::new();
    let mut x_freq: HashMap<i32, usize> = HashMap::new();
    let mut y_freq: HashMap<i32, usize> = HashMap::new();
    
    // Discretize continuous values using simple binning
    // For gene expression data, we'll use quantile-based binning
    let mut x_sorted = x.to_vec();
    let mut y_sorted = y.to_vec();
    x_sorted.sort_by(|a, b| a.partial_cmp(b).unwrap());
    y_sorted.sort_by(|a, b| a.partial_cmp(b).unwrap());
    
    let bins = 10; // Number of bins for discretization
    
    for i in 0..n {
        let x_bin = discretize_value(x[i], &x_sorted, bins);
        let y_bin = discretize_value(y[i], &y_sorted, bins);
        
        *joint_freq.entry((x_bin, y_bin)).or_insert(0) += 1;
        *x_freq.entry(x_bin).or_insert(0) += 1;
        *y_freq.entry(y_bin).or_insert(0) += 1;
    }
    
    // Calculate mutual information
    let mut mi = 0.0;
    let n_f = n as f64;
    
    for (&(x_val, y_val), &joint_count) in &joint_freq {
        let p_xy = joint_count as f64 / n_f;
        let p_x = x_freq[&x_val] as f64 / n_f;
        let p_y = y_freq[&y_val] as f64 / n_f;
        
        if p_xy > 0.0 && p_x > 0.0 && p_y > 0.0 {
            mi += p_xy * (p_xy / (p_x * p_y)).ln();
        }
    }
    
    mi
}

/// Discretize a continuous value based on quantiles
fn discretize_value(value: f64, sorted_values: &[f64], bins: usize) -> i32 {
    let n = sorted_values.len();
    if n == 0 { return 0; }
    
    for i in 1..bins {
        let quantile_idx = (i * n) / bins;
        if quantile_idx < n && value <= sorted_values[quantile_idx] {
            return (i - 1) as i32;
        }
    }
    (bins - 1) as i32
}

/// Compute pairwise mutual information for all gene pairs in a matrix
#[pyfunction]
fn compute_mutual_information(
    py: Python<'_>,
    matrix: PyReadonlyArray2<f64>,
    genes: &Bound<'_, PyList>,
) -> PyResult<PyObject> {
    let matrix = matrix.as_array();
    let gene_names: Vec<String> = genes
        .iter()
        .map(|item| item.extract::<String>())
        .collect::<Result<Vec<_>, _>>()?;
    
    // Validate input dimensions
    if matrix.nrows() != gene_names.len() {
        return Err(MutualInfoError::DimensionMismatch {
            matrix_rows: matrix.nrows(),
            gene_count: gene_names.len(),
        }.into());
    }
    
    if matrix.nrows() == 0 || matrix.ncols() == 0 {
        return Err(MutualInfoError::EmptyInput.into());
    }
    
    let n_genes = gene_names.len();
    
    // Create progress bar
    let total_pairs = (n_genes * (n_genes + 1)) / 2; // Including diagonal
    let progress_bar = ProgressBar::new(total_pairs as u64);
    progress_bar.set_style(
        ProgressStyle::default_bar()
            .template("{spinner:.green} [{elapsed_precise}] [{bar:40.cyan/blue}] {pos}/{len} ({eta}) {msg}")
            .unwrap()
            .progress_chars("#>-")
    );
    progress_bar.set_message("Computing mutual information...");
    
    // Create result dictionary
    let result = PyDict::new(py);
    
    // Compute mutual information for all pairs in parallel
    let gene_pairs: Vec<(usize, usize)> = (0..n_genes)
        .flat_map(|i| (i..n_genes).map(move |j| (i, j)))
        .collect();
    
    let progress_counter = Mutex::new(0);
    let mi_results: Vec<((usize, usize), f64)> = gene_pairs
        .par_iter()
        .map(|&(i, j)| {
            let row_i = matrix.row(i);
            let row_j = matrix.row(j);
            let mi = if i == j {
                // Self-mutual information (entropy)
                mutual_information(row_i.as_slice().unwrap(), row_i.as_slice().unwrap())
            } else {
                mutual_information(row_i.as_slice().unwrap(), row_j.as_slice().unwrap())
            };
            
            // Update progress bar
            {
                let mut counter = progress_counter.lock().unwrap();
                *counter += 1;
                progress_bar.set_position(*counter as u64);
            }
            
            ((i, j), mi)
        })
        .collect();
    
    progress_bar.finish_with_message("Mutual information computation completed!");
    
    // Build nested dictionary structure
    for ((i, j), mi_value) in mi_results {
        let gene_i = &gene_names[i];
        let gene_j = &gene_names[j];
        
        // Get or create inner dictionary for gene_i
        if !result.contains(gene_i)? {
            let new_dict = PyDict::new(py);
            result.set_item(gene_i, new_dict)?;
        }
        let item = result.get_item(gene_i)?.unwrap();
        let inner_dict = item.downcast::<PyDict>()?;
        inner_dict.set_item(gene_j, mi_value)?;
        
        // For symmetric matrix, also set the reverse mapping (unless it's the diagonal)
        if i != j {
            if !result.contains(gene_j)? {
                let new_dict = PyDict::new(py);
                result.set_item(gene_j, new_dict)?;
            }
            let item_j = result.get_item(gene_j)?.unwrap();
            let inner_dict_j = item_j.downcast::<PyDict>()?;
            inner_dict_j.set_item(gene_i, mi_value)?;
        }
    }
    
    Ok(result.into())
}

/// A Python module implemented in Rust for computing gene mutual information.
#[pymodule]
fn gene_mutual_info(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(compute_mutual_information, m)?)?;
    Ok(())
}
