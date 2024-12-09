import nltk
from keybert import KeyBERT
from transformers import pipeline

from gensim.corpora.dictionary import Dictionary
from gensim.models import LdaModel

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download('stopwords')
nltk.download('punkt_tab')
model = KeyBERT()
kw_model = KeyBERT(model="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
sentiment_analyzer = pipeline("sentiment-analysis", model="cardiffnlp/twitter-xlm-roberta-base-sentiment-multilingual")
