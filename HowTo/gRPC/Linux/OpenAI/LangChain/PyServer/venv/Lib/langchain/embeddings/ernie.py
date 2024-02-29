import logging
import threading
from typing import Dict, List, Optional

import requests

from langchain.embeddings.base import Embeddings
from langchain.pydantic_v1 import BaseModel, root_validator
from langchain.utils import get_from_dict_or_env

logger = logging.getLogger(__name__)


class ErnieEmbeddings(BaseModel, Embeddings):
    """`Ernie Embeddings V1` embedding models."""

    ernie_client_id: Optional[str] = None
    ernie_client_secret: Optional[str] = None
    access_token: Optional[str] = None

    chunk_size: int = 16

    model_name = "ErnieBot-Embedding-V1"

    _lock = threading.Lock()

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        values["ernie_client_id"] = get_from_dict_or_env(
            values,
            "ernie_client_id",
            "ERNIE_CLIENT_ID",
        )
        values["ernie_client_secret"] = get_from_dict_or_env(
            values,
            "ernie_client_secret",
            "ERNIE_CLIENT_SECRET",
        )
        return values

    def _embedding(self, json: object) -> dict:
        base_url = (
            "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/embeddings"
        )
        resp = requests.post(
            f"{base_url}/embedding-v1",
            headers={
                "Content-Type": "application/json",
            },
            params={"access_token": self.access_token},
            json=json,
        )
        return resp.json()

    def _refresh_access_token_with_lock(self) -> None:
        with self._lock:
            logger.debug("Refreshing access token")
            base_url: str = "https://aip.baidubce.com/oauth/2.0/token"
            resp = requests.post(
                base_url,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                params={
                    "grant_type": "client_credentials",
                    "client_id": self.ernie_client_id,
                    "client_secret": self.ernie_client_secret,
                },
            )
            self.access_token = str(resp.json().get("access_token"))

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not self.access_token:
            self._refresh_access_token_with_lock()
        text_in_chunks = [
            texts[i : i + self.chunk_size]
            for i in range(0, len(texts), self.chunk_size)
        ]
        lst = []
        for chunk in text_in_chunks:
            resp = self._embedding({"input": [text for text in chunk]})
            if resp.get("error_code"):
                if resp.get("error_code") == 111:
                    self._refresh_access_token_with_lock()
                    resp = self._embedding({"input": [text for text in chunk]})
                else:
                    raise ValueError(f"Error from Ernie: {resp}")
            lst.extend([i["embedding"] for i in resp["data"]])
        return lst

    def embed_query(self, text: str) -> List[float]:
        if not self.access_token:
            self._refresh_access_token_with_lock()
        resp = self._embedding({"input": [text]})
        if resp.get("error_code"):
            if resp.get("error_code") == 111:
                self._refresh_access_token_with_lock()
                resp = self._embedding({"input": [text]})
            else:
                raise ValueError(f"Error from Ernie: {resp}")
        return resp["data"][0]["embedding"]
