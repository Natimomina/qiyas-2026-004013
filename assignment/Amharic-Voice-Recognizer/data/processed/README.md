# Processed Data

This directory contains data generated during preprocessing and feature extraction.

Possible generated files include:

```text
processed/
├── mfcc_features.csv
└── ...
```

The MFCC dataset contains numerical features extracted from the original audio recordings.

For each recording, the project extracts:

* 13 MFCC coefficients
* Mean of each coefficient
* Standard deviation of each coefficient

This produces:

```text
26 MFCC-derived features per audio recording
```

Large generated datasets and temporary files should not be committed unless they are intentionally included for reproducibility.

The notebook can regenerate the processed data from the original audio dataset.
