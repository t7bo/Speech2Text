import os
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk
from pymongo import MongoClient
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from transformers import pipeline
import openai

load_dotenv()

speech_key = os.getenv("AZURE_SUBSCRIPTION_KEY")
region = os.getenv("AZURE_REGION")
mongodb_uri = os.getenv("MONGODB_URI")
mongodb_db_name = os.getenv("MONGODB_DB_NAME")
mongodb_collection_name = os.getenv("MONGODB_COLLECTION_NAME")
azure_text_analytics_key = os.getenv("AZURE_TEXT_ANALYTICS_KEY")
azure_text_analytics_endpoint = os.getenv("AZURE_TEXT_ANALYTICS_ENDPOINT")
api_key = os.getenv("OPENAI_API_KEY")
api_base = os.getenv("OPENAI_API_BASE")
api_deployment = os.getenv('OPENAPI_DEPLOYMENT')
api_version = os.getenv('OPENAPI_VERSION')

# First model: Speech2Text (Azure)
# class SpeechToTextModel:
#     def __init__(self):

#         # Load environment variables
#         load_dotenv()
#         self.speech_key = os.getenv("api_key")
#         self.service_region = os.getenv("region")
#         self.mongodb_uri = os.getenv("mongodb_uri")

#         if not all([self.speech_key, self.service_region, self.mongodb_uri]):
#             raise ValueError("One or more environment variables are missing")

#         # MongoDB setup
#         self.cluster = MongoClient(self.mongodb_uri)
#         self.db = self.cluster["AzureSpeechToText"]
#         self.collection = self.db["transcriptions"]

#     # Transcribe Speech to Text (French)
#     def transcribe(self, audio_file_path, output_file):
#         if not os.path.isfile(audio_file_path):
#             raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

#         speech_config = speechsdk.SpeechConfig(subscription=self.speech_key, region=self.service_region)
#         speech_config.speech_recognition_language = "fr-FR"
        
#         audio_config = speechsdk.audio.AudioConfig(filename=audio_file_path)
#         recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

#         print("Reconnaissance vocale en cours à partir du fichier audio...")

#         all_results = []

#         done = threading.Event()

#         def recognized(evt):
#             all_results.append(evt.result.text)
#             print(f"Texte reconnu: {evt.result.text}")

#         def stop_cb(evt):
#             print('CLOSING on {}'.format(evt))
#             done.set()

#         recognizer.recognized.connect(recognized)
#         recognizer.session_stopped.connect(stop_cb)
#         recognizer.canceled.connect(stop_cb)

#         recognizer.start_continuous_recognition()
#         done.wait()

#         recognizer.stop_continuous_recognition()
        
#         # Writing & Saving of the transcription
#         with open(output_file, "w", encoding='utf-8') as file:
#             file.write(" ".join(all_results))
#         return " ".join(all_results)

# class TranslationModel:
#     def __init__(self):
#         self.translation_pipeline = pipeline("translation", model="Helsinki-NLP/opus-mt-fr-en")

#     def translate(self, text):
#         result = self.translation_pipeline(text)
#         return result[0]['translation_text']

class SentimentAnalysisModel:
    def __init__(self):
        self.sentiment_pipeline = pipeline("text-classification", model="mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis")

    def analyze_sentiment(self, text):
        result = self.sentiment_pipeline(text)
        return result[0]

class GenerateResponseModel:
    def __init__(self) -> None:
        pass

    def generate_response(self, sentiment, text):
        prompt = f"Le client est insatisfait. Voici le texte: '{text}'. Pourquoi le client est-il insatisfait?"
        response = openai.ChatCompletion.create(
            engine=api_deployment,
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100  # Limiter le nombre de tokens à 100
        )
        llm_response = response['choices'][0]['message']['content'].strip()
        print("Réponse du modèle OpenAI : {}".format(llm_response))
        return llm_response