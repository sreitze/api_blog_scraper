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

def get_blog_links(categoria):
    # Para el scraper completo, necesitamos construir la URL de forma diferente
    # que el scraper por categoría (que usa get_category_link_from_input)
    categoria_normalizada = normalize_text(categoria)
    url = f"{BASE_URL}{categoria_normalizada}"
    print(f"🔍 Fetching links from category URL: {url}")
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

def get_categories_links():
    url = f"{BASE_URL}"
    print(f"🔍 Fetching categories from: {url}")
    html_content = get_rendered_html(url)
    soup = BeautifulSoup(html_content, "html.parser")

    category_links = set()

    navbar = soup.find("nav")
    if navbar:
        for a_tag in navbar.find_all("a", href=True):
            href = a_tag["href"]
            # Asegurar que el href esté completo
            if not href.startswith("http"):
                href = BASE_URL.rstrip("/") + href
            # Filtrar solo los links de categorías del blog
            if "/blog/" in href and href != BASE_URL.rstrip("/") + "/blog/":
                category_links.add(href)
                print(f"✅ Categoría encontrada: {href}")

    print(f"✅ Total de categorías encontradas: {len(category_links)}")
    return list(category_links)

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

def scrap_and_save_all_categories(webhook_url):
    try:
        category_links = get_categories_links()
        sheet_url, worksheet = create_sheet()
        print(f"📄 Sheet creado en: {sheet_url}")

        all_posts = []
        for category_link in category_links:
            # Extraer el nombre de la categoría de la URL
            categoria = category_link.split("/blog/")[-1].rstrip("/")
            print(f"🏷️ Procesando categoría: {categoria}")
            posts = scrape_blog(categoria, worksheet)
            all_posts.extend(posts)
        
        print(f"✅ Total de posts encontrados: {len(all_posts)}")
        send_webhook(webhook_url, sheet_url)
        print("✅ Webhook enviado")
    except Exception as e:
        print(f"❌ Error en scrap_and_save_all_categories: {e}")