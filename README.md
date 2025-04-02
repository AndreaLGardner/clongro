# clongro

Simple code to estimate the exponential growth rate of each clone in a barcoded cell population from targeted barcode sequencing data from at least two timepoints.

#### Getting started
Install `clongro` using pip:
```
pip install clongro
```

#### How it works
$t_0$ : Initial time $[h]$\
$t_f$ : Final time $[h]$\
$t :$ Time in hours between $t_0$ and $t_f$ $[h]$\
${N_{pop}}_0$ : Total number of cells in the bulk population at inital time $t_0$ $[cells]$\
${N_{pop}}_f$ : Total number of cells in the bulk population at final time $t_f$ $[cells]$\
$R :$ Growth rate of bulk population $[h^{-1}]$\
${N_0}_i:$ Initial number of cells of clone $i$ in the population at inital time $t_0$ $[cells]$\
${N_f}_i:$ Final number of cells of clone $i$ in the population at final time $t_f$ $[cells]$\
${r}_i :$ Growth rate of clone $i$ $[h^{-1}]$\
${percent_i}_0$ : Percent of clone $i$ in the bulk population at inital time $t_0$ $[percent]$\
${percent_i}_f$ : Percent of clone $i$ in the bulk population at final time $t_f$ $[percent]$
___


First, we show how to determine the exponential growth rate of a bulk population from:

${N_{pop}}_f = {N_{pop}}_0exp{(Rt)}$

![test](https://latex.codecogs.com/svg.image?\large&space;\bg{white}${N_{pop}}_f={N_{pop}}_{0}exp{(Rt)}$)


Solving for growth rate ${R}$ as:

$R = {\dfrac{1}{t}}log \Biggl({\dfrac{{N_{pop}}_f}{{N_{pop}}_0}}\Biggr)$


Now, if we want to determine the growth rate of each clone in the population, we can use the same equation as above but for each clone $i$ from:

${N_f}_i = {N_0}_iexp{(r_i*t)}$

Solving for clonal growth rate ${r}_i$ as:

$r_i = {\dfrac{1}{t}}log({\dfrac{{N_f}_i}{{N_0}_i}})$


From targeted barcode sequencing data we know the percent of each clone in the population. Given that we know the size of the bulk population (${N_{pop}}$) and the percent of each clone within the total population, then for each clone $i$, it's total cell number in the population can be computed as:

$N_i = {N_{pop}}(\dfrac{percent_i}{100})$

This can be used as ${N_f}_i$ and ${N_0}$ in the clonal growth rate equation:

$r_i = {\dfrac{1}{t}}log({\dfrac{{{N_{pop}}_f}({percent_i}_f /\ {100})}{{{{N_{pop}}_0}({percent_i}_0 /\ {100})}}}$

Which given log rules can be re-written as:

$r_i = {\dfrac{1}{t}}log({\dfrac{{{N_{pop}}_f}}{{N_{pop}}_0}}) + {\dfrac{1}{t}}log(\dfrac{{percent_i}_0}{{percent_i}_f})$

In this form, we note that the first term on the right side of the equation is simply the growth rate of the total population $R$ and the second term becomes a scaling factor for each clone.

$r_i = R + {\dfrac{1}{t}}log(\dfrac{{percent_i}_0}{{percent_i}_f})$

`clongro` uses the percent of each clone from targeted barcode sequencing and the time between each targeted sequencing run to calculate this growth rate scaling factor for each clone. 

If the growth rate of the bulk population $R$, is known, then true growth rate estimates can be determined for each clone by simply adding this scaling factor to the bulk growth rate. `clongro` returns these values as `est_r_i_scaled` in the output csv.

If the growth rate of the bulk population R is not know, then `clongro` uses $R=0$ and returns the computed scaling factor as the unscaled estimate for growth rate of each clone. Even without a known bulk population growth rate ($R$), the unscaled estimates for $r_i$ encode for relative relationships between clones and can be used to identify clones that are growing faster (`est_r_i > 0`) or slower (`est_r_i < 0`) than the bulk population.




#### Required inputs
`clongro` requires two input tsv/csv files and can be run simply as:

```
clongro --data {PATH_TO_YOUR_BARCODE_DATA} --meta {PATH_TO_YOUR_METADATA}
```

1. `--data` A csv or tsv in long format with named columns for 'barcode', 'sample', and 'percent'. If you have run pycashier on your targetted sequencing data, results of pycashier 'receipt' can be used directly here. This can be formatted manually, but ensure that each barcode gets a unique row for each sample/timepoint.

2. `--meta` A csv or tsv with named columns for 'sample', 'time', and 'sample_group'. This maps each sample to a specific experimental timepoint. The time column should be in hours. If you are only running one experiment, then sample_group can be left blank or you can give both samples the same sample_group name, e.g. 'A' in the example below


| sample                  | time | sample_group |
|-------------------------|------|--------------|
| my_barcoded_cells_early | 0    | A            |
| my_barcoded_cells_late  | 840  | A            |


Each sample_group must map to two samples, one denoting the initial timepoint and the other denoting the later timepoint. sample_group can be used to estimate growth rates of clones from separate experiments in a single run of clongro, e.g. 

| sample     | time | sample_group |
|------------|------|--------------|
| HEK_early  | 0    | A            |
| HEK_late   | 840  | A            |
| MCF7_early | 0    | B            |
| MCF7_late  | 1000 | B            |


When `clongro` is run with just `--data` and `--meta`, it will return a csv (default: `outs/clongro_outs.csv`) which contains unscaled, relative estimates of clonal growth rates for each clonal population that was detected and quantified in both timepoints. Barcodes which were not identified in both timepoints will return null for growth rates.



#### Optional inputs to estimate true growth rate

##### Single population growth rate for all sample groups
If you are only running one sample_group or all sample_groups are estimated to have the same bulk population growth rate ($R$), then the bulk population growth rate in $h^{-1}$ can be supplied at the command line. To call this option at the command line, use the `--pop-growth-rate` flag, i.e.:

```
clongro --data {PATH_TO_YOUR_BARCODE_DATA} --meta {PATH_TO_YOUR_METADATA} --pop-growth-rate 0.02
```
`clongro` will return a csv (default: `outs/clongro_outs.csv`) with scaled estimates of clonal growth rates for each barcode that was detected and quantified in both timepoints. Barcodes which were not identified in both timepoints will return null for growth rates.


##### Different growth rates for each sample_group
If you are running clongfrom with sample_groups are estimated to have the different bulk population growth rates ($R$), then a csv should be provided mapping each sample_group to its known bulk population growth rate.

Data must have named columns for 'sample_group' and 'bulk_growth_rate_R' in inverse hours $h^{-1}$. Groups in 'sample_group' must match those in the sample metadata. The mean population growth rate (`bulk_growth_rate_R`) can be estimated from cell counting, live-cell imaging, or other methods. Providing this file is optional, but it will allow for true estimates of clonal growth rates within each sample_group. An example is below:

| sample_group | bulk_growth_rate_R |
|--------------|--------------------|
| A            | 0.02               |
| B            | 0.025              |

To call this option at the command line, use the `--growths` flag and point to a tsv/csv containing your growth rate data with the columns properly names, i.e.:

```
clongro --data {PATH_TO_YOUR_BARCODE_DATA} --meta {PATH_TO_YOUR_METADATA} --growths{PATH_TO_GROWTH_RATE_METADATA}
```
`clongro` will return a csv (default: `outs/clongro_outs.csv`) with scaled estimates of clonal growth rates for each barcode in each sample_group that was detected and quantified in both timepoints for that sample_group. Barcodes which were not identified in both timepoints will return null for growth rates.



#### More complex meta data sample_group examples

In the meta data file, sample_group can also be used to map a single sample to multiple groups using comma separation, such as the case where multiple replicates are split off from a shared initial timepoint, e.g.

| sample                      | time | sample_group |
|-----------------------------|------|--------------|
| my_barcoded_cells_early     | 0    | A,B,C,D,E    |
| my_barcoded_cells_late_rep1 | 840  | A            |
| my_barcoded_cells_late_rep2 | 840  | B            |
| my_barcoded_cells_late_rep3 | 840  | C            |
| my_barcoded_cells_late_rep4 | 840  | D            |
| my_barcoded_cells_late_rep5 | 840  | E            |

Or if sequential passaging was performed, the sample_group column can contain multiple groups separated by commas to indicate use as the initial timepoint for one sample_group and the final timepoint for another from as in one of the example data sets provided:

`data/test_data_1/meta.csv`
| sample           | sample_group | passage | time |
|------------------|--------------|---------|------|
| JA21116-libB3    | A            | 15      | 0    |
| JA22214-1KB3-P17 | A,B          | 17      | 144  |
| JA22214-1KB3-P19 | B,C          | 19      | 288  |
| JA22214-1KB3-P21 | C,D          | 21      | 432  |
| JA22214-1KB3-P23 | D,E          | 23      | 576  |
| JA22214-1KB3-P25 | E,F          | 25      | 720  |
| JA22214-1KB3-P27 | F,G          | 27      | 864  |
| JA22214-1KB3-P29 | G,H          | 29      | 1008 |
| JA22214-1KB3-P31 | H            | 31      | 1152 |


#### Running example data
Two data sets are provided which can be run as examples, to learn more about the unique setups in each experiment, refererence the ABOUT.md files in each test_data subdirectory.

To run test data set #1
```
clongro --data data/test_data_1/data.tsv --meta data/test_data_1/meta.csv --pop-growth-rate 0.02 --outs clongro_test_data_1_outs
```

To run test data set #2
```
clongro --data data/test_data_2/data.tsv --meta data/test_data_2/meta.csv --growths data/test_data_2/bulk_growth_rates.csv --outs clongro_test_data_2_outs
```


#### Understanding outputs
The returned outputs will retain columns supplied in the meta data files and will minimally have columns for 'barcode', 'sample_group', 'interval', 'duration', 'est_r_i', 'bulk_growth', and 'est_r_i_scaled'.

Barcodes which were not detected in both timepoints are removed by default, to return all data including null values in the output, use the flag `--drop-empty False`

Column info:
- barcode: name of the clone
- sample_group: the group containing the set of before and after data used to estimate this growth rate
- interval: exact time interval used for this calculation, i.e. time0_timef $[h]$
- duration: time beween initial and final timepoints (equivalent to $t$ in the exponential growth equations) $[h]$
- est_r_i : unscaled relative growth rate (i.e. the mathematically derived 'growth rate scaling factor') $[h^{-1}]$
- bulk_growth: the bulk population growth rate ($R$) supplied by the user. Default is 0. $[h^{-1}]$
- est_r_i_scaled : scaled growth rate (i.e. $r_i$ ) $[h^{-1}]$

The most important output is `est_r_i_scaled` this is the estimated growth rate of for each barcode within each sample group. If bulk growth rate ($R$) was provided, than `est_r_i_scaled` is closer to true estimate of growth rate. If bulk growth rate was not provided, this is a relative estimate of clonal growth rate compared the the population average.
