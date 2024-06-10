import os
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk
from pymongo import MongoClient
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from transformers import pipeline
import openai

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

class SentimentAnalysisModel:
    def __init__(self):
        self.sentiment_pipeline = pipeline("text-classification", model="mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis")

    def analyze_sentiment(self, text):
        result = self.sentiment_pipeline(text)
        print(f"Sentiment Analysis: {result}")
        return result[0]

class GenerateResponseModel:
    def __init__(self) -> None:
        pass

    def generate_response(self, sentiment, text):
        prompt = f"Voici la transcription d'un message vocal laissé par un client auprès de sa banque. Analyse la transcription suivante et résume en quelques mots pourquoi le client est-il insatisfait. Transcription: {text}"
        # Appel à l'API OpenAI pour générer une réponse basée sur le modèle GPT-3.5-turbo.
        # Le modèle est configuré avec un ensemble de messages, dont un message système pour configurer le contexte et un message utilisateur contenant l'invite créée ci-dessus.
        response = openai.ChatCompletion.create(
            engine=api_deployment,  # Spécifie l'instance du modèle déployée à utiliser
            model="gpt-3.5-turbo",  
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},  # Message système pour définir le rôle de l'assistant
                {"role": "user", "content": prompt}  # Message utilisateur contenant l'invite
            ],
            max_tokens=100  # Limite le nombre de tokens dans la réponse générée à 100
        )
        # Extraction de la réponse générée via l'appel à l'API.
        llm_response = response['choices'][0]['message']['content'].strip()
        print("Réponse du modèle OpenAI : {}".format(llm_response))
        return llm_response