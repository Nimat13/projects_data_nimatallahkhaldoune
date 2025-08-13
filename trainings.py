import os
import json
import pickle
import chromadb
from chromadb.utils import embedding_functions
import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import matplotlib.pyplot as plt
from nltk.stem import WordNetLemmatizer
import nltk

# Télécharger les ressources nécessaires pour nltk
nltk.download('punkt')
nltk.download('wordnet')

# Initialisation
lemmatizer = WordNetLemmatizer()

# Fonction de prétraitement des phrases
def preprocess(sentence):
    tokens = nltk.word_tokenize(sentence.lower())  # Tokenisation
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word.isalnum()]  # Lemmatisation et nettoyage
    return " ".join(tokens)

# Chargement ou entraînement du modèle
def load_or_train_model():
    if os.path.exists("model.pkl") and os.path.exists("vectorizer.pkl") and os.path.exists("label_encoder.pkl"):
        print("🔄 Chargement des modèles existants...")
        with open("model.pkl", "rb") as model_file:
            model = pickle.load(model_file)
        with open("vectorizer.pkl", "rb") as vectorizer_file:
            vectorizer = pickle.load(vectorizer_file)
        with open("label_encoder.pkl", "rb") as encoder_file:
            label_encoder = pickle.load(encoder_file)
        return model, vectorizer, label_encoder
    else:
        print("⚙️ Aucun modèle trouvé. Entraînement en cours...")
        return train_model()

# Entraînement du modèle
def train_model():
    with open("intents.json", "r", encoding="utf-8") as file:
        intents = json.load(file)
    
    sentences = []
    labels = []
    all_questions = []
    question_types = []

    for intent in intents["intents"]:
        for pattern in intent["patterns"]:
            sentences.append(preprocess(pattern))
            labels.append(intent["tag"])
            all_questions.append(preprocess(pattern))
            question_types.append(intent["complexe"])

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(sentences)

    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(labels)

    model = SVC(kernel="linear", probability=True)
    model.fit(X, y)

    with open("model.pkl", "wb") as model_file:
        pickle.dump(model, model_file)
    with open("vectorizer.pkl", "wb") as vectorizer_file:
        pickle.dump(vectorizer, vectorizer_file)
    with open("label_encoder.pkl", "wb") as encoder_file:
        pickle.dump(label_encoder, encoder_file)

    print("✅ Modèles sauvegardés : model.pkl, vectorizer.pkl, label_encoder.pkl")
    index_questions_with_embeddings(all_questions, question_types, vectorizer)
    evaluate_model(model, X, y, label_encoder)
    return model, vectorizer, label_encoder

def index_questions_with_embeddings(questions, question_types, vectorizer):
    print("🔍 Indexation des questions dans ChromaDB...")
    client = chromadb.Client()
    collection = client.get_or_create_collection(name="questions_attijari_wafa")

    tfidf_embeddings = vectorizer.transform(questions).toarray()

    for idx, (question, embedding, is_complex) in enumerate(zip(questions, tfidf_embeddings, question_types)):
        collection.add(
            ids=[f"question_{idx}"],
            documents=[question],
            embeddings=[embedding.tolist()],
            metadatas=[{"complexe": is_complex}]
        )
    print("✅ Questions indexées dans ChromaDB avec embeddings TF-IDF.")

def extract_text_from_pdf(pdf_path):
    print(f"📄 Extraction du texte depuis : {pdf_path}")
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    print("✅ Extraction terminée.")
    return text

def process_pdf_and_index(pdf_path, vectorizer):
    pdf_text = extract_text_from_pdf(pdf_path)
    chunks = [pdf_text[i:i+500] for i in range(0, len(pdf_text), 500)]
    print("🔹 Exemple de chunks extraits pour ChromaDB :", chunks[:2])
    processed_chunks = [preprocess(chunk) for chunk in chunks]
    index_questions_with_embeddings(processed_chunks, ["complexe"] * len(processed_chunks), vectorizer)

# Évaluation du modèle
def evaluate_model(model, X, y, label_encoder):
    print("📊 Évaluation du modèle...")
    y_pred = model.predict(X)
    y_true = y

    print("\nConfusion Matrix:")
    print(confusion_matrix(y_true, y_pred))

    print("\nClassification Report:")
    print(classification_report(y_true, y_pred, target_names=label_encoder.classes_))

    accuracy = accuracy_score(y_true, y_pred)
    print(f"\nAccuracy: {accuracy * 100:.2f}%")

    # Visualisation des performances
    plt.figure(figsize=(12, 5))

    # Matrice de confusion
    cm = confusion_matrix(y_true, y_pred)
    plt.matshow(cm, cmap='coolwarm', fignum=1)
    plt.colorbar()
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.show()

if __name__ == "__main__":
    model, vectorizer, label_encoder = load_or_train_model()
    process_pdf_and_index("info.pdf", vectorizer)
    print("✅ Le modèle est prêt pour l'utilisation ou les tests.")
