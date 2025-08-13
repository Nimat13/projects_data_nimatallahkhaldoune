import streamlit as st
import chromadb
from chatbot import load_models, respond_to_user_input

# Charger les modèles et la collection ChromaDB
model, vectorizer, label_encoder, collection = load_models()

# Se connecter à ChromaDB
client = chromadb.Client()
collection = client.get_or_create_collection(name="questions_attijari_wafa")

# Configuration de l'application Streamlit
st.set_page_config(page_title="Chatbot", page_icon="🤖", layout="centered")
st.image('Logo_AWB.png', width=200)
st.title("🤖 Attijariwafa Bot")

# Initialisation de la session_state.messages si elle n'existe pas
if "messages" not in st.session_state:
    st.session_state.messages = []

def is_complex_response(response):
    """
    Détermine si une réponse est déjà bien formatée.
    Critères :
    - Contient plusieurs sauts de ligne (\n).
    - Contient des puces (- ou *) ou des numéros (1., 2., etc.).
    """
    if "\n" in response and ("-" in response or "*" in response or "1." in response):
        return True
    return False

def format_response(response):
    """
    Formate les réponses simples pour les rendre lisibles.
    Ne modifie pas les réponses déjà bien formatées.
    """
    # Si la réponse est complexe, la retourner telle quelle
    if is_complex_response(response):
        return response

    # Sinon, appliquer un formatage simple
    response = response.replace("\n", " ").strip()
    response = response.replace(". ", ".\n\n")
    return response


# Champ de texte pour l'entrée de l'utilisateur
user_input = st.text_input("Posez une question:")

# Si l'utilisateur envoie une requête
if user_input:
    # Ajouter le message de l'utilisateur à la session et l'afficher immédiatement
    st.session_state.messages.append({"role": "user", "message": user_input})
    st.chat_message("user").markdown(f"**Vous**: {user_input}")

    # Générer la réponse du bot
    raw_response = respond_to_user_input(user_input, collection, model, vectorizer, label_encoder)
    
    # Formater la réponse
    response = format_response(raw_response)
    
    # Ajouter la réponse du bot à la session et l'afficher immédiatement
    st.session_state.messages.append({"role": "bot", "message": response})
    st.chat_message("bot").markdown(response)

# Afficher l'historique complet pour les visiteurs qui chargent la page après une interaction
for msg in st.session_state.messages[:-2]:  # Exclure les deux derniers qui sont déjà affichés
    if msg["role"] == "user":
        st.chat_message("user").markdown(f"**Vous**: {msg['message']}")
    else:
        st.chat_message("bot").markdown(msg["message"])
