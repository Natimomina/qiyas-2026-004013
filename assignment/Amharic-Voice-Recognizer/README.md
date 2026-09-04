# 🎙️ Amharic Voice Gender Classification

A machine learning project for classifying **Amharic voice recordings as Male or Female** using audio signal processing and machine learning.

The project compares two approaches:

1. **MFCC + Random Forest**
2. **Mel Spectrogram + Convolutional Neural Network (CNN)**

The goal is to investigate which audio representation and model combination performs better for Amharic voice gender classification.

---

## Project Overview

Voice contains acoustic characteristics that can be used to distinguish between different classes.

In this project, we use audio recordings from Amharic speakers and extract meaningful features from the speech signal.

The system learns:

```text
Voice Recording
       ↓
Audio Preprocessing
       ↓
Feature Extraction
       ↓
┌─────────────────────────────┐
│                             │
│  MFCC Features              │
│       ↓                     │
│  Random Forest              │
│                             │
│           VS                │
│                             │
│  Mel Spectrogram             │
│       ↓                     │
│  CNN                         │
│                             │
└─────────────────────────────┘
       ↓
Male / Female
```

The model does **not** use speaker identity as an input feature.

Speaker IDs are used only to:

* derive the gender label from the dataset structure
* prevent the same speaker from appearing in both training and testing data

This makes the evaluation more representative of predicting the gender of an **unseen speaker**.

---

## Objectives

The main objectives are:

* Load and inspect Amharic speech recordings
* Understand the structure of the audio dataset
* Identify speaker and gender labels
* Analyze audio signals
* Extract MFCC features
* Analyze MFCC dimensions and time steps
* Generate Mel spectrogram representations
* Train a Random Forest classifier using MFCC features
* Train a CNN using Mel spectrograms
* Evaluate both approaches
* Compare model performance
* Save the trained models
* Build an interactive interface for gender prediction

---

## Dataset

The dataset contains **1,571 WAV audio recordings** organized by speaker.

The speaker directories contain gender information using folder names such as:

```text
amh-spk-1-M
amh-spk-2-F
amh-spk-3-F
...
```

where:

* `M` = Male
* `F` = Female

### Dataset organization

The original dataset follows a structure similar to:

```text
Amharic Audio/
│
├── amh-spk-1-M/
│   └── recording_sessions/
│       └── *.wav
│
├── amh-spk-2-F/
│   └── recording_sessions/
│       └── *.wav
│
└── ...
```

### Dataset privacy and size

The original audio dataset is not included in this repository because of its size and potential redistribution restrictions.

See:

```text
data/raw/README.md
```

for instructions on placing the dataset locally.

---

## Audio Processing

The recordings are loaded as mono audio and resampled to:

```text
Sampling Rate: 16,000 Hz
```

The project uses:

* `librosa`
* `soundfile`
* NumPy
* Pandas

The audio signal is represented as a sequence of numerical samples.

---

## MFCC Features

Mel-Frequency Cepstral Coefficients (MFCCs) are used to represent important characteristics of the speech signal.

The project extracts:

```text
13 MFCC coefficients
```

For each recording, the MFCC matrix has the general form:

```text
13 × Time Steps
```

The number of time steps depends on the duration of the recording and the selected audio-processing parameters.

For the Random Forest model, the MFCC sequence is converted into a fixed-size feature vector using:

* Mean of each MFCC coefficient
* Standard deviation of each MFCC coefficient

Therefore:

```text
13 mean features
+
13 standard deviation features
=
26 features per audio recording
```

---

## Mel Spectrogram

A Mel spectrogram represents how the frequency content of an audio signal changes over time.

It provides a two-dimensional representation:

```text
Frequency
    ↑
    │
    │   ████
    │ ███████
    │████████
    └────────────────→ Time
```

The Mel spectrogram is resized to:

```text
128 × 128
```

and used as input to the CNN.

---

## Machine Learning Models

### Model 1 — MFCC + Random Forest

The first approach uses numerical MFCC features.

```text
Audio
 ↓
MFCC
 ↓
Mean + Standard Deviation
 ↓
26 Features
 ↓
StandardScaler
 ↓
Random Forest
 ↓
Male / Female
```

### Model 2 — Mel Spectrogram + CNN

The second approach uses Mel spectrograms.

```text
Audio
 ↓
Mel Spectrogram
 ↓
128 × 128
 ↓
CNN
 ↓
Male / Female
```

The CNN contains convolutional, pooling, normalization, and dropout layers.

---

## Train/Test Strategy

A **speaker-independent split** is used.

This is important because multiple recordings can belong to the same speaker.

We do not want:

```text
Speaker A → Training
Speaker A → Testing
```

because the model could learn characteristics specific to Speaker A rather than learning general gender-related acoustic patterns.

Instead:

```text
Training Speakers
       ↓
    Training

Testing Speakers
       ↓
     Testing
```

The test set therefore contains speakers that the model did not see during training.

---

## Evaluation

The models are evaluated using:

* Accuracy
* Weighted F1-score
* Classification report
* Confusion matrix

The final comparison is presented as:

| Model                 | Accuracy | Weighted F1 |
| --------------------- | -------: | ----------: |
| MFCC + Random Forest  |        — |           — |
| Mel Spectrogram + CNN |        — |           — |

The actual values are generated after training the models.

---

## Interactive Prediction

The project includes a Gradio interface where a user can:

1. Upload an audio recording
2. Record audio using a microphone
3. Send the audio to the trained model
4. Receive the predicted gender
5. View the prediction confidence

Example:

```text
┌──────────────────────────────────┐
│   Amharic-Voice-Recognizer       │
│                                  │
│   🎤 Record / Upload Audio       │
│                                  │
│          [ Analyze ]             │
│                                  │
│   Prediction: Male               │
│   Confidence: 94.52%             │
└──────────────────────────────────┘
```

---

## Project Structure

```text
Amharic-Voice-Recognizer/
│
├── data/
│   ├── raw/
│   │   └── README.md
│   └── processed/
│       └── README.md
│
├── notebooks/
│   └── Amharic-Voice-Recognizer.ipynb
│
├── models/
│   └── README.md
│
├── outputs/
│   ├── figures/
│   └── results/
│
├── src/
│   └── README.md
│
├── README.md
├── requirements.txt
└── .gitignore
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/Natimomina/qiyas-2026-004013.git
```

Move into the project:

```bash
cd qiyas-2026-004013/assignment/Amharic-Voice-Recognizer
```

Create a virtual environment if desired:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

##  Running the Notebook

Start Jupyter Notebook:

```bash
jupyter notebook
```

Open:

```text
notebooks/Amharic-Voice-Recognizer.ipynb
```

Run the notebook cells in order.

---

## Technologies Used

| Technology         | Purpose                          |
| ------------------ | -------------------------------- |
| Python             | Programming language             |
| Jupyter Notebook   | Development and experimentation  |
| NumPy              | Numerical computation            |
| Pandas             | Dataset management               |
| Librosa            | Audio processing                 |
| SoundFile          | Audio file handling              |
| Scikit-learn       | Machine learning                 |
| TensorFlow / Keras | CNN development                  |
| Matplotlib         | Visualization                    |
| Joblib             | Model serialization              |
| Gradio             | Interactive prediction interface |

---

## Key Concepts

This project provides practical experience with:

* Digital audio
* Sampling rate
* Waveforms
* Frequency-domain analysis
* MFCC
* Mel spectrograms
* Feature extraction
* Time steps
* Random Forest
* Convolutional Neural Networks
* Train/test splitting
* Speaker leakage
* Model evaluation
* Model serialization
* Interactive machine learning applications

---

## Limitations

The model should not be interpreted as a perfect determination of a person's biological sex or gender identity.

The classifier learns patterns associated with the labels available in the training dataset.

Performance can also be affected by:

* Recording quality
* Background noise
* Microphone differences
* Speaker variation
* Dataset size
* Dataset gender balance
* Accent and pronunciation differences

Therefore, predictions should be treated as model classifications rather than definitive statements about a person.

---

## Future Improvements

Possible future improvements include:

* Increasing the number of speakers
* Adding more Amharic dialect and regional variation
* Adding noise augmentation
* Voice activity detection
* Data augmentation
* Hyperparameter optimization
* Comparing additional machine learning models
* Using CNN-LSTM architectures
* Using pretrained speech representations
* Deploying the model as a web application
* Creating an API for real-time prediction
* Adding confidence visualization

---

## Author

**Natnael Tesfaye Mekonen**

Computer Science Student
Addis Ababa, Ethiopia

GitHub: [Natimomina](https://github.com/Natimomina)

---

## 📄 License

This project is intended for educational and research purposes.