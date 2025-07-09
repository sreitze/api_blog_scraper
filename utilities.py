import unicodedata

def normalize_text(text):
    normalized_text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    return normalized_text.lower().replace(" ", "-")