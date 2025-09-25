# import streamlit as st
# import requests
# from bs4 import BeautifulSoup
# from mailjet_rest import Client
# from fake_useragent import UserAgent

# # -----------------------------
# # Configure Mailjet
# # -----------------------------
# API_KEY = st.secrets["api_key"]
# API_SECRET = st.secrets["api_secret"]

# mailjet = Client(auth=(API_KEY, API_SECRET), version='v3.1')
# ua = UserAgent()


# # -----------------------------
# # Scraper function
# # -----------------------------
# def scrape_gnews(query, lang="en", country="US", max_results=5, date_filter=None):
#     """
#     Scrape Google News article titles and links based on query, language, country, and optional date filter.
#     """
#     # Add date filter if provided (e.g., when:7d, when:1m)
#     if date_filter:
#         query = f"{query} when:{date_filter}"

#     url = f"https://news.google.com/search?q={query}&hl={lang}&gl={country}&ceid={country}:{lang}"
#     r = requests.get(url, headers={'User-Agent': ua.chrome}, timeout=10)
#     soup = BeautifulSoup(r.text, "html.parser")

#     # Extract titles + links
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
#       'Messages': [
#         {
#           "From": {"Email": "cuenta.de.repuesto2021@gmail.com", "Name": "News Bot"},
#           "To": [{"Email": r.strip(), "Name": r.strip()} for r in recipients],
#           "Subject": subject,
#           "TextPart": body
#         }
#       ]
#     }
#     result = mailjet.send.create(data=data)
#     return result.status_code


# # -----------------------------
# # Streamlit UI
# # -----------------------------
# st.set_page_config(page_title="Buscador y scraper de noticias", page_icon="📰")
# st.title("📰 Buscador y scraper de noticias")

# query = st.text_input("Ingrese palabra clave (en minuscula y separado por comas si hay más de una)", "Formula 1")
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
# emails = st.text_area("Emails (separados con coma)", "team@example.com")

# if st.button("Buscar y enviar"):
#     st.write("🔍 Scrapeando noticias...")
#     articles = scrape_gnews(query, lang=lang, country=country, max_results=num_articles, date_filter=date_filter)

#     if articles:
#         st.success("✅ Artículos scrapeados exitosamente!")
#         for a in articles:
#             st.markdown(f"**{a['title']}**  \n[{a['url']}]({a['url']})")

#         body = "\n\n".join([f"{a['title']}\n{a['url']}" for a in articles])

#         st.write("📧 Enviando emails...")
#         recipients = emails.split(",")
#         status = send_email(f"Resultados de noticias acerca de '{query}'", body, recipients)

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
import json
import os

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
        save_emails(["team@example.com"])  # default
    with open(EMAIL_FILE, "r") as f:
        return json.load(f)["emails"]

def save_emails(emails):
    with open(EMAIL_FILE, "w") as f:
        json.dump({"emails": emails}, f, indent=4)

# -----------------------------
# Scraper function
# -----------------------------
def scrape_gnews(query, lang="en", country="US", max_results=5, date_filter=None):
    """Scrape Google News article titles, links, publisher and snippet."""
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

        # Publisher: look upward in the DOM tree for the div
        publisher_tag = a.find_parent("article").select_one("div.SVJrMe")
        publisher = publisher_tag.get_text(strip=True) if publisher_tag else "Desconocido"

        # Snippet: also inside the same article card
        snippet_tag = a.find_parent("article").select_one("spanx.BNeawe.s3v9rd")
        snippet = snippet_tag.get_text(strip=True) if snippet_tag else "Sin resumen disponible."

        articles.append({
            "title": title,
            "url": link,
            "publisher": publisher,
            "summary": snippet
        })

    return articles

# -----------------------------
# Email sender
# -----------------------------
def send_email(subject, body, recipients):
    data = {
      'Messages': [
        {
          "From": {"Email": "cuenta.de.repuesto2021@gmail.com", "Name": "News Bot"},
          "To": [{"Email": r.strip(), "Name": r.strip()} for r in recipients],
          "Subject": subject,
          "TextPart": body
        }
      ]
    }
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
date_filter = st.selectbox(
    "Filtrar por fecha",
    options=["", "1d", "7d", "1m"],
    format_func=lambda x: {
        "": "Sin filtro",
        "1d": "Últimas 24 horas",
        "7d": "Última semana",
        "1m": "Último mes"
    }[x]
)
num_articles = st.slider("Número de artículos", 1, 50, 5)

# Load and manage emails
emails = load_emails()
st.subheader("📧 Lista de emails")
email_input = st.text_input("Agregar nuevo email")
if st.button("➕ Agregar"):
    if email_input and email_input not in emails:
        emails.append(email_input)
        save_emails(emails)
        st.success(f"{email_input} agregado!")

remove_input = st.selectbox("Eliminar email", [""] + emails)
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
            st.markdown(f"**{a['title']}**  \n*{a['publisher']}*  \n{a['summary']}  \n[{a['url']}]({a['url']})")

        body = "\n\n".join([
            f"{a['title']} ({a['publisher']})\n{a['summary']}\n{a['url']}"
            for a in articles
        ])

        st.write("📧 Enviando emails...")
        status = send_email(f"Resultados de noticias acerca de '{query}'", body, emails)

        if status == 200:
            st.success("✅ Email enviado!")
        else:
            st.error("❌ No se pudo enviar el email.")
    else:
        st.warning("No se encontraron artículos.")
