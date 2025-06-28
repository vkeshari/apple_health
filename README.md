# apple_health

> [!IMPORTANT]
> You may use the code in this repository for your own analysis of apple health data,
> but **you must attribute references to this or any derivative work to the original author**.

The Apple Health library can processes, aggregate, compare and visualize fitness data
exported by Apple Health.

# Code Structure
`params.py`: All config lives here. Treat this as command-line params.

## Prerequisites
Data exported from Apple Health contains a file named `export.xml`.
* Save this file under `data/raw`, renaming if necessary.
* Set `params.ParserParams.INPUT_FILENAME` to the file's name, exclusing directory path.
* Set `params.DataParams` as per your requirements.
* Run the scripts below.

## Common Config
See `params.py`
* `params.RecordParams`: Contains expected unit types and desired aggregation types for daily data
  for each `RecordType`
  * If `AggregationType` is `SUM`, all values are added to get daily data. 
  * If `AggregationType` is `AVERAGE` or `MEDIAN`, first hourly averages are calculated
    and then the respective average or median is calculated on those hourly averages
    to get daily aggregated data.

* `params.DataParams`: Configures which CSV files to use for data analysis.
> [!NOTE]
> All scripts use the same `params.DataParams` to locate CSV files containing parsed data.
>
> Use `params.DataParams.SUFFIX` to create multiple aggregations from the same raw XML data.
> Suffixes should be of the form `_XYZNAME`.

## Data Processing
* `parse_data.py`: Parses raw XML data into a CSV file containing daily aggregates for all data.
  * Configure using `params.ParserParams`
  * A summary of XML data can be shown for debugging by setting `par.ParserParams.SHOW_SUMMARY`
    and `par.XmlDebugParams`. 
  * See also: `params.RecordParams` above.

* `aggregate_data.py`: Aggregates daily values into weekly, monthly or quarterly values.
  * Configure using `params.AggregatorParams`
  * All aggregations are averages of daily values from `parse_data.py`.

Output files will be saved under `data/processed`.
These files will be used by all analysis scripts below.

## Data Analysis
* `build_graphs.py`: Saves line graphs and histograms for each record type.
  * Configure using `params.GraphParams`
  * Line graphs are saved in `out/line`
  * Histograms are saved in `out/hist/singleseries`.
    Histograms are only created for record types with `AggregationType = SUM`

* `bucketed_graphs.py`: Splits data into multiple groups and creates overlapping histograms
  of their distributions.
  * Configre using `params.BucketedGraphParams`
  * Histograms are saved in `out/hist/multiseries`.
    Histograms are only created for record types with `AggregationType = SUM`

* `bucketed_tuning.py`: Creates interval graphs of distribution of average values of data subsets
  when data is randomly split into varying no. of buckets for each record type.
  * Configure using `params.BucketTuningParams`
  * Tuning graphs are saved in `out/tuning`

* `record_comparison.py`: Creates scatter plots of all values between pairs of record types
  that show high correlation. It will compare both raw and delta values of records
  in the same period and in offset periods.
  > For example, it can compare weekly StepCount values to weekly changes (deltas) in
  > RestingHeartRate values two weeks later.
  * Configure using `params.RecordComparisonParams`
  * Scatter plots are saved in `out/comparison`

> [!NOTE]
> This script runs in multiple processes. The output graphs might be in different folders
> with adjacent timestamps.

* `distribution_fit.py`: Checks what distribution(s) can fit data for given record-type.
  * Configure using `params.DistributionFitParams`

> [!WARNING]
> This script runs slowly and shows a lot of debug information. It also doesn't seem to fit data particularly well.
