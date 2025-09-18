# import streamlit as st
# import requests
# from bs4 import BeautifulSoup
# from newspaper import Article
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
# # Scraper function (close to your notebook)
# # -----------------------------
# def scrape_gnews(query, lang="en", country="US", max_results=5):
#     """
#     Scrape Google News articles based on query, language, and country.
#     """
#     url = f"https://news.google.com/search?q={query}&hl={lang}&gl={country}&ceid={country}:{lang}"
#     r = requests.get(url, headers={'User-Agent': ua.chrome}, timeout=10)
#     soup = BeautifulSoup(r.text, "html.parser")

#     # Extract article links
#     raw_links = [a["href"] for a in soup.select("a.DY5T1d")[:max_results]]
#     links = []
#     for link in raw_links:
#         if link.startswith("./"):
#             link = "https://news.google.com" + link[1:]
#         links.append(link)

#     # Parse articles
#     articles = []
#     for link in links:
#         try:
#             article = Article(link)
#             article.download()
#             article.parse()
#             articles.append({
#                 "title": article.title,
#                 "text": article.text,
#                 "url": link
#             })
#         except Exception as e:
#             st.error(f"No se pudo parsear el artículo: {e}")
#             continue

#     return articles


# # -----------------------------
# # Email sender
# # -----------------------------
# def send_email(subject, body, recipients):
#     """Send email using Mailjet API."""
#     data = {
#       'Messages': [
#         {
#           "From": {"Email": "anapaulacastillozuain@gmail.com", "Name": "News Bot"},
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

# query = st.text_input("Ingrese palabra clave", "Formula 1")
# lang = st.text_input("Lenguaje (e.g., en, es, fr)", "es")
# country = st.text_input("País (e.g., US, AR, FR)", "US")
# num_articles = st.slider("Número de artículos", 1, 50, 5)
# emails = st.text_area("Emails (separados con coma)", "team@example.com")

# if st.button("Buscar y enviar"):
#     st.write("🔍 Scrapeando noticias...")
#     articles = scrape_gnews(query, lang=lang, country=country, max_results=num_articles)

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

# -----------------------------
# Configure Mailjet
# -----------------------------
API_KEY = st.secrets["api_key"]
API_SECRET = st.secrets["api_secret"]

mailjet = Client(auth=(API_KEY, API_SECRET), version='v3.1')
ua = UserAgent()


# -----------------------------
# Scraper function
# -----------------------------
def scrape_gnews(query, lang="en", country="US", max_results=5):
    """
    Scrape Google News article titles and links based on query, language, and country.
    """
    url = f"https://news.google.com/search?q={query}&hl={lang}&gl={country}&ceid={country}:{lang}"
    r = requests.get(url, headers={'User-Agent': ua.chrome}, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    # Extract titles + links
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
# Email sender
# -----------------------------
def send_email(subject, body, recipients):
    """Send email using Mailjet API."""
    data = {
      'Messages': [
        {
          "From": {"Email": "anapaulacastillozuain@gmail.com", "Name": "News Bot"},
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

query = st.text_input("Ingrese palabra clave", "Formula 1")
lang = st.text_input("Lenguaje (e.g., en, es, fr)", "es")
country = st.text_input("País (e.g., US, AR, FR)", "US")
num_articles = st.slider("Número de artículos", 1, 50, 5)
emails = st.text_area("Emails (separados con coma)", "team@example.com")

if st.button("Buscar y enviar"):
    st.write("🔍 Scrapeando noticias...")
    articles = scrape_gnews(query, lang=lang, country=country, max_results=num_articles)

    if articles:
        st.success("✅ Artículos scrapeados exitosamente!")
        for a in articles:
            st.markdown(f"**{a['title']}**  \n[{a['url']}]({a['url']})")

        body = "\n\n".join([f"{a['title']}\n{a['url']}" for a in articles])

        st.write("📧 Enviando emails...")
        recipients = emails.split(",")
        status = send_email(f"Resultados de noticias acerca de '{query}'", body, recipients)

        if status == 200:
            st.success("✅ Email enviado!")
        else:
            st.error("❌ No se pudo enviar el email.")
    else:
        st.warning("No se encontraron artículos.")
