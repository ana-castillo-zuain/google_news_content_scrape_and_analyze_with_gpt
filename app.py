# import streamlit as st
# import requests
# from bs4 import BeautifulSoup
# from mailjet_rest import Client
# from fake_useragent import UserAgent
# import os
# import json

# # -----------------------------
# # Configure Mailjet
# # -----------------------------
# API_KEY = st.secrets["api_key"]
# API_SECRET = st.secrets["api_secret"]

# mailjet = Client(auth=(API_KEY, API_SECRET), version='v3.1')
# ua = UserAgent()

# # -----------------------------
# # Email list handling
# # -----------------------------
# EMAIL_FILE = "emails.json"


# def load_emails():
#     if not os.path.exists(EMAIL_FILE):
#         save_emails(["team@example.com"])  # default
#     with open(EMAIL_FILE, "r") as f:
#         data = json.load(f)
#         return data.get("emails", [])


# def save_emails(emails):
#     with open(EMAIL_FILE, "w") as f:
#         json.dump({"emails": emails}, f, indent=4)


# # -----------------------------
# # Scraper function
# # -----------------------------
# def scrape_gnews(query, lang="en", country="US", max_results=5, date_filter=None):
#     """
#     Scrape Google News article titles and links based on query, language,
#     country, and optional date filter.
#     """
#     if date_filter:
#         query = f"{query} when:{date_filter}"

#     url = f"https://news.google.com/search?q={query}&hl={lang}&gl={country}&ceid={country}:{lang}"
#     r = requests.get(url, headers={'User-Agent': ua.chrome}, timeout=10)
#     soup = BeautifulSoup(r.text, "html.parser")

#     articles = []
#     raw_links = soup.select("a.DY5T1d")[:max_results]

#     for a in raw_links:
#         link = a["href"]
#         if link.startswith("./"):
#             link = "https://news.google.com" + link[1:]
#         title = a.get_text(strip=True)
#         articles.append({"title": title, "url": link})

#     return articles


# # -----------------------------
# # Email sender
# # -----------------------------
# def send_email(subject, body, recipients):
#     """Send email using Mailjet API."""
#     data = {
#         'Messages': [
#             {
#                 "From": {"Email": "cuenta.de.repuesto2021@gmail.com", "Name": "News Bot"},
#                 "To": [{"Email": r.strip(), "Name": r.strip()} for r in recipients],
#                 "Subject": subject,
#                 "TextPart": body,
#             }
#         ]
#     }
#     result = mailjet.send.create(data=data)
#     return result.status_code


# # -----------------------------
# # Streamlit UI
# # -----------------------------
# st.set_page_config(page_title="Buscador y scraper de noticias", page_icon="📰")
# st.title("📰 Buscador y scraper de noticias")

# query = st.text_input(
#     "Ingrese palabra clave (en minuscula y separado por comas si hay más de una)",
#     "Formula 1"
# )
# lang = st.text_input("Lenguaje (e.g., en, es, fr)", "es")
# country = st.text_input("País (e.g., US, AR, FR)", "US")
# date_filter = st.selectbox(
#     "Filtrar por fecha",
#     options=["", "1d", "7d", "1m"],
#     format_func=lambda x: {
#         "": "Sin filtro",
#         "1d": "Últimas 24 horas",
#         "7d": "Última semana",
#         "1m": "Último mes"
#     }[x]
# )
# num_articles = st.slider("Número de artículos", 1, 50, 5)

# # -----------------------------
# # Email management
# # -----------------------------
# emails = load_emails()
# st.subheader("📧 Lista de emails")

# email_input = st.text_input("Agregar nuevo email")
# if st.button("➕ Agregar"):
#     if email_input and email_input not in emails:
#         emails.append(email_input)
#         save_emails(emails)
#         st.success(f"{email_input} agregado!")

# remove_input = st.selectbox("Eliminar email", [""] + list(emails))
# if st.button("➖ Eliminar") and remove_input:
#     emails.remove(remove_input)
#     save_emails(emails)
#     st.warning(f"{remove_input} eliminado!")

# st.write("**Emails actuales:**", ", ".join(emails))

# # -----------------------------
# # Run scraper + send
# # -----------------------------
# if st.button("Buscar y enviar"):
#     st.write("🔍 Scrapeando noticias...")
#     articles = scrape_gnews(query, lang=lang, country=country,
#                             max_results=num_articles, date_filter=date_filter)

#     if articles:
#         st.success("✅ Artículos scrapeados exitosamente!")
#         for a in articles:
#             st.markdown(f"**{a['title']}**  \n[{a['url']}]({a['url']})")

#         body = "\n\n".join([
#             f"{a['title']}\n{a['url']}"
#             for a in articles
#         ])

#         st.write("📧 Enviando emails...")
#         status = send_email(f"Resultados de noticias acerca de '{query}'", body, emails)

#         if status == 200:
#             st.success("✅ Email enviado!")
#         else:
#             st.error("❌ No se pudo enviar el email.")
#     else:
#         st.warning("No se encontraron artículos.")

import streamlit as st
import requests 
from bs4 import BeautifulSoup 
from mailjet_rest import Client 
from fake_useragent import UserAgent 
import os 
import json 
import time
from transformers import pipeline

# -----------------------------
# Configure Mailjet 
# -----------------------------
API_KEY = st.secrets["api_key"] 
API_SECRET = st.secrets["api_secret"] 
mailjet = Client(auth=(API_KEY, API_SECRET), version='v3.1') 
ua = UserAgent() 

# -----------------------------
# Email list handling 
# -----------------------------
EMAIL_FILE = "emails.json" 

def load_emails():
    if not os.path.exists(EMAIL_FILE): 
        save_emails(["team@example.com"]) # default
    with open(EMAIL_FILE, "r") as f: 
        data = json.load(f)
        return data.get("emails", [])

def save_emails(emails): 
    with open(EMAIL_FILE, "w") as f: 
        json.dump({"emails": emails}, f, indent=4) 

# -----------------------------
# Scraper function 
# -----------------------------
def scrape_gnews(query, lang="en", country="US", max_results=5, date_filter=None):
    """ Scrape Google News article titles and links based on query, language, country, and optional date filter. """ 
    if date_filter:
        query = f"{query} when:{date_filter}" 
    url = f"https://news.google.com/search?q={query}&hl={lang}&gl={country}&ceid={country}:{lang}" 
    r = requests.get(url, headers={'User-Agent': ua.chrome}, timeout=10) 
    soup = BeautifulSoup(r.text, "html.parser")
    articles = [] 
    raw_links = soup.select("a.DY5T1d")[:max_results] 
    for a in raw_links: 
        link = a["href"] 
        if link.startswith("./"): 
            link = "https://news.google.com" + link[1:] 
        title = a.get_text(strip=True) 
        articles.append({"title": title, "url": link}) 
    return articles 

# -----------------------------
# Playwright to resolve final URL and extract text
# -----------------------------
import trafilatura

def resolve_and_extract(gnews_url):
    downloaded = trafilatura.fetch_url(gnews_url)
    if not downloaded:
        return {"publisher": "Desconocido", "url": gnews_url, "text": ""}

    # Try to detect publisher
    soup = BeautifulSoup(downloaded, "html.parser")
    publisher = None
    og_site = soup.find("meta", property="og:site_name")
    if og_site:
        publisher = og_site.get("content")

    text = trafilatura.extract(downloaded, include_comments=False, include_tables=False)
    if not text:
        text = ""

    return {
        "publisher": publisher or "Desconocido",
        "url": gnews_url,
        "text": text
    }

# -----------------------------
# Summarizers
# -----------------------------

import requests

HF_HEADERS = {"Authorization": f"Bearer {st.secrets['hf_api_key']}"}

MODELS = {
    "es": "mrm8488/bert2bert_shared-spanish-finetuned-summarization",
    "en": "sshleifer/distilbart-cnn-12-6"
}

def hf_summarize(text, lang="es"):
    model_id = MODELS.get(lang, MODELS["en"])
    API_URL = f"https://api-inference.huggingface.co/models/{model_id}"

    payload = {
        "inputs": text[:3000],  # truncate to avoid oversized payloads
        "parameters": {"min_length": 40, "max_length": 130}
    }
    response = requests.post(API_URL, headers=HF_HEADERS, json=payload)

    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and len(data) > 0 and "summary_text" in data[0]:
            return data[0]["summary_text"]
        else:
            return "⚠️ No se pudo generar resumen"
    else:
        return f"❌ Error {response.status_code}: {response.text}"


def summarize_text(text, lang="es"):
    text = text[:3000]  # evitar input demasiado largo
    if lang == "es":
        return hf_summarize(text, max_length=130, min_length=40, do_sample=False)[0]["summary_text"]
    else:
        return hf_summarize(text, max_length=130, min_length=40, do_sample=False)[0]["summary_text"]

# -----------------------------
# Email sender 
# -----------------------------
def send_email(subject, body, recipients): 
    data = { 'Messages': [ { 
        "From": {"Email": "cuenta.de.repuesto2021@gmail.com", "Name": "News Bot"}, 
        "To": [{"Email": r.strip(), "Name": r.strip()} for r in recipients], 
        "Subject": subject, 
        "TextPart": body 
    } ] } 
    result = mailjet.send.create(data=data) 
    return result.status_code 

# -----------------------------
# Streamlit UI 
# -----------------------------
st.set_page_config(page_title="Buscador y scraper de noticias", page_icon="📰") 
st.title("📰 Buscador y scraper de noticias") 

query = st.text_input("Ingrese palabra clave (en minuscula y separado por comas si hay más de una)", "Formula 1") 
lang = st.text_input("Lenguaje (e.g., en, es, fr)", "es") 
country = st.text_input("País (e.g., US, AR, FR)", "US") 
date_filter = st.selectbox("Filtrar por fecha", options=["", "1d", "7d", "1m"],
    format_func=lambda x: { "": "Sin filtro", "1d": "Últimas 24 horas", "7d": "Última semana", "1m": "Último mes" }[x]) 
num_articles = st.slider("Número de artículos", 1, 50, 5)

# Load and manage emails 
emails = load_emails() 
st.subheader("📧 Lista de emails") 

# Always display the list
if emails:
    st.write("**Emails actuales:**", ", ".join(emails))
else:
    st.info("No hay emails guardados aún.")

email_input = st.text_input("Agregar nuevo email") 
if st.button("➕ Agregar"): 
    if email_input and email_input not in emails: 
        emails.append(email_input) 
        save_emails(emails) 
        st.success(f"{email_input} agregado!") 

remove_input = st.selectbox("Eliminar email", [""] + list(emails)) 
if st.button("➖ Eliminar") and remove_input: 
    emails.remove(remove_input) 
    save_emails(emails) 
    st.warning(f"{remove_input} eliminado!") 
    st.write("**Emails actuales:**", ", ".join(emails)) 

# Run scraper + send 
if st.button("Buscar y enviar"): 
    st.write("🔍 Scrapeando noticias...") 
    articles = scrape_gnews(query, lang=lang, country=country, max_results=num_articles, date_filter=date_filter) 
    
    if articles: 
        st.success("✅ Artículos scrapeados exitosamente!") 
        for a in articles: 
            try:
                info = resolve_and_extract(a["url"])
                resumen = hf_summarize(info["text"], lang if lang in ["es", "en"] else "en")


                st.markdown(f"**{a['title']}**") 
                st.write(f"Fuente: {info['publisher']}") 
                st.write(f"🔗 [Leer artículo completo]({info['url']})") 
                st.write(f"📝 Resumen: {resumen}") 
                st.write("---")

            except Exception as e:
                st.error(f"Error al procesar {a['url']}: {e}")

        body = "\n\n".join([f"{a['title']}\n{a['url']}" for a in articles]) 
        st.write("📧 Enviando emails...") 
        status = send_email(f"Resultados de noticias acerca de '{query}'", body, emails) 
        if status == 200: 
            st.success("✅ Email enviado!")
        else: 
            st.error("❌ No se pudo enviar el email.") 
    else: 
        st.warning("No se encontraron artículos.")
