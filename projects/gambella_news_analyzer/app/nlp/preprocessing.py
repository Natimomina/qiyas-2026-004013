import re

def normalize_text(text):
    text = text or ''
    text = re.sub(r'\s+', ' ', text).strip()
    return text
