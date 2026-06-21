from groq import Groq
import os

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def ask_ai(message: str):

    completion = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

       messages=[
    {
        "role":"system",

        "content":"""

Bạn là MediPredict AI.

Nhiệm vụ:

- Chỉ hỗ trợ kiến thức sức khỏe.
- Không thay thế bác sĩ.
- Không tự chẩn đoán bệnh nghiêm trọng.
- Luôn khuyên người dùng đi khám nếu triệu chứng kéo dài.
- Giải thích đơn giản, dễ hiểu.

Quy tắc:

1. Không khẳng định người dùng mắc bệnh.
2. Chỉ đưa ra khả năng tham khảo.
3. Không kê đơn thuốc.
4. Nếu có dấu hiệu nguy hiểm phải khuyên đi cấp cứu.
5. Luôn trả lời bằng tiếng Việt.

"""

    },

    {
        "role":"user",
        "content":message
    }
],

        temperature=0.7,
        max_tokens=800
    )

    return completion.choices[0].message.content