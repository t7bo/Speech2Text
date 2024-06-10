import os
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk
import pyaudio
import wave
import threading
import uuid
import subprocess

load_dotenv()
speech_key = os.getenv("speech_key")
region = os.getenv("region")

class Speech2TextModel:
    def __init__(self, speech_key, region):
        self.speech_key = speech_key
        self.region = region
        self.recording = False

    @staticmethod
    def generate_unique_filename():
        unique_id = uuid.uuid4()
        return str(unique_id)

    def record_audio(self, output_file):
        chunk = 1024
        sample_format = pyaudio.paInt16
        channels = 1
        fs = 44100  # samples per second
        p = pyaudio.PyAudio()  # creates an interface to PortAudio
        
        # Vérification des périphériques audio disponibles
        info = p.get_host_api_info_by_index(0)
        num_devices = info.get('deviceCount')
        print(f"Nombre de périphériques audio : {num_devices}")

        mic_available = False
        for i in range(0, num_devices):
            device_info = p.get_device_info_by_host_api_device_index(0, i)
            if device_info.get('maxInputChannels') > 0:
                print(f"Input Device id {i} - {device_info.get('name')}")
                mic_available = True

        # Si aucun microphone n'est disponible, essayez de l'activer via PulseAudio
        if not mic_available:
            print("Aucun microphone disponible. Tentative d'activation via PulseAudio...")
            try:
                subprocess.run(["pactl", "load-module", "module-loopback"], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Erreur lors de l'activation du micro: {e}")
                return  # Arrêtez l'enregistrement si le micro ne peut pas être activé
        
        stream = p.open(format=sample_format,
                        channels=channels,
                        rate=fs,
                        frames_per_buffer=chunk,
                        input=True)
        frames = []  # initialize array to store frames
        print("Recording audio...")
        while self.recording:
            data = stream.read(chunk)
            frames.append(data)
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("Saving audio...")
        wf = wave.open(output_file, "wb")
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(sample_format))
        wf.setframerate(fs)
        wf.writeframes(b''.join(frames))
        wf.close()

    def speak_to_microphone(self, stop_phrase, output_file):
        speech_config = speechsdk.SpeechConfig(subscription=self.speech_key, region=self.region)
        speech_config.speech_recognition_language = "fr-FR"
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

        print('Speak into your microphone. Say "stop session" to end the recording session.')

        self.recording = True

        # Generate unique filenames and save them in the corresponding folders
        base_filename = self.generate_unique_filename()
        audios_folder = "audios/"
        transcripts_folder = "transcripts/"
        # Ensure the directories exist
        os.makedirs(audios_folder, exist_ok=True)
        os.makedirs(transcripts_folder, exist_ok=True)
        audio_output_file = os.path.join(audios_folder, f"{base_filename}.wav")
        text_output_file = os.path.join(transcripts_folder, f"{base_filename}.txt")

        # Start audio recording in a separate thread
        audio_thread = threading.Thread(target=self.record_audio, args=(audio_output_file,))
        audio_thread.start()

        '''Speech to Text: Transcript'''
        with open(text_output_file, "w", encoding="utf-8") as file:
            while True:
                # Wait for any audio signal
                speech = speech_recognizer.recognize_once_async().get()

                if speech.reason == speechsdk.ResultReason.RecognizedSpeech:
                    # Generate unique filename for text_transcription
                    print('Recognized: {}'.format(speech.text))
                    file.write(speech.text + "\n")
                    if stop_phrase.lower() in speech.text.lower():
                        print("Session ended by user.")
                        self.recording = False  # stop recording
                        audio_thread.join()  # wait for the audio thread to finish
                        break

                # Check if the mic-speech is recognized, if not, print an error message (including logs/details).
                elif speech.reason == speechsdk.ResultReason.NoMatch:
                    print("No speech could be recognized: {}".format(speech.no_match_details))

                # Print an error message with details if transcript gets canceled for any reason
                elif speech.reason == speechsdk.ResultReason.Canceled:
                    cancellation_details = speech.cancellation_details
                    print("Speech Recognition canceled: {}".format(cancellation_details.reason))
                    if cancellation_details.reason == speechsdk.CancellationReason.Error:
                        print('Error details: {}'.format(cancellation_details.error_details))
                        print('Did you set the speech resource key and region values?')

        # Return the transcription content
        with open(text_output_file, "r", encoding="utf-8") as file:
            transcription = file.read()
        return transcription