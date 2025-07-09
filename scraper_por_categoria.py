import requests
from bs4 import BeautifulSoup
from google_sheets import create_sheet
from htm_rendering import get_rendered_html
from utilities import normalize_text

EMAIL = "sebareitze@gmail.com"
BASE_URL = "https://xepelin.com/blog/"

def extract_author(soup):
    author_div = soup.find("div", class_="text-sm dark:text-text-disabled")
    if author_div:
        author_name = author_div.text.strip()
        return author_name
    return "Desconocido" 

def get_post_details(url, categoria):
    print(f"🔍 Fetching details for URL: {url}")
    html = get_rendered_html(url)
    print("✅ HTML content fetched successfully")
    soup = BeautifulSoup(html, "html.parser")

    # Título
    title_tag = soup.select_one("h1[class*=ArticleSingle_title]")
    title = title_tag.text.strip() if title_tag else "Sin título"
    print(f"📝 Title extracted: {title}")

    # Tiempo de lectura
    read_time_tag = soup.select_one("div.text-grey-600")
    read_time = read_time_tag.text.strip() if read_time_tag else "-"
    print(f"⏳ Read time extracted: {read_time}")

    # Autor
    author = extract_author(soup)
    print(f"👤 Author extracted: {author}")

    # Fecha (placeholder)
    date = "02-02-2025"
    print(f"📅 Date set: {date}")

    return [title, categoria, author, read_time, date]

def get_category_link_from_input(categoria):
    html_content = get_rendered_html(BASE_URL)
    soup = BeautifulSoup(html_content, "html.parser")

    categoria_normalizada = normalize_text(categoria)

    navbar = soup.find("nav")
    if navbar:
        for a_tag in navbar.find_all("a", href=True):
            link_text = a_tag.get_text(strip=True).lower()
            link_text_normalized = normalize_text(link_text)
            if link_text_normalized == categoria_normalizada:
                href = a_tag["href"]
                if not href.startswith("http"):
                    href = BASE_URL.rstrip("/") + href
                print(f"✅ Link encontrado para la categoría '{categoria}': {href}")
                return href
    print(f"❌ No se encontró link para la categoría '{categoria}'")
    return None

def get_blog_links(categoria):
    url = get_category_link_from_input(categoria)
    html_content = get_rendered_html(url, click_cargar_mas=True)
    soup = BeautifulSoup(html_content, "html.parser")
    post_links = set()

    h1_tag = soup.find("h1")
    if h1_tag:
        for a_tag in h1_tag.find_next("div").find_all("a", href=True):
            href = a_tag["href"]
            if href.startswith(BASE_URL):
                post_links.add(href)
    else:
        print(f"❌ No matching <h1> found for category: {categoria}")

    print(f"✅ Encontrados {len(post_links)} posts en la categoría '{categoria}':")

    return list(post_links)

def scrape_blog(categoria, worksheet=None):
    links = get_blog_links(categoria)

    posts = []
    for link in links:
        print(f"Scrapeando: {link}")
        data = get_post_details(link, categoria)
        posts.append(data)
        if worksheet:
            worksheet.append_row(data)
    return posts

def send_webhook(webhook_url, sheet_url):
    payload = {"email": EMAIL, "link": sheet_url}
    requests.post(webhook_url, json=payload)

def scrap_and_save(categoria, webhook_url):
    try:
        sheet_url, worksheet = create_sheet()
        print(f"📄 Sheet creado en: {sheet_url}")

        rows = scrape_blog(categoria, worksheet=worksheet)
        print(f"✅ Posts encontrados: {len(rows)}")

        send_webhook(webhook_url, sheet_url)
        print("✅ Webhook enviado")
    except Exception as e:
        print(f"❌ Error en scrape_and_save: {e}")
