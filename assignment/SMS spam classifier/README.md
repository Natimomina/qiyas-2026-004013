# SMS Spam Classifier

A machine-learning project that classifies SMS messages as HAM or SPAM.  
The project trains multiple text-classification pipelines on the SMSSpamCollection dataset, compares them by performance, saves the best pipeline into a `.pkl` bundle, and loads that bundle in a Gradio web app for live classification.

## Project files

- `Sms_Spam_Classifier_Project_new.ipynb` — training, evaluation, model selection, and Gradio app code
- `SMSSpamCollection` — the training dataset (tab-separated `label` and `message` columns)
- `spam_pipeline_bundle.pkl` — the saved production bundle containing the selected model, vectorizer, and evaluation results

## How the project works

1. The dataset is loaded from `SMSSpamCollection`.
2. The text is cleaned by:
   - converting to lowercase
   - removing URLs, numbers, and punctuation
   - removing English stop words
3. The notebook trains and compares several models with both **TF-IDF** and **CountVectorizer**.
4. The best pipeline is selected based on **F1 score**.
5. The selected pipeline is saved into `spam_pipeline_bundle.pkl`.
6. The Gradio app loads that bundle and performs:
   - single message classification
   - batch classification from `.csv` or `.txt`
   - model information display

## Features

- SMS spam vs ham prediction
- Confidence score output
- Keyword highlighting for likely spam words
- Message signal statistics
- Batch prediction and CSV download
- Model comparison chart