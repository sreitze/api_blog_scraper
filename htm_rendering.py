from playwright.sync_api import sync_playwright

def get_rendered_html(url, click_cargar_mas=False):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_default_timeout(60000)
        print(f"🔗 Navigating to URL: {url}")
        try:
            page.goto(url)
            print("✅ Page loaded successfully")
            if click_cargar_mas:
                page.wait_for_load_state("networkidle")
                while True:
                    try:
                        cargar_mas_button = page.locator("button:has-text('Cargar más')")
                        if cargar_mas_button.is_visible():
                            print("🖱️ Haciendo clic en 'Cargar más'")
                            cargar_mas_button.click()
                            page.wait_for_timeout(2000)
                        else:
                            print("✅ No hay más botón 'Cargar más'")
                            break
                    except Exception as e:
                        print(f"⚠️ Error al intentar hacer clic en 'Cargar más': {e}")
                        break
            else:
                page.wait_for_timeout(5000)
        except Exception as e:
            print(f"❌ Error durante la carga de la página: {e}")
            browser.close()
            return ""
        
        html = page.content()
        browser.close()
        return html