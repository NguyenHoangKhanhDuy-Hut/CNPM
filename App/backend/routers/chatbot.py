import json
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.database import get_db
from services.aihub import AIHubService
from schemas.aihub import GenTxtRequest, ChatMessage
from services.diseases import DiseasesService
from services.drugs import DrugsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/chatbot", tags=["chatbot"])

BASE_SYSTEM_PROMPT = """Bạn là trợ lý AI của MediPredict - Hệ thống Dự đoán Bệnh và Tra cứu Thuốc thông minh.

Mục tiêu của MediPredict:
1. Dự đoán bệnh dựa trên triệu chứng người dùng nhập vào
2. Gợi ý thuốc phù hợp cho từng bệnh (bao gồm thông tin từ FDA)
3. Tra cứu thông tin chi tiết về bệnh và thuốc
4. Cung cấp kiến thức y tế hữu ích cho người dùng

Hướng dẫn trả lời:
- Trả lời bằng tiếng Việt, thân thiện, dễ hiểu
- Luôn nhấn mạnh rằng kết quả chỉ mang tính tham khảo, cần gặp bác sĩ để được chẩn đoán chính xác
- Không đưa ra lời khuyên y tế mang tính quyết định
- Nếu người dùng hỏi về bệnh cụ thể, hướng dẫn họ dùng tính năng Dự đoán bệnh tại /predict
- Nếu người dùng hỏi về thuốc, hướng dẫn họ tra cứu tại /drugs
- Nếu được hỏi về danh sách bệnh hoặc thuốc, hãy trả lời dựa trên dữ liệu được cung cấp bên dưới
- Trả lời ngắn gọn, súc tích, tập trung vào giá trị thực tế"""


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


def build_system_prompt(db: Session) -> str:
    diseases_service = DiseasesService(db)
    drugs_service = DrugsService(db)

    diseases_result = diseases_service.get_list(skip=0, limit=100)
    diseases = diseases_result.get("items", [])

    drugs_result = drugs_service.get_list(skip=0, limit=50)
    drugs = drugs_result.get("items", [])

    context_parts = [BASE_SYSTEM_PROMPT]

    if diseases:
        disease_list = []
        for d in diseases[:30]:
            disease_list.append(f"- {d.name} (triệu chứng: {d.symptoms or 'không có thông tin'})")
        context_parts.append("\nDanh sách bệnh trong hệ thống:\n" + "\n".join(disease_list))

    if drugs:
        drug_list = []
        for dr in drugs[:20]:
            drug_list.append(f"- {dr.name} (nhóm: {dr.group_name}, NSX: {dr.manufacturer})")
        context_parts.append("\nDanh sách thuốc trong hệ thống:\n" + "\n".join(drug_list))

    return "\n\n".join(context_parts)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        ai_service = AIHubService()
        system_prompt = build_system_prompt(db)
        gen_request = GenTxtRequest(
            messages=[
                ChatMessage(role="system", content=system_prompt),
                ChatMessage(role="user", content=request.message),
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=1024,
        )
        response = await ai_service.gentxt(gen_request)
        return ChatResponse(response=response.content)
    except ValueError as e:
        logger.error(f"AI service configuration error: {e}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AI service chưa được cấu hình")
    except Exception as e:
        error_str = str(e)
        logger.error(f"Chatbot error: {e}")
        if "429" in error_str or "quota" in error_str.lower() or "RESOURCE_EXHAUSTED" in error_str:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="API AI đã hết quota. Vui lòng thử lại sau 1-2 phút hoặc liên hệ admin để nâng cấp API key.",
            )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
