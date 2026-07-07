# Fuel Price Prediction with PySpark

Forecasting daily fuel prices for the gas stations of A Coruna (Spain) on 1.6M records: a full Spark ML pipeline with temporal feature engineering, leakage-free splits and Optuna hyperparameter search.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![PySpark](https://img.shields.io/badge/PySpark-3.5%2B-orange)
![Optuna](https://img.shields.io/badge/Optuna-3.6%2B-purple)
![License](https://img.shields.io/badge/license-MIT-green)

## Overview

Spanish gas stations report their prices daily to the government, which publishes them as open data. This project takes the historical series for the province of A Coruna (1,628,611 station-day records, 24 columns: per-fuel prices plus station metadata) and predicts the price of three target fuels: regular gasoline (95 E5), diesel (gasoleo A) and LPG (GLP).

Everything runs on PySpark, from exploratory statistics to model training, so the same notebook scales beyond a single machine. Hyperparameters are tuned with Optuna using a strictly temporal validation split.

## Results

Final test metrics (temporal 80/20 split per station, models tuned with Optuna on MAE):

| Target fuel | Model | MAE (EUR/L) | R2 |
|---|---|---|---|
| Diesel (gasoleo A) | **Linear Regression** | **0.0135** | **0.996** |
| Diesel (gasoleo A) | Random Forest | 0.0505 | 0.938 |
| Diesel (gasoleo A) | GBT | 0.0550 | 0.926 |
| Gasoline 95 E5 | **Linear Regression** | **0.0117** | **0.995** |
| Gasoline 95 E5 | Random Forest | 0.0449 | 0.929 |
| Gasoline 95 E5 | GBT | 0.0444 | 0.930 |
| LPG (GLP) | **Linear Regression** | **0.0056** | **0.995** |
| LPG (GLP) | Random Forest | 0.0093 | 0.986 |
| LPG (GLP) | GBT | 0.0105 | 0.983 |

Linear regression wins across all three fuels, and the reason is instructive: once each station's own lagged prices and rolling means enter the feature set, next-day prediction becomes an almost autoregressive problem where a well-regularized linear model on standardized features is hard to beat, while tree ensembles pay for their coarse piecewise-constant approximation of a smooth signal.

## What the notebook does

`fuel_price_prediction.ipynb` walks the full pipeline:

1. **EDA at scale.** Null counts and cardinality per column, distribution plots, a mixed correlation matrix (numeric and categorical), normality tests and per-feature significance against each target, all computed in Spark.
2. **Temporal feature engineering.** Cyclic encodings for calendar features (day of week, month, day of year), and per-station windows over the price series: lags of 1, 7 and 14 days, rolling means over 7 and 14 days, and 14-day rolling standard deviation. Windows are defined over `Window.partitionBy(station).orderBy(timestamp)` with range frames, so no future information leaks into any feature.
3. **Checkpointing.** The engineered dataset is materialized once to `data/df_full.csv` and reloaded from disk on subsequent runs, skipping the expensive window computations.
4. **Feature selection.** Random Forest importance computed on a stratified subsample, keeping the most informative features per target.
5. **Leakage-free evaluation.** The train/test split is temporal (first 80% vs last 20% of each station's history), and Optuna's validation split is again temporal inside the training set, so tuning never sees the future.
6. **Model tuning.** Optuna studies (TPE sampler, MAE objective) for Linear Regression, Random Forest and GBT, one study per model and target fuel, with per-trial results saved to CSV. Final models are retrained on the full training set and evaluated on the held-out test period.

## Getting started

Requires Java 17+ (PySpark runs on the JVM) and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run jupyter lab   # open fuel_price_prediction.ipynb
```

### Data

The raw data comes from the Spanish government's open fuel price service: [Geoportal Gasolineras](https://geoportalgasolineras.es/) (Ministerio para la Transicion Ecologica), which also offers a [REST API](https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/) with historical daily prices per station. The notebook expects the A Coruna subset as a pipe-delimited CSV at `data/coruna.csv` with one row per station and day, per-fuel price columns (`price_g95e5`, `price_goa`, `price_glp`, ...) and station metadata (id, company, address, coordinates, locality).

`data/` is git-ignored; nothing under it is ever committed.

## Project structure

```
.
├── fuel_price_prediction.ipynb   # The full pipeline: EDA, features, models, Optuna
├── pyproject.toml                # Dependencies (uv-native project)
├── uv.lock                       # Locked environment (uv sync)
└── data/                         # Local data, git-ignored
    └── coruna.csv
```

Generated artifacts (the `df_full.csv` checkpoint and `optuna_studies/` trial CSVs) are git-ignored too.

## Credits

Team project built together with [Pablo Fernández (@appuchias)](https://github.com/appuchias) and [Miguel Planas (@miguelplanas)](https://github.com/miguelplanas).

## References

- T. Akiba et al. (2019). *Optuna: A Next-generation Hyperparameter Optimization Framework*. KDD.
- J. Bergstra et al. (2011). *Algorithms for Hyper-Parameter Optimization* (TPE). NeurIPS.
- M. Zaharia et al. (2016). *Apache Spark: A Unified Engine for Big Data Processing*. CACM.

## License

[MIT](LICENSE)
