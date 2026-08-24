import re

POSITIVE = {'good','great','success','successful','improve','improved','peace','positive','win','won','growth','benefit','beneficial','agreement','support','restore','restored','hope'}
NEGATIVE = {'bad','crisis','conflict','attack','killed','death','dead','arrested','war','violence','negative','injured','dispute','collapse','decline','threat'}

def analyze_sentiment(text):
    words = re.findall(r"[A-Za-z']+", (text or '').lower())
    if not words: return 'Neutral', 0.0
    pos = sum(w in POSITIVE for w in words)
    neg = sum(w in NEGATIVE for w in words)
    score = (pos-neg) / max(pos+neg, 1)
    if score > 0.2: label='Positive'
    elif score < -0.2: label='Negative'
    else: label='Neutral'
    return label, round(float(score), 4)
