from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
from bs4 import BeautifulSoup

def get_wikipedia_url_selenium(query: str):
    options = Options()
    # options.add_argument("--headless")  # Bật lại nếu muốn chạy nền
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(f"https://www.google.com/search?q={query}+site:vi.wikipedia.org")
        print("[⏳] Chờ phần tử div.yuRUbf a xuất hiện...")

        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a"))
        )

        result_links = driver.find_elements(By.CSS_SELECTOR, "div.yuRUbf a")
        print(f"[🔍] Link trong div.yuRUbf: {len(result_links)}")

        # Nếu không có kết quả trong div.yuRUbf, fallback sang toàn bộ <a>
        if not result_links:
            result_links = driver.find_elements(By.CSS_SELECTOR, "a")
            print(f"[🧪] Fallback – Tổng số <a>: {len(result_links)}")

        for link in result_links:
            href = link.get_attribute("href")
            print("→", href)
            if href and "vi.wikipedia.org/wiki/" in href:
                print("✅ Wikipedia URL tìm thấy!")
                return href
    except Exception as e:
        print("❌ Lỗi khi crawl:", e)
    finally:
        driver.quit()

    return None

def get_content_from_wiki(href):
    if not href:
        print("❌ Không có URL hợp lệ để lấy nội dung.")
        return None

    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(href, headers=headers)
        if res.status_code != 200:
            print(f"❌ Không truy cập được URL: {href}")
            return None

        soup = BeautifulSoup(res.text, "html.parser")
        paragraphs = soup.select("p")
        content = "\n".join(
            p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)
        )
        return content
    except Exception as e:
        print(f"❌ Lỗi khi lấy nội dung từ Wikipedia: {e}")
        return None

if __name__ == "__main__":
    query = "Nhà thờ Lớn Hà Nội"
    print(f"\n🔍 Tìm Wikipedia với Selenium cho: {query}")
    url = get_wikipedia_url_selenium(query)
    if url:
        print(f"\n🔗 Wikipedia URL: {url}")
        content = get_content_from_wiki(url)
        if content:
            print(f"\n📄 Nội dung trích xuất (500 ký tự đầu):\n{content[:500]}")
        else:
            print("❌ Không trích được nội dung.")
    else:
        print("❌ Không tìm thấy URL Wikipedia.")
