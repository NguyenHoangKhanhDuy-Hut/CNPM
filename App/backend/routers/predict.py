import json
import logging
import re
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.database import get_db
from services.diseases import DiseasesService
from services.disease_drug_mappings import Disease_drug_mappingsService
from services.drugs import DrugsService
from services.aihub import AIHubService
from schemas.aihub import GenTxtRequest, ChatMessage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/predict", tags=["predict"])

# Common Vietnamese medical symptom keywords
MEDICAL_KEYWORDS = {
    "sốt", "ho", "đau", "nhức", "mệt", "chóng", "mặt", "buồn", "nôn", "tiêu",
    "chảy", "ngạt", "khó", "thở", "tức", "ngực", "đầy", "bụng", "rối", "loạn",
    "mất", "ngủ", "chán", "ăn", "sụt", "cân", "gầy", "yếu", "liệt", "run",
    "co", "giật", "tê", "bì", "ngứa", "phát", "ban", "nổi", "mề", "đay",
    "sưng", "phù", "xuất", "huyết", "chấm", "đỏ", "da", "vàng", "mắt",
    "tim", "huyết", "áp", "loạn", "nhịp", "đánh", "trống", "ngực", "hen",
    "suyễn", "viêm", "phổi", "phế", "quản", "lao", "ung", "thư", "u", "bướu",
    "tiểu", "đường", "đái", "tháo", "mỡ", "máu", "gout", "khớp", "xương",
    "cơ", "bắp", "lưng", "cổ", "vai", "gáy", "đầu", "nửa", "đầu", "migraine",
    "răng", "miệng", "lợi", "họng", "thanh", "quản", "mũi", "xoang", "tai",
    "giảm", "thị", "lực", "mờ", "cận", "viễn", "loạn", "thị", "giác",
    "trầm", "cảm", "lo", "âu", "căng", "thẳng", "stress", "hoảng", "loạn",
    "hoa", "mắt", "ù", "tai", "nóng", "lạnh", "ớn", "rét", "run",
    "bệnh", "triệu", "chứng", "dấu", "hiệu", "chuẩn", "đoán", "xét", "nghiệm",
    "thuốc", "điều", "trị", "chữa", "uống", "tiêm", "truyền",
    "viêm", "nhiễm", "trùng", "virus", "vi", "khuẩn", "nấm", "ký", "sinh",
}

# Also check individual Vietnamese characters that could be part of symptom words
VIETNAMESE_CHARS = set("ăâđêôơưừắằẳẵặấầẩẫậéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ")


def is_nonsense_input(text: str) -> bool:
    """Detect if input is gibberish/nonsense rather than medical symptoms."""
    if not text or len(text.strip()) < 3:
        return True

    cleaned = text.lower().strip()
    words = re.findall(r'[a-zA-Zàáạảãâầấậẩẫăắằặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớởỡợùúụủũưừứựửữỳýỵỷỹđ]+', cleaned)

    if not words:
        return True

    # Check if any word is a recognized medical keyword
    medical_word_count = 0
    for word in words:
        if word in MEDICAL_KEYWORDS:
            medical_word_count += 1

    # At least 1 medical keyword expected in genuine symptom description
    if medical_word_count == 0:
        # Check for partial matches (e.g. "sot" instead of "sốt")
        for word in words:
            for kw in MEDICAL_KEYWORDS:
                if kw in word or word in kw:
                    medical_word_count += 0.5
                    break

    # Gibberish detection: check if input has repetitive patterns
    if len(cleaned) >= 6:
        # Check for keyboard smashing like "asdfghjkl" or "qwerty"
        consecutive_consonants = 0
        max_consecutive = 0
        vowels = set("aeiouy")
        for ch in cleaned:
            if ch.isalpha() and ch not in vowels:
                consecutive_consonants += 1
                max_consecutive = max(max_consecutive, consecutive_consonants)
            else:
                consecutive_consonants = 0
        if max_consecutive >= 8:
            return True

        # Check for repeated characters like "aaaaaa" or "111111"
        if any(ch * 5 in cleaned for ch in set(cleaned) if ch.isalpha()):
            return True

    return medical_word_count < 0.5


class PredictRequest(BaseModel):
    symptoms: str
    disease_name: Optional[str] = None


class PredictionItem(BaseModel):
    disease_id: int
    disease_name: str
    accuracy_score: int
    description: str
    risk_level: str
    group_name: str
    icon: str
    symptoms: Optional[str] = None
    suggested_drugs: list = []
    ai_explanation: Optional[str] = None


class PredictResponse(BaseModel):
    disease_id: int
    disease_name: str
    accuracy_score: int
    description: str
    risk_level: str
    group_name: str
    icon: str
    symptoms: Optional[str] = None
    suggested_drugs: list = []
    ai_explanation: Optional[str] = None
    predictions: list[PredictionItem] = []


@router.post("", response_model=PredictResponse)
async def predict_disease(
    data: PredictRequest,
    db: Session = Depends(get_db),
):
    """Predict disease based on symptoms using AI and database matching"""
    logger.info(f"Prediction request: symptoms={data.symptoms}, disease_name={data.disease_name}")

    # Validate input - detect nonsense
    combined_input = f"{data.symptoms} {data.disease_name or ''}".strip()
    if is_nonsense_input(combined_input):
        raise HTTPException(
            status_code=400,
            detail="Vui lòng nhập triệu chứng hợp lệ (ví dụ: sốt, ho, đau đầu, mệt mỏi...). "
                   "Dự đoán AI chỉ hoạt động với mô tả triệu chứng y tế có ý nghĩa."
        )

    diseases_service = DiseasesService(db)
    drugs_service = DrugsService(db)
    mappings_service = Disease_drug_mappingsService(db)

    # Get all diseases for matching
    diseases_result = diseases_service.get_list(skip=0, limit=1000)
    diseases = diseases_result.get("items", [])

    if not diseases:
        logger.warning("Diseases table is empty, attempting to reload mock data...")
        try:
            from services.mock_data import initialize_mock_data
            initialize_mock_data()
            diseases_result = diseases_service.get_list(skip=0, limit=1000)
            diseases = diseases_result.get("items", [])
        except Exception as reload_err:
            logger.error(f"Failed to reload mock data: {reload_err}")

    if not diseases:
        raise HTTPException(status_code=404, detail="No diseases found in database")

    # Build disease info for AI prompt
    disease_info = []
    for d in diseases:
        disease_info.append({
            "id": d.id,
            "name": d.name,
            "symptoms": d.symptoms or "",
            "group": d.group_name,
            "risk": d.risk_level,
        })

    # Use AI to match symptoms to top diseases
    prompt = f"""Bạn là một bác sĩ AI chuyên khoa. Dựa trên triệu chứng được mô tả, hãy phân tích và chọn ra TOP 3 bệnh phù hợp nhất từ danh sách bệnh có sẵn, xếp theo thứ tự từ phù hợp nhất đến ít phù hợp hơn.

Triệu chứng người dùng mô tả: {data.symptoms}
{"Tên bệnh gợi ý: " + data.disease_name if data.disease_name else ""}

Danh sách bệnh có sẵn:
{json.dumps(disease_info, ensure_ascii=False, indent=2)}

Hãy phân tích kỹ lưỡng các triệu chứng, đối chiếu với từng bệnh và trả về JSON array với format. PHẢI trả về ĐÚNG 3 bệnh:
[{{"disease_id": <id>, "accuracy_score": <điểm 60-99>, "explanation": "<giải thích tại sao chọn bệnh này>"}},
 {{"disease_id": <id>, "accuracy_score": <điểm 60-99>, "explanation": "<giải thích>"}},
 {{"disease_id": <id>, "accuracy_score": <điểm 60-99>, "explanation": "<giải thích>"}}]

CHỈ trả về JSON array, không có text khác."""

    predictions = []

    try:
        ai_service = AIHubService()
        request = GenTxtRequest(
            messages=[
                ChatMessage(role="system", content="You are a medical AI assistant. Return ONLY valid JSON array."),
                ChatMessage(role="user", content=prompt),
            ],
            model="llama-3.3-70b-versatile",
        )

        # Close DB transaction before slow AI call
        db.rollback()

        response = await ai_service.gentxt(request)
        raw_content = response.content.strip()

        # Extract JSON
        if raw_content.startswith("```"):
            match = re.search(r"```(?:json)?\n(.*?)```", raw_content, re.DOTALL)
            if match:
                raw_content = match.group(1).strip()

        start = raw_content.find("[")
        end = raw_content.rfind("]")
        if start >= 0 and end > start:
            raw_content = raw_content[start:end + 1]

        results = json.loads(raw_content)
        if not isinstance(results, list):
            results = [results]

        for item in results[:3]:
            disease = diseases_service.get_by_id(item.get("disease_id"))
            if disease:
                predictions.append({
                    "disease": disease,
                    "accuracy_score": min(99, max(60, item.get("accuracy_score", 85))),
                    "explanation": item.get("explanation", ""),
                })

    except Exception as e:
        logger.warning(f"AI prediction failed, using fallback matching: {str(e)}")

    # Build fallback predictions if AI returned fewer than 3
    if len(predictions) < 3:
        symptoms_lower = data.symptoms.lower()
        scored = []
        for d in diseases:
            if any(p["disease"].id == d.id for p in predictions):
                continue
            score = 0
            disease_symptoms = (d.symptoms or "").lower()
            for symptom in symptoms_lower.split(","):
                symptom = symptom.strip()
                if symptom and symptom in disease_symptoms:
                    score += 1
            if data.disease_name and data.disease_name.lower() in d.name.lower():
                score += 5
            if score > 0:
                scored.append((d, score))
        scored.sort(key=lambda x: x[1], reverse=True)

        for d, score in scored[: 3 - len(predictions)]:
            predictions.append({
                "disease": d,
                "accuracy_score": min(95, 60 + score * 8),
                "explanation": f"Phù hợp dựa trên từ khóa triệu chứng (điểm: {score})",
            })

    # If still empty, add defaults (excluding the first if already used)
    used_ids = {p["disease"].id for p in predictions}
    for d in diseases:
        if len(predictions) >= 3:
            break
        if d.id not in used_ids:
            predictions.append({
                "disease": d,
                "accuracy_score": 50,
                "explanation": "Dự phòng - bệnh có trong hệ thống",
            })
            used_ids.add(d.id)

    # Build full response with drugs for each prediction
    result_predictions = []
    for pred in predictions:
        disease = pred["disease"]
        mappings_result = mappings_service.get_list(
            skip=0, limit=10,
            query_dict={"disease_id": disease.id},
            sort="priority",
        )
        mappings = mappings_result.get("items", [])

        suggested_drugs = []
        for mapping in mappings:
            try:
                drug = await drugs_service.get_by_generic_name(mapping.drug_name)
                if drug:
                    suggested_drugs.append({
                        "id": drug.get("id", hash(mapping.drug_name)),
                        "name": drug.get("name", mapping.drug_name),
                        "generic_name": drug.get("generic_name", mapping.drug_name),
                        "code": drug.get("code", ""),
                        "group_name": drug.get("group_name", "FDA"),
                        "manufacturer": drug.get("manufacturer", "FDA"),
                        "price": drug.get("price", ""),
                        "rating": drug.get("rating", 0),
                        "usage_info": drug.get("usage_info", ""),
                        "dosage": drug.get("dosage", ""),
                        "match_score": mapping.match_score,
                        "priority": mapping.priority,
                        "data_source": drug.get("data_source", "openfda"),
                    })
            except Exception as e:
                logger.warning(f"Failed to fetch drug {mapping.drug_name}: {str(e)}")
                suggested_drugs.append({
                    "id": hash(mapping.drug_name),
                    "name": mapping.drug_name,
                    "generic_name": mapping.drug_name,
                    "code": "",
                    "group_name": "FDA",
                    "manufacturer": "FDA",
                    "price": "",
                    "rating": 0,
                    "usage_info": "",
                    "dosage": "",
                    "match_score": mapping.match_score,
                    "priority": mapping.priority,
                    "data_source": "openfda",
                })

        result_predictions.append({
            "disease_id": disease.id,
            "disease_name": disease.name,
            "accuracy_score": pred["accuracy_score"],
            "description": disease.description,
            "risk_level": disease.risk_level,
            "group_name": disease.group_name,
            "icon": disease.icon or "🏥",
            "symptoms": disease.symptoms,
            "suggested_drugs": suggested_drugs,
            "ai_explanation": pred["explanation"],
        })

    top = result_predictions[0]
    return PredictResponse(
        disease_id=top["disease_id"],
        disease_name=top["disease_name"],
        accuracy_score=top["accuracy_score"],
        description=top["description"],
        risk_level=top["risk_level"],
        group_name=top["group_name"],
        icon=top["icon"],
        symptoms=top["symptoms"],
        suggested_drugs=top["suggested_drugs"],
        ai_explanation=top["ai_explanation"],
        predictions=result_predictions,
    )


\\note
