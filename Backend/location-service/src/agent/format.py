from transformers import pipeline
from openai import OpenAI

XAI_API_KEY = "xai-Lwvyn1pZr6KIOX6DEguKthSUkIvhINLmjeUyD72SqJd6RHtk43JYxKyohxrNFdkLcuk3CngJjkMDAmhO"
client = OpenAI(
    api_key=XAI_API_KEY,
    base_url="https://api.x.ai/v1",
)

class TextProcessor:
    def __init__(self):
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

    def summarize_text(self, text: str, max_length: int = 50) -> str:
        return self.summarizer(text, max_length=max_length, min_length=10, do_sample=False)[0]['summary_text']

    def format_response(self, user_messages: list, record: dict) -> str:
        """
        Tạo câu trả lời phù hợp dựa trên tin nhắn người dùng và bản ghi dữ liệu.
        
        Args:
            user_messages (list): Danh sách tin nhắn của người dùng (str)
            record (dict): Bản ghi dữ liệu (ví dụ: thông tin địa điểm)
        
        Returns:
            str: Câu trả lời từ Grok
        """
        context = " ".join(user_messages)
        summarized_context = self.summarize_text(context, max_length=100)
        #print("Summarized context:", summarized_context)

        name = record.get("data", {}).get("name", "Địa điểm")
        address = record.get("data", {}).get("address", "Địa chỉ không rõ")
        description = record.get("data", {}).get("description", "Mô tả không có")

        prompt = (
            f"User context: {summarized_context}\n"
            f"Record: This is a location record - Name: {name}, Address: {address}, Description: {description}\n"
            f"Instruction: Provide a helpful and concise response based on the user context and the location record."
        )

        try:
            completion = client.chat.completions.create(
                model="grok-3-beta",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response = completion.choices[0].message.content
            return f"{response}"

        except Exception as e:
            return f"Đây là địa điểm phù hợp với yêu cầu của bạn."

if __name__ == "__main__":
    Process = TextProcessor()

    user_messages = [
        "Tôi nghĩ chúng ta nên đi đến Ninh Bình.",
        "Ồ, đó thực sự là danh lam thắng cảnh nổi tiếng.",
        "Tuyệt vời, tôi cũng đang muốn ăn món núi rừng"
    ]
    record = {
        "_id": "6820a1bc3dd0a2e345dc4c00",
        "data": {
            "name": "Vườn Quốc Gia Cúc Phương",
            "category": "Công viên",
            "address": "Xã Cúc Phương, Huyện Nho Quan, Ninh Bình",
            "description": "Vườn Quốc Gia Cúc Phương là khu bảo tồn thiên nhiên với núi rừng xanh mướt. Du khách có thể ngắm cảnh, trekking và khám phá động vật hoang dã."
        }
    }

    response = Process.format_response(user_messages, record)
    print("Response:", response)