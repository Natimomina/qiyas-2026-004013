import re
from typing import List, Dict

try:
    import spacy
except ImportError:
    spacy = None

_nlp = None


def get_nlp():
    global _nlp
    if _nlp is not None:
        return _nlp
    if spacy is None:
        return None
    for model_name in ('en_core_web_sm',):
        try:
            _nlp = spacy.load(model_name)
            return _nlp
        except Exception:
            continue
    return None


def _fallback(text: str) -> List[Dict]:
    # Conservative fallback when spaCy's model is not installed.
    results = []
    patterns = {
        'DATE': r'\b(?:\d{1,2}\s+)?(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b',
        'MONEY': r'(?:\$|€|£)\s?\d[\d,]*(?:\.\d+)?|\b\d[\d,]*(?:\.\d+)?\s*(?:birr|ETB|USD|dollars?)\b',
    }
    for label, pat in patterns.items():
        for m in re.finditer(pat, text, re.I):
            results.append({'text': m.group(0), 'label': label, 'start': m.start(), 'end': m.end()})
    return results


def extract_entities(text: str) -> List[Dict]:
    text = text or ''
    nlp = get_nlp()
    if nlp:
        doc = nlp(text)
        allowed = {'PERSON','ORG','GPE','LOC','DATE','MONEY','EVENT','NORP','FAC'}
        mapped = {'GPE':'LOCATION','LOC':'LOCATION','FAC':'LOCATION'}
        return [
            {'text': e.text.strip(), 'label': mapped.get(e.label_, e.label_), 'start': e.start_char, 'end': e.end_char}
            for e in doc.ents if e.label_ in allowed and e.text.strip()
        ]
    return _fallback(text)
