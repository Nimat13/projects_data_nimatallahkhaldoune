import os
import json
import pickle
import chromadb
import google.generativeai as genai
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Télécharger les ressources nécessaires pour nltk
import nltk
nltk.download('punkt')
nltk.download('wordnet')

# Initialisation des ressources
lemmatizer = WordNetLemmatizer()

# Charger les modèles et le vectorizer
def load_models():
    with open("model.pkl", "rb") as model_file:
        model = pickle.load(model_file)
    with open("vectorizer.pkl", "rb") as vectorizer_file:
        vectorizer = pickle.load(vectorizer_file)
    with open("label_encoder.pkl", "rb") as encoder_file:
        label_encoder = pickle.load(encoder_file)

    # Initialisation de ChromaDB pour la recherche de questions complexes
    client = chromadb.Client()
    collection = client.get_or_create_collection(name="questions_attijari_wafa")
    
    return model, vectorizer, label_encoder, collection

# Prétraitement de la phrase
def preprocess(sentence):
    tokens = word_tokenize(sentence.lower())  # Tokenisation
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word.isalnum()]  # Lemmatisation
    return " ".join(tokens)

# Fonction pour obtenir une réponse depuis ChromaDB
def get_direct_response_from_chromadb(question, collection, vectorizer):
    # Prétraiter la question
    preprocessed_question = preprocess(question)
    
    # Vectoriser la question (transformer en embedding avec le même vectorizer utilisé lors de l'indexation)
    question_embedding = vectorizer.transform([preprocessed_question]).toarray()

    # Rechercher dans ChromaDB avec l'embedding
    search_results = collection.query(query_embeddings=question_embedding.tolist(), n_results=1)
    
    # Si des résultats sont trouvés, retourner le document associé comme réponse
    if search_results["documents"]:
        document = search_results["documents"][0]
        return f"Réponse trouvée dans la base de données : {document}"  # Fournir plus de détails sur la source de la réponse
    
    return "Désolé, je n'ai pas trouvé de réponse directe à votre question dans la base de données ChromaDB."  # Si aucun résultat n'est trouvé


# Fonction pour détecter si la question est complexe en la recherchant dans ChromaDB
def is_complex_question(question, collection, vectorizer):
    # Prétraiter la question
    preprocessed_question = preprocess(question)
    
    # Vectoriser la question (transformer en embedding avec le même vectorizer utilisé lors de l'indexation)
    question_embedding = vectorizer.transform([preprocessed_question]).toarray()

    # Rechercher dans ChromaDB avec l'embedding
    search_results = collection.query(query_embeddings=question_embedding.tolist(), n_results=1)
    
    # Si la recherche retourne des résultats, c'est une question complexe
    if search_results["documents"]:
        return True
    return False

# Utiliser Gemini pour générer une réponse pour une question complexe
def generate_response_with_gemini(question):
    # Récupération de la clé API à partir de l'environnement
    GOOGLE_API_KEY = "YOUR_API_KEY"
    
    if not GOOGLE_API_KEY:
        raise ValueError("La clé API Google n'est pas définie dans le fichier .env")

    try:
        # Configuration de l'API Gemini avec la clé API chargée
        genai.configure(api_key=GOOGLE_API_KEY)

        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }

        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config=generation_config,
           system_instruction= """
            Vous êtes AWBBot un assistant IA expert en services bancaires et d'assurances. Votre mission est de fournir des réponses claires, précises et professionnelles aux utilisateurs en utilisant deux principales sources :

            1. intents.json : Ce fichier contient les questions fréquentes et leurs réponses prédéfinies pour les requêtes simples.
            2. info.pdf : Ce document est utilisé pour enrichir les réponses complexes nécessitant des détails supplémentaires.

            ### Instructions de fonctionnement :
            1. **Correspondance des intentions :**
            - Si une question correspond à un "pattern" présent dans intents.json, utilisez directement la réponse prédéfinie.

            2. **Requêtes complexes :**
            - Si aucune réponse directe n'est trouvée, consultez le contenu du document info.pdf.
            - Formulez une réponse structurée en incluant :
                - Une introduction claire.
                - Des informations détaillées avec des exemples chiffrés lorsque possible.
                - Une référence utile (contact/service client) si applicable.

            3. **Ambiguïté :**
            - Si la question est inconnue ou hors sujet ou manque de précision, demandez à l'utilisateur de clarifier sa demande.

            4. **Ton et style :**
            - Soyez professionnel, concis et utilisez un langage adapté aux services bancaires et d'assurances.

            ### Format attendu des réponses :
            - **Questions simples :** Réponse directe depuis intents.json.
            - **Questions complexes :** Réponse enrichie avec des détails extraits de info.pdf.
            """
        )

        chat_session = model.start_chat(history=[])
        response = chat_session.send_message(question)
        return response.text

    except Exception as e:
        print(f"Erreur lors de la génération de la réponse avec Gemini : {e}")
        return "Désolé, une erreur est survenue lors de la génération de la réponse."


# Répondre à la question de l'utilisateur en recherchant directement dans ChromaDB
def respond_to_user_input(user_input, collection, model, vectorizer, label_encoder):
    # Prétraiter l'entrée de l'utilisateur
    preprocessed_input = preprocess(user_input)

    # Vérifier si la question correspond à un "pattern" dans intents.json (réponse simple)
    with open("intents.json", "r", encoding="utf-8") as file:
        intents = json.load(file)
            
    for intent in intents["intents"]:
        for pattern in intent["patterns"]:
            if preprocessed_input == preprocess(pattern):  
                # Vérifier si la question est complexe
                if intent.get("complexe", False):
                    print("🧠 Question complexe détectée, réponse générée par Gemini...")
                    return generate_response_with_gemini(user_input)
                else:
                    return intent["responses"][0]

    # Si la question n'est pas simple, vérifier si c'est une question complexe
    if is_complex_question(preprocessed_input, collection, vectorizer):
        print("🧠 Question complexe détectée, recherche directe dans ChromaDB...")
        return get_direct_response_from_chromadb(user_input, collection, vectorizer)
    
    # Si la question n'est ni simple ni complexe, essayer de prédire avec le modèle
    print("📝 Question simple, réponse basée sur l'intention...")
    # Transformer l'entrée utilisateur et prédire l'intention
    X_input = vectorizer.transform([preprocessed_input])
    prediction = model.predict(X_input)
    intent = label_encoder.inverse_transform(prediction)[0]
    return intent  # Renvoie l'intention comme réponse


if __name__ == "__main__":
    # Charger les modèles et ChromaDB
    model, vectorizer, label_encoder, collection = load_models()
    
    # Tester avec une entrée utilisateur
    user_input = "Comment puis-je réduire mes frais bancaires en utilisant vos services ?"
    response = respond_to_user_input(user_input, collection, model, vectorizer, label_encoder)
    print(f"Réponse de l'assistant : {response}")
