# Amharic (Ge'ez) Digit Recognition Using CNN

A computer vision and deep learning project for recognizing **Amharic/Ge'ez numerical characters** using a Convolutional Neural Network (CNN).

The project focuses on recognizing nine Ge'ez digits:

**፩ ፪ ፫ ፬ ፭ ፮ ፯ ፰ ፱**

The original dataset contains images with different dimensions and color modes. An image preprocessing pipeline is used to standardize the images before training the CNN.

---

## Project Overview

Amharic uses Ge'ez numerals to represent numbers. In this project, image classification is used to automatically recognize nine Ge'ez numerical characters.

The complete workflow is:

```text
Raw Dataset
     ↓
Dataset Inspection
     ↓
Image Preprocessing
     ↓
Grayscale Conversion
     ↓
Find Maximum Width & Height
     ↓
Zero Padding
     ↓
Normalized Image Dataset
     ↓
Train/Test Split
     ↓
CNN Training
     ↓
Model Evaluation
     ↓
Ge'ez Digit Prediction
```

---

## Classes

The project currently contains **9 classes**:

| Class | Ge'ez Digit |
| ----: | :---------: |
|     1 |      ፩      |
|     2 |      ፪      |
|     3 |      ፫      |
|     4 |      ፬      |
|     5 |      ፭      |
|     6 |      ፮      |
|     7 |      ፯      |
|     8 |      ፰      |
|     9 |      ፱      |

> **Note:** The dataset currently does not contain the Ge'ez digit ፲ (10), so this project is a 9-class classification problem.

---

## Dataset

The dataset consists of images representing the nine Ge'ez numerical characters.

The raw dataset is approximately **1.69 MB** and is included in:

```text
data/raw/
```

The images have different:

* Dimensions
* Color modes
* Image characteristics

The notebook automatically processes the images before they are used for machine learning.

### Dataset Structure

```text
data/
└── raw/
    └── amharic_digit_dataset.zip
```

The ZIP file contains the original class folders.

---

## Image Preprocessing

The images are not initially standardized, so preprocessing is performed before CNN training.

### 1. Image Loading

Images are loaded using **Pillow (PIL)**.

### 2. Grayscale Conversion

Different color images are converted to grayscale so that the model focuses primarily on the shape of the Ge'ez character.

### 3. Maximum Dimensions

Instead of forcing every image into an arbitrary fixed size such as 128×128, the preprocessing pipeline determines:

```text
Maximum Width
Maximum Height
```

from the dataset.

These dimensions are then used as the standard image dimensions.

### 4. Zero Padding

Images that are smaller than the maximum dimensions are placed inside a NumPy array initialized with zeros.

Conceptually:

```text
Original image
      ↓
┌─────────────────────┐
│                     │
│      Character      │
│                     │
└─────────────────────┘
      ↓
Maximum-size canvas
      ↓
Unused areas = 0
```

This ensures that every image has the same dimensions without unnecessarily distorting the original character.

### 5. Pixel Normalization

Pixel values are converted from:

```text
0 – 255
```

to:

```text
0 – 1
```

using:

```python
X = X / 255.0
```

---

## CNN Model

A Convolutional Neural Network is used to classify the images.

The model contains:

* Convolutional layers
* ReLU activation functions
* Max pooling
* Dense layers
* Dropout
* Softmax output layer

The final layer contains **9 neurons**, one for each Ge'ez digit class.

```text
Input Image
     ↓
Convolution
     ↓
Pooling
     ↓
Convolution
     ↓
Pooling
     ↓
Convolution
     ↓
Pooling
     ↓
Flatten
     ↓
Dense Layer
     ↓
Dropout
     ↓
9-Class Softmax
     ↓
፩ ፪ ፫ ፬ ፭ ፮ ፯ ፰ ፱
```

---

## Model Evaluation

The project evaluates the CNN using:

### Accuracy

Measures the percentage of correctly classified images.

### Classification Report

Provides:

* Precision
* Recall
* F1-score

for each Ge'ez digit.

### Confusion Matrix

Shows which Ge'ez digits the model correctly recognizes and which classes it confuses.

---

## Jupyter Notebook

The main implementation is available in:

```text
notebooks/amharic_geez_9_class_cnn.ipynb
```

The notebook contains the complete workflow:

1. Import libraries
2. Extract dataset
3. Inspect dataset
4. Analyze image dimensions and formats
5. Display sample images
6. Preprocess images
7. Find maximum image dimensions
8. Apply zero padding
9. Save processed images
10. Load images into NumPy arrays
11. Normalize pixel values
12. Split dataset
13. Build CNN
14. Train model
15. Evaluate model
16. Generate classification report
17. Generate confusion matrix
18. Visualize predictions
19. Save trained model

---

## 🚀 How to Run

### 1. Clone the repository

```bash
git clone https://github.com/Natimomina/amharic-geez-digit-recognition.git
```

### 2. Enter the project directory

```bash
cd amharic-geez-digit-recognition
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the environment

On Windows:

```bash
venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Start Jupyter Notebook

```bash
jupyter notebook
```

Then open:

```text
notebooks/amharic_geez_9_class_cnn.ipynb
```

Run the cells from top to bottom.

---

## Technologies Used

* Python
* NumPy
* Pandas
* Pillow
* Matplotlib
* Scikit-learn
* TensorFlow
* Keras
* Jupyter Notebook

---

## Project Structure

```text
amharic-geez-digit-recognition/
│
├── data/
│   ├── raw/
│   │   └── amharic_digit_dataset.zip
│   └── processed/
│       └── README.md
│
├── notebooks/
│   └── amharic_geez_9_class_cnn.ipynb
│
├── models/
│   └── README.md
│
├── README.md
├── requirements.txt
├── .gitignore
└── LICENSE
```

---

## Dataset Limitation

The current dataset is relatively small, with approximately **113 images across 9 classes**.

Because of the limited number of samples, the CNN may experience **overfitting**.

The model's performance should therefore not be interpreted as a production-ready Ge'ez digit recognition system.

Future versions should use a larger and more diverse dataset.

---

## Future Improvements

Possible improvements include:

* Collect more Ge'ez digit images
* Add the missing ፲ class
* Increase the number of samples per class
* Improve data augmentation
* Experiment with different CNN architectures
* Compare CNN with traditional machine-learning approaches
* Add image preprocessing techniques such as noise removal and thresholding
* Build a web interface for uploading an image and predicting its Ge'ez digit
* Deploy the trained model as an API
* Create a real-time Ge'ez digit recognition application

---

## Learning Objectives

This project demonstrates practical experience with:

* Computer vision
* Image preprocessing
* Image normalization
* NumPy arrays
* Dataset preparation
* Supervised learning
* CNN architecture
* Model training
* Model evaluation
* Classification reports
* Confusion matrices
* Deep learning with TensorFlow/Keras

---

## Author

**Natnael Tesfaye**

Computer Science Student | AI & Data Analysis Enthusiast

---

## License

This project is intended for educational and research purposes.

Before redistributing the dataset, verify that its original license or source permits redistribution.
