# Environment Notes

This project is developed in WSL Ubuntu using the `pds` conda environment.

## Activate Environment

Run this command before working on the project:

    conda activate pds

## Main Packages Used

- pandas
- duckdb
- matplotlib
- streamlit

## Check Environment

Useful commands:

    which python
    python --version
    python -c "import pandas as pd; print('pandas:', pd.__version__)"
    python -c "import duckdb; print('duckdb:', duckdb.__version__)"
    python -c "import streamlit; print('streamlit:', streamlit.__version__)"

## Notes

The `pds` environment is used for Python, pandas, DuckDB, EDA, visualisation, and dashboard work.
