## Test Data Set # 1

This data set is from an experiment in which barcoded cells were passaged over 48 days and sampled at every other passage.

The average growth rate of the bulk population (R) was ~ $0.02$ $h^{-1}$

The data set contains the following files:
- 'data.tsv' show the barcodes and their corresponding percentage within each sample at each passage. These are outputs from `pycashier receipt`. This can be loaded into clonegro as `--data data/test_data_1/data.tsv`
- 'meta.csv' maps each sample to a sample group, passage number, and time point (in hours). Note that some samples are assigned to multiple sample_groups separated by a comma. This meta data can be loaded into clonegro as `--meta data/test_data_1/meta.csv`

In this setup, we want to estimate the growth of each clone at each passage and the `sample_group` identifier can be taken advantage for this. For example, we assigned passage 15 to group A, passage 17 to group A and group B, and passage 19 to group B and C. This means that growth rates for each clone will be independently estimated between passage 15 and 17 (group A), between passage 17 and 19 (group B), and so forth. 

To run this at the command line, try:
```
clongro --data data/test_data_1/data.tsv --meta data/test_data_1/meta.csv --pop-growth-rate 0.02 --outs clongro_test_data_1_outs
```