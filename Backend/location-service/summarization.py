from google import genai
import re
import json
from langchain_core.messages import HumanMessage

client = genai.Client(api_key="AIzaSyDU3Hl2kTKLMOPJlK4tIU3s6vpHYq8d-58")

def summarization(messages):
    """
    Summarize Vietnamese messages using Google GenAI API.
    
    Args:
        messages (list): List of user messages.
    
    Returns:
        dict: Summary and extracted entities.
    """

    # join messages into a single string
    input_text = ". ".join([msg.content.strip() if isinstance(msg, HumanMessage) else msg.strip() 
                            for msg in messages if (msg.content.strip() if isinstance(msg, HumanMessage) else msg.strip())])
    if not input_text:
        return {"summary": "Invalid input!", "entities": {"locations": [], "features": [], "activities": []}}

    prompt = f"""
        Tóm tắt các yêu cầu du lịch bằng tiếng Việt trong một câu ngắn gọn (tối đa 25 từ),
        ưu tiên địa điểm (vùng miền, tỉnh, thành phố), đặc điểm (biển, núi, rừng,...) và hoạt động (ngắm cảnh, leo núi,...),
        chỉ giữ các thông tin cốt lõi, bỏ các từ như "muốn", "đi du lịch", "tìm nơi có",...
        Input: {input_text}
        Output format: 
        Tóm tắt: <summary>
        Thực thể: {{'locations': [], 'features': [], 'activities': []}}
        """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        output = response.text.strip()

        summary_match = re.search(r"Tóm tắt: (.*?)\n", output)
        entities_match = re.search(r"Thực thể: ({.*?})", output)

        summary = summary_match.group(1) if summary_match else "Không thể tóm tắt."
        try:
            entities = json.loads(entities_match.group(1).replace("'", "\"")) if entities_match else {"locations": [], "features": [], "activities": []}
        except json.JSONDecodeError:
            entities = {"locations": [], "features": [], "activities": []}

        return {
            "summary": summary,
            "entities": entities
        }
    except Exception as e:
        print(f"Error: {e}")
        return {
            "summary": "Error occurred during API call.", 
            "entities": {"locations": [], "features": [], "activities": []}
        }
    
def main():
    user_messages = [
        "Tôi muốn đi du lịch đến một nơi có nhiều cảnh đẹp thiên nhiên, không khí trong lành và yên tĩnh.",
        "Còn tôi thì muốn đi đến một nơi nào đó ở miền Nam.",
        "Tôi nghĩ chúng ta nên đi đến một nơi có đồi núi.",
        "Tây Ninh thì sao nhỉ?",
        "Thật đúng lúc, tôi đang muốn leo núi.",
        "Tôi nghĩ đó là ý hay đấy!",
        "Lâu rồi tôi chưa ăn mãng cầu.",
        "Ở đó có chùa không nhỉ mọi người?",
        "Tôi nghe nói thứ 7 tuần này có concert ở đó."
    ]
    # result
    # summary: Miền Nam, Tây Ninh có đồi núi để leo núi, ngắm cảnh, có thể có chùa và concert thứ 7.
    # entities: {'locations': ['miền Nam', 'Tây Ninh'], 'features': ['đồi núi'], 'activities': ['leo núi', 'ngắm cảnh']}
    result = summarization(user_messages)
    print("User messages:", user_messages)
    print("Summary:", result["summary"])
    print("Entities:", result["entities"])

if __name__ == "__main__":
    main()
