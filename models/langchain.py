from pydantic import Field
from langchain.chains.base import Chain
from datetime import datetime
import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv
from .mic2text import Speech2TextModel
import os
import azure.cognitiveservices.speech as speechsdk
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from .models import SentimentAnalysisModel, GenerateResponseModel
import openai

# Chargement des variables d'environnement
load_dotenv()
speech_key = os.getenv("speech_key")
region = os.getenv("region")
mongodb_uri = os.getenv("MONGODB_URI")
mongodb_db_name = os.getenv("MONGODB_DB_NAME")
mongodb_collection_name = os.getenv("MONGODB_COLLECTION_NAME")
azure_text_analytics_key = os.getenv("AZURE_TEXT_ANALYTICS_KEY")
azure_text_analytics_endpoint = os.getenv("AZURE_TEXT_ANALYTICS_ENDPOINT")
api_key = os.getenv("OPENAI_API_KEY")
api_base = os.getenv("OPENAI_API_BASE")
api_deployment = os.getenv('OPENAPI_DEPLOYMENT')
api_version = os.getenv('OPENAPI_VERSION')

# MongoDB set-up
cluster = MongoClient(mongodb_uri)
db = cluster[mongodb_db_name]
collection = db[mongodb_collection_name]

# Config Azure Text Analytics Client
text_analytics_client = TextAnalyticsClient(
    endpoint=azure_text_analytics_endpoint,
    credential=AzureKeyCredential(azure_text_analytics_key)
)

# Configurer l'API OpenAI avec les informations d'Azure
openai.api_key = api_key
openai.api_base = api_base
openai.api_type = 'azure'
openai.api_version = api_version

class GenerateResponseChain(Chain):
    stt_model: Speech2TextModel = Field(...)
    # translation_model: TranslationModel = Field(...)
    sentiment_model: SentimentAnalysisModel = Field(...)
    generate_response_model: GenerateResponseModel = Field(...)
    collection: pymongo.collection.Collection = Field(...)

    def __init__(self, stt_model, sentiment_model, generate_response_model, collection, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stt_model = stt_model
        # self.translation_model = translation_model
        self.sentiment_model = sentiment_model
        self.generate_response_model = generate_response_model
        self.collection = collection

    def _call(self, inputs):
        # audio_file_path = inputs['audio_file_path']
        stop_phrase = inputs['stop_phrase']
        output_file = inputs.get('output_file', 'transcriptions/audio_wav_transcript_translate.txt')
        
        # Étape 1 : Transcription
        transcription = self.stt_model.speak_to_microphone(stop_phrase, output_file)
        # Étape 2 : Traduction
        # translation = self.translation_model.translate(transcription)
        # Étape 3 : Analyse de Sentiment
        sentiment = self.sentiment_model.analyze_sentiment(transcription)['label']
        # Étape 4 : Génération de Réponse
        response = self.generate_response_model.generate_response(sentiment, transcription)
        # Étape 5 : Génération de date
        timestamp = datetime.now()
        
        # Sauvegarder la sortie de chaque étape dans MongoDB
        self.collection.insert_one({
            "transcription": transcription,
            # "translation": translation,
            "timestamp": timestamp,
            "sentiment": sentiment,
            "response": response
        })
        
        return {
            'transcription': transcription,
            # 'translation': translation,
            'timestamp': timestamp,
            'sentiment': sentiment,
            'response': response
        }

    def process(self, inputs):
        return self._call(inputs)

    @property
    def input_keys(self):
        return ['stop_phrase']
    
    @property
    def output_keys(self):
        return ['transcription', 'timestamp', 'sentiment', 'response']

# Génération des modèles
stt_model = Speech2TextModel()
# translation_model = TranslationModel()
sentiment_model = SentimentAnalysisModel()
generate_response_model = GenerateResponseModel()

# Création de la chaîne
chain = GenerateResponseChain(
    stt_model=stt_model,
    # translation_model=translation_model,
    sentiment_model=sentiment_model,
    generate_response_model=generate_response_model,
    collection=collection
)

# Fichier audio en entrée
stop_phrase = "stop session"

# Exécution de la chaîne
results = chain.process({'stop_phrase': stop_phrase})
print(results)