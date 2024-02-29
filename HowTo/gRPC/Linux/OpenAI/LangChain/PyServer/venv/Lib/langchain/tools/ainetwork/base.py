"""Base class for AINetwork tools."""
from __future__ import annotations

import asyncio
import threading
from enum import Enum
from typing import TYPE_CHECKING, Any, Optional

from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.pydantic_v1 import Field
from langchain.tools.ainetwork.utils import authenticate
from langchain.tools.base import BaseTool

if TYPE_CHECKING:
    from ain.ain import Ain


class OperationType(str, Enum):
    SET = "SET"
    GET = "GET"


class AINBaseTool(BaseTool):
    """Base class for the AINetwork tools."""

    interface: Ain = Field(default_factory=authenticate)
    """The interface object for the AINetwork Blockchain."""

    def _run(
        self,
        *args: Any,
        run_manager: Optional[CallbackManagerForToolRun] = None,
        **kwargs: Any,
    ) -> str:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            result_container = []

            def thread_target() -> None:
                nonlocal result_container
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    result_container.append(
                        new_loop.run_until_complete(self._arun(*args, **kwargs))
                    )
                except Exception as e:
                    result_container.append(e)
                finally:
                    new_loop.close()

            thread = threading.Thread(target=thread_target)
            thread.start()
            thread.join()
            result = result_container[0]
            if isinstance(result, Exception):
                raise result
            return result

        else:
            result = loop.run_until_complete(self._arun(*args, **kwargs))
            loop.close()
            return result
