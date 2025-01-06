from keybert import KeyBERT
from transformers import pipeline

def get_keywords_keybert(chats):
    kw_model = KeyBERT(model="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    keywords = kw_model.extract_keywords(chats)
    return keywords

def get_sentiment_data(chats):
    #Patrick_ToCheck this model do not work...
    #sentiment_analyzer = pipeline("sentiment-analysis", model="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    sentiment_analyzer = pipeline("sentiment-analysis", model="cardiffnlp/twitter-xlm-roberta-base-sentiment-multilingual")

    messages = chats.split(">") #TODO use real way to split out different messages
    #TODO: make sure no single message is too long for classification, can break it up if length too long
    sentiments = sentiment_analyzer(messages)
    category_scores = {"positive": 0, "neutral": 0, "negative": 0}
    category_counts = {"positive": 0, "neutral": 0, "negative": 0}
    for result in sentiments:
        label = result['label'].lower()
        category_scores[label] += result['score']
        category_counts[label] += 1
    # Normalize scores by dividing by the total number of messages
    total_messages = len(messages)
    normalized_scores = {key: (category_scores[key] / total_messages) for key in category_scores}
    return normalized_scores
