from keybert import KeyBERT
from transformers import pipeline

# from gensim.corpora.dictionary import Dictionary
# from gensim.models import LdaModel

# from nltk.corpus import stopwords
# from nltk.tokenize import word_tokenize

def get_keywords_keybert(chats):
    kw_model = KeyBERT(model="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    keywords = kw_model.extract_keywords(chats)
    return keywords

# def get_keywords_keybert(text, num_words=5):
#     model = KeyBERT()
#     keywords = model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=num_words)
#     return {word: score for word, score in keywords}

# def get_keywords_lda(text, num_topics=1, num_words=5):
#     stop_words = set(stopwords.words('english'))
#     words = [word for word in word_tokenize(text.lower()) if word.isalnum() and word not in stop_words]

#     # Create dictionary and corpus for LDA
#     dictionary = Dictionary([words])
#     corpus = [dictionary.doc2bow(words)]

#     # Train LDA model
#     lda = LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=15)

#     # Extract keywords and their weights
#     topics = lda.show_topics(num_topics=num_topics, num_words=num_words, formatted=False)
#     keywords = {word: weight for _, word_weight_list in topics for word, weight in word_weight_list}
#     return keywords

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
