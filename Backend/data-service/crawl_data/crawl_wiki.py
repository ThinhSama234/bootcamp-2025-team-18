import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

def extract_wiki_content_by_title(title: str) -> str | None:
    """Truy cập trực tiếp và trích xuất nội dung từ trang Wikipedia tiếng Việt."""
    # Encode tiêu đề để đảm bảo URL hợp lệ
    encoded_title = quote(title.replace(" ", "_"))
    url = f"https://vi.wikipedia.org/wiki/{encoded_title}"

    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        print(f"❌ Không truy cập được URL: {url}")
        return None

    soup = BeautifulSoup(res.text, "html.parser")
    paragraphs = soup.select("p")
    content = "\n".join(
        p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)
    )
    return content

if __name__ == "__main__":
    query = "Nhà_thờ_Lớn_Hà_Nội"
    print(f"📘 Đang truy xuất Wikipedia cho: {query}")
    content = extract_wiki_content_by_title(query)

    if content:
        print(f"📄 Nội dung trích xuất (500 ký tự đầu):\n{content[:500]}")
    else:
        print("❌ Không tìm thấy nội dung.")
