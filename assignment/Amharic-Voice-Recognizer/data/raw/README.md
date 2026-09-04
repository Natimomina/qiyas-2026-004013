# Raw Dataset

This directory is intended to contain the original Amharic audio dataset.

## Dataset

The project uses an Amharic speech dataset containing approximately **1,571 WAV recordings** organized by speaker.

The expected directory structure is:

```text
data/
└── raw/
    └── Amharic Audio/
        ├── amh-spk-1-M/
        ├── amh-spk-2-F/
        ├── amh-spk-3-F/
        └── ...
```

The dataset itself is **not included in this GitHub repository** because of its large size and dataset redistribution considerations.

## Setup

After obtaining the dataset, place the `Amharic Audio` directory inside:

```text
data/raw/
```

The notebook should then point to:

```python
DATASET_DIR = Path("../data/raw/Amharic Audio")
```
