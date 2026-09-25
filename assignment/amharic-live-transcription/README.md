# Amharic Live Transcription

A speech-to-text (ASR) system for Amharic, built as a machine learning experiment on a subset
of the [Amharic Speech Corpus](https://www.kaggle.com/datasets/ashenafifasilkebede/amharic-speech-corpus).
Includes a live-microphone transcription demo built with [Gradio](https://gradio.app).

## What it does

- Loads and cleans the first 3,000 labeled audio clips from the corpus
- Trains and compares two models:
  1. A CNN + BiGRU acoustic model trained from scratch with CTC loss
  2. A fine-tuned `facebook/wav2vec2-large-xlsr-53` (transfer learning)
- Automatically selects whichever model scores a lower Word Error Rate (WER) on a held-out
  validation split
- Serves the winning model through a Gradio app: live microphone transcription, file upload,
  and a tab to check predictions against real held-out examples

## Setup

1. **Clone this repo** and open `Amharic_Live_Transcription.ipynb` in Jupyter.
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Download the dataset** from [Kaggle](https://www.kaggle.com/datasets/ashenafifasilkebede/amharic-speech-corpus),
   extract it, and point `DATA_ROOT` (in the notebook's Configuration cell) at it.
4. **(Optional) Download the base model manually** if the automatic Hugging Face download is
   slow or unreliable on your connection. Grab `config.json`, `preprocessor_config.json`, and
   `pytorch_model.bin` from
   [facebook/wav2vec2-large-xlsr-53](https://huggingface.co/facebook/wav2vec2-large-xlsr-53/tree/main),
   put them in one local folder, and point `W2V_BASE_MODEL` at that folder instead.

## Running it

Run the notebook cells in order, top to bottom. Set `QUICK_TEST = True` in the Configuration
cell for a fast end-to-end smoke test (~150 samples, 1 epoch) before committing to the full run.

## Results

_Fill in after your final run:_
- Baseline (CNN+BiGRU+CTC) — WER: `__`, CER: `__`
- Fine-tuned Wav2Vec2-XLSR-53 — WER: `__`, CER: `__`
- Automatically selected model: `__`

## Acknowledgments

- Dataset: [Amharic Speech Corpus](https://www.kaggle.com/datasets/ashenafifasilkebede/amharic-speech-corpus) (ALFFA / OpenSLR-25)
- Base model: [facebook/wav2vec2-large-xlsr-53](https://huggingface.co/facebook/wav2vec2-large-xlsr-53)
