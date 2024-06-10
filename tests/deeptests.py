""" 
Test de Chargement des Variables d'Environnement
    Vérifiez que toutes les variables d'environnement sont correctement chargées et accessibles.
    
Test de Disponibilité du Microphone
    Vérifiez que le microphone est disponible et peut être activé si nécessaire.
    
Test des Permissions du Microphone
    Vérifiez que l'application gère correctement les erreurs lorsque les permissions d'accès au microphone ne sont pas accordées.
    
Test de Détection d'Erreur d'Activation du Microphone
    Vérifiez que le code détecte et gère correctement les erreurs lorsque le microphone ne peut pas être activé.
    
Test de Manipulation des Fichiers
    Vérifiez que les fichiers audio et texte sont créés dans les répertoires corrects et que les noms de fichiers sont uniques.

Test de l'Enregistrement Audio
    Vérifiez que l'enregistrement audio est sauvegardé correctement dans le fichier spécifié.


    
Test de la Fonction de Transcription
    Enregistrez un court message vocal et vérifiez que la transcription correspond au message enregistré.

Test de la Durée de l'Enregistrement
    Enregistrez un message de différentes durées et assurez-vous que la transcription est correcte pour chaque durée.
    
Test de la Phrase d'Arrêt
    Vérifiez que la transcription s'arrête correctement lorsque la phrase d'arrêt ("stop session") est prononcée.
    
Test de l'Analyse de Sentiment
    Vérifiez que l'analyse de sentiment fonctionne correctement avec des textes ayant des sentiments différents (positif, négatif, neutre).
    
Test de la Génération de Réponses
    Vérifiez que les réponses générées par le modèle GPT-3.5-turbo sont pertinentes par rapport à l'analyse de sentiment et au texte fourni.
    
Test des Erreurs de Reconnaissance Vocale
    Simulez des conditions où le texte n'est pas reconnu et vérifiez la gestion des erreurs.

Test de la Sauvegarde MongoDB
    Vérifiez que les données (transcription, sentiment, réponse, timestamp) sont correctement sauvegardées dans la base de données MongoDB.

Test des Limites de Tokens
    Vérifiez que la réponse générée ne dépasse pas la limite de 100 tokens.
    
    
    
Test d'Intégration Complète
    Effectuez un test de bout en bout en enregistrant un message vocal, en le transcrivant, en analysant le sentiment, en générant une réponse et en sauvegardant les données dans MongoDB.
    Assurez-vous que toutes les étapes fonctionnent ensemble de manière fluide.

Test de Compatibilité Multi-plateforme
    Testez le code sur différents systèmes d'exploitation (Windows, macOS, Linux) pour vous assurer qu'il fonctionne correctement partout.
"""