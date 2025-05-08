import requests
from bs4 import BeautifulSoup
import time
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
def get_all_attractions(province_url):
    """Lấy tất cả các điểm tham quan từ trang tỉnh thành, bao gồm các trang phân trang."""
    response = requests.get(province_url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    attraction_sections = soup.find("h2", string="Điểm tham quan nổi tiếng")
    if not attraction_sections:
        print("Không tìm thấy phần 'Điểm tham quan nổi tiếng' trên trang tỉnh thành.")
        return
    else:
        see_all_link = attraction_sections.find_next("a", class_="see-all")
        if not see_all_link:
            print("Không tìm thấy liên kết 'Xem tất cả' trong phần 'Điểm tham quan nổi tiếng'.")
            return
        print(see_all_link["href"])
        # lấy link
        base_url = "https://mia.vn"
        all_attractions_url = base_url +"/"+ see_all_link["href"]
        print(f"URL của tất cả các điểm tham quan: {all_attractions_url}")
        page = 1
        num_page_save = 0
        while True:
            page_url = all_attractions_url if page == 1 else f"{all_attractions_url.split('?')[0]}?page={page}"
            print(f"Đang truy cập trang: {page_url}")
            response = requests.get(page_url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            attraction_cards = soup.find_all(class_="article-link")
            if not attraction_cards:
                print(f"Không tìm thấy điểm tham quan nào trên trang {page}. Dừng lại.")
                break
            if not attraction_cards:
                print(f"Không tìm thấy điểm tham quan nào trên trang {page}.")
                break
            for card in attraction_cards:
                link = card["href"]
                print(f"Liên kết đến điểm tham quan: {link}")
                # lưu url vào txt file
                url_file = base_url + "/" + link
                with open("attraction_links.txt", "a", encoding="utf-8") as f:
                    f.write(url_file + "\n")
                num_page_save += 1
            page+=1
            time.sleep(1)
    print(f"Đã lưu {num_page_save} liên kết điểm tham quan vào file 'attraction_links.txt'.")
if __name__ == "__main__":
    # URL của trang tỉnh thành
    province_url = "https://mia.vn/cam-nang-du-lich/khanh-hoa"
    get_all_attractions(province_url)
    # xong rồi chạy file crawl_web_llm_json.py để lấy dữ liệu từ file attraction_links.txt 
    # và lưu vào MongoDB