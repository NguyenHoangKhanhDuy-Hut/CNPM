import logging
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

OPENFDA_BASE_URL = "https://api.fda.gov"
DEFAULT_API_KEY = "cYzhzoHiQdDiwxC3w3smJ5Fp5rlpKudgLVvgrkQ9"


class OpenFDAService:
    def __init__(self, api_key: str = DEFAULT_API_KEY):
        self.api_key = api_key

    async def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{OPENFDA_BASE_URL}{path}"
        query_params = dict(params or {})
        query_params["api_key"] = self.api_key
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                resp = await client.get(url, params=query_params)
                resp.raise_for_status()
                return resp.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"openFDA HTTP error: {e.response.status_code} - {e.response.text}")
                return {"error": True, "status": e.response.status_code, "detail": e.response.text}
            except Exception as e:
                logger.error(f"openFDA request error: {str(e)}")
                return {"error": True, "detail": str(e)}

    async def search_drug_label(
        self,
        search: str,
        limit: int = 10,
        skip: int = 0,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {"limit": limit, "skip": skip}
        if search:
            params["search"] = search
        return await self._get("/drug/label.json", params)

    async def get_drug_label_by_brand(
        self,
        brand_name: str,
        limit: int = 5,
    ) -> Dict[str, Any]:
        return await self.search_drug_label(
            search=f"openfda.brand_name:{brand_name}",
            limit=limit,
        )

    async def get_drug_label_by_generic(
        self,
        generic_name: str,
        limit: int = 5,
    ) -> Dict[str, Any]:
        return await self.search_drug_label(
            search=f"openfda.generic_name:{generic_name}",
            limit=limit,
        )

    async def search_drug_events(
        self,
        search: str,
        limit: int = 10,
        skip: int = 0,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {"limit": limit, "skip": skip}
        if search:
            params["search"] = search
        return await self._get("/drug/event.json", params)

    async def get_drug_events_by_name(
        self,
        drug_name: str,
        limit: int = 10,
    ) -> Dict[str, Any]:
        return await self.search_drug_events(
            search=f"patient.drug.openfda.brand_name:{drug_name}",
            limit=limit,
        )

    async def search_drug_recalls(
        self,
        search: str = "",
        limit: int = 10,
        skip: int = 0,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {"limit": limit, "skip": skip}
        if search:
            params["search"] = search
        return await self._get("/drug/enforcement.json", params)

    async def get_drug_recalls_by_name(
        self,
        product_name: str,
        limit: int = 10,
    ) -> Dict[str, Any]:
        return await self.search_drug_recalls(
            search=f"product_description:{product_name}",
            limit=limit,
        )

    async def search_ndc(
        self,
        search: str,
        limit: int = 10,
        skip: int = 0,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {"limit": limit, "skip": skip}
        if search:
            params["search"] = search
        return await self._get("/drug/ndc.json", params)

    async def enrich_drug_info(
        self,
        brand_name: str = "",
        generic_name: str = "",
    ) -> Dict[str, Any]:
        labels = []
        if brand_name:
            label_resp = await self.get_drug_label_by_brand(brand_name, limit=3)
            if not label_resp.get("error") and "results" in label_resp:
                labels = label_resp["results"]
        if not labels and generic_name:
            label_resp = await self.get_drug_label_by_generic(generic_name, limit=3)
            if not label_resp.get("error") and "results" in label_resp:
                labels = label_resp["results"]
        events_resp = await self.get_drug_events_by_name(brand_name or generic_name, limit=5)
        events = []
        if not events_resp.get("error") and "results" in events_resp:
            events = events_resp["results"]
        recalls_resp = await self.get_drug_recalls_by_name(brand_name or generic_name, limit=5)
        recalls = []
        if not recalls_resp.get("error") and "results" in recalls_resp:
            recalls = recalls_resp["results"]
        result: Dict[str, Any] = {}
        if labels:
            result["label"] = self._extract_label_summary(labels[0])
        if events:
            result["adverse_events"] = self._summarize_events(events)
        if recalls:
            result["recalls"] = self._summarize_recalls(recalls)
        return result

    def _extract_label_summary(self, label: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "brand_name": (label.get("openfda") or {}).get("brand_name", [None])[0] if label.get("openfda") else None,
            "generic_name": (label.get("openfda") or {}).get("generic_name", [None])[0] if label.get("openfda") else None,
            "manufacturer_name": (label.get("openfda") or {}).get("manufacturer_name", [None])[0] if label.get("openfda") else None,
            "purpose": label.get("purpose", []),
            "warnings": label.get("warnings", []),
            "dosage_and_administration": label.get("dosage_and_administration", []),
            "adverse_reactions": label.get("adverse_reactions", []),
            "drug_interactions": label.get("drug_interactions", []),
            "contraindications": label.get("contraindications", []),
            "indications_and_usage": label.get("indications_and_usage", []),
            "boxed_warning": label.get("boxed_warning", []),
        }

    def _summarize_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        summarized = []
        for event in events[:5]:
            patient = event.get("patient", {})
            reaction_list = patient.get("reaction", [])
            summarized.append({
                "serious": event.get("serious"),
                "seriousnessdeath": event.get("seriousnessdeath"),
                "seriousnesshospitalization": event.get("seriousnesshospitalization"),
                "reactions": [r.get("reactionmeddrapt") for r in reaction_list if r.get("reactionmeddrapt")],
                "receivedate": event.get("receiptdate"),
            })
        return summarized

    def _summarize_recalls(self, recalls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        summarized = []
        for recall in recalls[:5]:
            summarized.append({
                "recall_status": recall.get("status"),
                "recall_reason": recall.get("reason_for_recall"),
                "product_description": recall.get("product_description"),
                "recalling_firm": recall.get("recalling_firm"),
                "report_date": recall.get("report_date"),
                "classification": recall.get("classification"),
            })
        return summarized
