from __future__ import annotations

import copy
import json
import logging
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Literal,
    Optional,
    TypedDict,
    Union,
    overload,
)

from langchain.callbacks.manager import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,
)
from langchain.llms.base import LLM
from langchain.pydantic_v1 import PrivateAttr

if TYPE_CHECKING:
    import openllm


ServerType = Literal["http", "grpc"]


class IdentifyingParams(TypedDict):
    """Parameters for identifying a model as a typed dict."""

    model_name: str
    model_id: Optional[str]
    server_url: Optional[str]
    server_type: Optional[ServerType]
    embedded: bool
    llm_kwargs: Dict[str, Any]


logger = logging.getLogger(__name__)


class OpenLLM(LLM):
    """OpenLLM, supporting both in-process model
    instance and remote OpenLLM servers.

    To use, you should have the openllm library installed:

    .. code-block:: bash

        pip install openllm

    Learn more at: https://github.com/bentoml/openllm

    Example running an LLM model locally managed by OpenLLM:
        .. code-block:: python

            from langchain.llms import OpenLLM
            llm = OpenLLM(
                model_name='flan-t5',
                model_id='google/flan-t5-large',
            )
            llm("What is the difference between a duck and a goose?")

    For all available supported models, you can run 'openllm models'.

    If you have a OpenLLM server running, you can also use it remotely:
        .. code-block:: python

            from langchain.llms import OpenLLM
            llm = OpenLLM(server_url='http://localhost:3000')
            llm("What is the difference between a duck and a goose?")
    """

    model_name: Optional[str] = None
    """Model name to use. See 'openllm models' for all available models."""
    model_id: Optional[str] = None
    """Model Id to use. If not provided, will use the default model for the model name.
    See 'openllm models' for all available model variants."""
    server_url: Optional[str] = None
    """Optional server URL that currently runs a LLMServer with 'openllm start'."""
    server_type: ServerType = "http"
    """Optional server type. Either 'http' or 'grpc'."""
    embedded: bool = True
    """Initialize this LLM instance in current process by default. Should 
    only set to False when using in conjunction with BentoML Service."""
    llm_kwargs: Dict[str, Any]
    """Key word arguments to be passed to openllm.LLM"""

    _runner: Optional[openllm.LLMRunner] = PrivateAttr(default=None)
    _client: Union[
        openllm.client.HTTPClient, openllm.client.GrpcClient, None
    ] = PrivateAttr(default=None)

    class Config:
        extra = "forbid"

    @overload
    def __init__(
        self,
        model_name: Optional[str] = ...,
        *,
        model_id: Optional[str] = ...,
        embedded: Literal[True, False] = ...,
        **llm_kwargs: Any,
    ) -> None:
        ...

    @overload
    def __init__(
        self,
        *,
        server_url: str = ...,
        server_type: Literal["grpc", "http"] = ...,
        **llm_kwargs: Any,
    ) -> None:
        ...

    def __init__(
        self,
        model_name: Optional[str] = None,
        *,
        model_id: Optional[str] = None,
        server_url: Optional[str] = None,
        server_type: Literal["grpc", "http"] = "http",
        embedded: bool = True,
        **llm_kwargs: Any,
    ):
        try:
            import openllm
        except ImportError as e:
            raise ImportError(
                "Could not import openllm. Make sure to install it with "
                "'pip install openllm.'"
            ) from e

        llm_kwargs = llm_kwargs or {}

        if server_url is not None:
            logger.debug("'server_url' is provided, returning a openllm.Client")
            assert (
                model_id is None and model_name is None
            ), "'server_url' and {'model_id', 'model_name'} are mutually exclusive"
            client_cls = (
                openllm.client.HTTPClient
                if server_type == "http"
                else openllm.client.GrpcClient
            )
            client = client_cls(server_url)

            super().__init__(
                **{
                    "server_url": server_url,
                    "server_type": server_type,
                    "llm_kwargs": llm_kwargs,
                }
            )
            self._runner = None  # type: ignore
            self._client = client
        else:
            assert model_name is not None, "Must provide 'model_name' or 'server_url'"
            # since the LLM are relatively huge, we don't actually want to convert the
            # Runner with embedded when running the server. Instead, we will only set
            # the init_local here so that LangChain users can still use the LLM
            # in-process. Wrt to BentoML users, setting embedded=False is the expected
            # behaviour to invoke the runners remotely.
            # We need to also enable ensure_available to download and setup the model.
            runner = openllm.Runner(
                model_name=model_name,
                model_id=model_id,
                init_local=embedded,
                ensure_available=True,
                **llm_kwargs,
            )
            super().__init__(
                **{
                    "model_name": model_name,
                    "model_id": model_id,
                    "embedded": embedded,
                    "llm_kwargs": llm_kwargs,
                }
            )
            self._client = None  # type: ignore
            self._runner = runner

    @property
    def runner(self) -> openllm.LLMRunner:
        """
        Get the underlying openllm.LLMRunner instance for integration with BentoML.

        Example:
        .. code-block:: python

            llm = OpenLLM(
                model_name='flan-t5',
                model_id='google/flan-t5-large',
                embedded=False,
            )
            tools = load_tools(["serpapi", "llm-math"], llm=llm)
            agent = initialize_agent(
                tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION
            )
            svc = bentoml.Service("langchain-openllm", runners=[llm.runner])

            @svc.api(input=Text(), output=Text())
            def chat(input_text: str):
                return agent.run(input_text)
        """
        if self._runner is None:
            raise ValueError("OpenLLM must be initialized locally with 'model_name'")
        return self._runner

    @property
    def _identifying_params(self) -> IdentifyingParams:
        """Get the identifying parameters."""
        if self._client is not None:
            self.llm_kwargs.update(self._client.configuration)
            model_name = self._client.model_name
            model_id = self._client.model_id
        else:
            if self._runner is None:
                raise ValueError("Runner must be initialized.")
            model_name = self.model_name
            model_id = self.model_id
            try:
                self.llm_kwargs.update(
                    json.loads(self._runner.identifying_params["configuration"])
                )
            except (TypeError, json.JSONDecodeError):
                pass
        return IdentifyingParams(
            server_url=self.server_url,
            server_type=self.server_type,
            embedded=self.embedded,
            llm_kwargs=self.llm_kwargs,
            model_name=model_name,
            model_id=model_id,
        )

    @property
    def _llm_type(self) -> str:
        return "openllm_client" if self._client else "openllm"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> str:
        try:
            import openllm
        except ImportError as e:
            raise ImportError(
                "Could not import openllm. Make sure to install it with "
                "'pip install openllm'."
            ) from e

        copied = copy.deepcopy(self.llm_kwargs)
        copied.update(kwargs)
        config = openllm.AutoConfig.for_model(
            self._identifying_params["model_name"], **copied
        )
        if self._client:
            return self._client.query(prompt, **config.model_dump(flatten=True))
        else:
            assert self._runner is not None
            return self._runner(prompt, **config.model_dump(flatten=True))

    async def _acall(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        try:
            import openllm
        except ImportError as e:
            raise ImportError(
                "Could not import openllm. Make sure to install it with "
                "'pip install openllm'."
            ) from e

        copied = copy.deepcopy(self.llm_kwargs)
        copied.update(kwargs)
        config = openllm.AutoConfig.for_model(
            self._identifying_params["model_name"], **copied
        )
        if self._client:
            return await self._client.acall(
                "generate", prompt, **config.model_dump(flatten=True)
            )
        else:
            assert self._runner is not None
            (
                prompt,
                generate_kwargs,
                postprocess_kwargs,
            ) = self._runner.llm.sanitize_parameters(prompt, **kwargs)
            generated_result = await self._runner.generate.async_run(
                prompt, **generate_kwargs
            )
            return self._runner.llm.postprocess_generate(
                prompt, generated_result, **postprocess_kwargs
            )
