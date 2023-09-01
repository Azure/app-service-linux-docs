from typing import Any, Dict, List, Optional

import requests

from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader

NOTION_BASE_URL = "https://api.notion.com/v1"
DATABASE_URL = NOTION_BASE_URL + "/databases/{database_id}/query"
PAGE_URL = NOTION_BASE_URL + "/pages/{page_id}"
BLOCK_URL = NOTION_BASE_URL + "/blocks/{block_id}/children"


class NotionDBLoader(BaseLoader):
    """Load from `Notion DB`.

    Reads content from pages within a Notion Database.
    Args:
        integration_token (str): Notion integration token.
        database_id (str): Notion database id.
        request_timeout_sec (int): Timeout for Notion requests in seconds.
            Defaults to 10.
    """

    def __init__(
        self,
        integration_token: str,
        database_id: str,
        request_timeout_sec: Optional[int] = 10,
    ) -> None:
        """Initialize with parameters."""
        if not integration_token:
            raise ValueError("integration_token must be provided")
        if not database_id:
            raise ValueError("database_id must be provided")

        self.token = integration_token
        self.database_id = database_id
        self.headers = {
            "Authorization": "Bearer " + self.token,
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }
        self.request_timeout_sec = request_timeout_sec

    def load(self) -> List[Document]:
        """Load documents from the Notion database.
        Returns:
            List[Document]: List of documents.
        """
        page_summaries = self._retrieve_page_summaries()

        return list(self.load_page(page_summary) for page_summary in page_summaries)

    def _retrieve_page_summaries(
        self, query_dict: Dict[str, Any] = {"page_size": 100}
    ) -> List[Dict[str, Any]]:
        """Get all the pages from a Notion database."""
        pages: List[Dict[str, Any]] = []

        while True:
            data = self._request(
                DATABASE_URL.format(database_id=self.database_id),
                method="POST",
                query_dict=query_dict,
            )

            pages.extend(data.get("results"))

            if not data.get("has_more"):
                break

            query_dict["start_cursor"] = data.get("next_cursor")

        return pages

    def load_page(self, page_summary: Dict[str, Any]) -> Document:
        """Read a page.

        Args:
            page_summary: Page summary from Notion API.
        """
        page_id = page_summary["id"]

        # load properties as metadata
        metadata: Dict[str, Any] = {}

        for prop_name, prop_data in page_summary["properties"].items():
            prop_type = prop_data["type"]

            if prop_type == "rich_text":
                value = (
                    prop_data["rich_text"][0]["plain_text"]
                    if prop_data["rich_text"]
                    else None
                )
            elif prop_type == "title":
                value = (
                    prop_data["title"][0]["plain_text"] if prop_data["title"] else None
                )
            elif prop_type == "multi_select":
                value = (
                    [item["name"] for item in prop_data["multi_select"]]
                    if prop_data["multi_select"]
                    else []
                )
            elif prop_type == "url":
                value = prop_data["url"]
            elif prop_type == "unique_id":
                value = (
                    f'{prop_data["unique_id"]["prefix"]}-{prop_data["unique_id"]["number"]}'
                    if prop_data["unique_id"]
                    else None
                )
            elif prop_type == "status":
                value = prop_data["status"]["name"] if prop_data["status"] else None
            elif prop_type == "people":
                value = (
                    [item["name"] for item in prop_data["people"]]
                    if prop_data["people"]
                    else []
                )
            else:
                value = None

            metadata[prop_name.lower()] = value

        metadata["id"] = page_id

        return Document(page_content=self._load_blocks(page_id), metadata=metadata)

    def _load_blocks(self, block_id: str, num_tabs: int = 0) -> str:
        """Read a block and its children."""
        result_lines_arr: List[str] = []
        cur_block_id: str = block_id

        while cur_block_id:
            data = self._request(BLOCK_URL.format(block_id=cur_block_id))

            for result in data["results"]:
                result_obj = result[result["type"]]

                if "rich_text" not in result_obj:
                    continue

                cur_result_text_arr: List[str] = []

                for rich_text in result_obj["rich_text"]:
                    if "text" in rich_text:
                        cur_result_text_arr.append(
                            "\t" * num_tabs + rich_text["text"]["content"]
                        )

                if result["has_children"]:
                    children_text = self._load_blocks(
                        result["id"], num_tabs=num_tabs + 1
                    )
                    cur_result_text_arr.append(children_text)

                result_lines_arr.append("\n".join(cur_result_text_arr))

            cur_block_id = data.get("next_cursor")

        return "\n".join(result_lines_arr)

    def _request(
        self, url: str, method: str = "GET", query_dict: Dict[str, Any] = {}
    ) -> Any:
        res = requests.request(
            method,
            url,
            headers=self.headers,
            json=query_dict,
            timeout=self.request_timeout_sec,
        )
        res.raise_for_status()
        return res.json()
