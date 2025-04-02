## Test Data Set # 2

This data set is from two different experiments which we want to analyze together. For each experiment, barcoded cells were taken at an early timepoint and at a later timepoint (35 days for H1806, 48 days for MB231). We want to estimate the growth rate of each clone in each experiment for the clones that present in both timepoints in each experiment.

A csv is provided with the average growth rates of the bulk population (R) for each experiment:
- The average growth rate of the H1806 population can be estimated (R) as ~ 0.025 \[1/hr\]
- The average growth rate of the MB231 population can be estimated (R) as ~ 0.020 \[1/hr\]

The data set contains the following files:
- 'data.tsv' show each barcode and their corresponding percentage within each sample in each experimental group. These are outputs from `pycashier receipt`. This can be loaded into clonegro as `--data data/test_data_2/data.tsv`
- 'meta.csv' maps each sample to a sample group, passage number, and time point (in hours). Note that some samples are assigned to multiple sample_groups separated by a comma. This meta data can be loaded into clonegro as `--meta data/test_data_2/meta.csv`
- 'bulk_growth_rates.csv' contains the average growth rates of the bulk population (R) for each experiment. This can be loaded into clonegro as `--growths data/test_data_2/bulk_growth_rates.csv`

To run this at the command line, try:
`clongro --data data/test_data_2/data.tsv --meta data/test_data_2/meta.csv --growths data/test_data_2/bulk_growth_rates.csv --outs clongro_test_data_2_outs`