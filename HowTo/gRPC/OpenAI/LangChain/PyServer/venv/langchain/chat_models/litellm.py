"""Wrapper around LiteLLM's model I/O library."""
from __future__ import annotations

import logging
from typing import (
    Any,
    AsyncIterator,
    Callable,
    Dict,
    Iterator,
    List,
    Mapping,
    Optional,
    Tuple,
    Union,
)

from langchain.callbacks.manager import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,
)
from langchain.chat_models.base import BaseChatModel
from langchain.llms.base import create_base_retry_decorator
from langchain.pydantic_v1 import Field, root_validator
from langchain.schema import (
    ChatGeneration,
    ChatResult,
)
from langchain.schema.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    BaseMessageChunk,
    ChatMessage,
    ChatMessageChunk,
    HumanMessage,
    HumanMessageChunk,
    SystemMessage,
    SystemMessageChunk,
)
from langchain.schema.output import ChatGenerationChunk
from langchain.utils import get_from_dict_or_env

logger = logging.getLogger(__name__)


class ChatLiteLLMException(Exception):
    """Error with the `LiteLLM I/O` library"""


def _truncate_at_stop_tokens(
    text: str,
    stop: Optional[List[str]],
) -> str:
    """Truncates text at the earliest stop token found."""
    if stop is None:
        return text

    for stop_token in stop:
        stop_token_idx = text.find(stop_token)
        if stop_token_idx != -1:
            text = text[:stop_token_idx]
    return text


class FunctionMessage(BaseMessage):
    """Message for passing the result of executing a function back to a model."""

    name: str
    """The name of the function that was executed."""

    @property
    def type(self) -> str:
        """Type of the message, used for serialization."""
        return "function"


class FunctionMessageChunk(FunctionMessage, BaseMessageChunk):
    """Message Chunk for passing the result of executing a function back to a model."""

    pass


def _create_retry_decorator(
    llm: ChatLiteLLM,
    run_manager: Optional[
        Union[AsyncCallbackManagerForLLMRun, CallbackManagerForLLMRun]
    ] = None,
) -> Callable[[Any], Any]:
    """Returns a tenacity retry decorator, preconfigured to handle PaLM exceptions"""
    import openai

    errors = [
        openai.error.Timeout,
        openai.error.APIError,
        openai.error.APIConnectionError,
        openai.error.RateLimitError,
        openai.error.ServiceUnavailableError,
    ]
    return create_base_retry_decorator(
        error_types=errors, max_retries=llm.max_retries, run_manager=run_manager
    )


def _convert_dict_to_message(_dict: Mapping[str, Any]) -> BaseMessage:
    role = _dict["role"]
    if role == "user":
        return HumanMessage(content=_dict["content"])
    elif role == "assistant":
        # Fix for azure
        # Also OpenAI returns None for tool invocations
        content = _dict.get("content", "") or ""
        if _dict.get("function_call"):
            additional_kwargs = {"function_call": dict(_dict["function_call"])}
        else:
            additional_kwargs = {}
        return AIMessage(content=content, additional_kwargs=additional_kwargs)
    elif role == "system":
        return SystemMessage(content=_dict["content"])
    elif role == "function":
        return FunctionMessage(content=_dict["content"], name=_dict["name"])
    else:
        return ChatMessage(content=_dict["content"], role=role)


async def acompletion_with_retry(
    llm: ChatLiteLLM,
    run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
    **kwargs: Any,
) -> Any:
    """Use tenacity to retry the async completion call."""
    retry_decorator = _create_retry_decorator(llm, run_manager=run_manager)

    @retry_decorator
    async def _completion_with_retry(**kwargs: Any) -> Any:
        # Use OpenAI's async api https://github.com/openai/openai-python#async-api
        return await llm.client.acreate(**kwargs)

    return await _completion_with_retry(**kwargs)


def _convert_delta_to_message_chunk(
    _dict: Mapping[str, Any], default_class: type[BaseMessageChunk]
) -> BaseMessageChunk:
    role = _dict.get("role")
    content = _dict.get("content") or ""
    if _dict.get("function_call"):
        additional_kwargs = {"function_call": dict(_dict["function_call"])}
    else:
        additional_kwargs = {}

    if role == "user" or default_class == HumanMessageChunk:
        return HumanMessageChunk(content=content)
    elif role == "assistant" or default_class == AIMessageChunk:
        return AIMessageChunk(content=content, additional_kwargs=additional_kwargs)
    elif role == "system" or default_class == SystemMessageChunk:
        return SystemMessageChunk(content=content)
    elif role == "function" or default_class == FunctionMessageChunk:
        return FunctionMessageChunk(content=content, name=_dict["name"])
    elif role or default_class == ChatMessageChunk:
        return ChatMessageChunk(content=content, role=role)
    else:
        return default_class(content=content)


def _convert_message_to_dict(message: BaseMessage) -> dict:
    if isinstance(message, ChatMessage):
        message_dict = {"role": message.role, "content": message.content}
    elif isinstance(message, HumanMessage):
        message_dict = {"role": "user", "content": message.content}
    elif isinstance(message, AIMessage):
        message_dict = {"role": "assistant", "content": message.content}
        if "function_call" in message.additional_kwargs:
            message_dict["function_call"] = message.additional_kwargs["function_call"]
    elif isinstance(message, SystemMessage):
        message_dict = {"role": "system", "content": message.content}
    elif isinstance(message, FunctionMessage):
        message_dict = {
            "role": "function",
            "content": message.content,
            "name": message.name,
        }
    else:
        raise ValueError(f"Got unknown type {message}")
    if "name" in message.additional_kwargs:
        message_dict["name"] = message.additional_kwargs["name"]
    return message_dict


class ChatLiteLLM(BaseChatModel):
    """`LiteLLM` Chat models API.

        1. The ``GOOGLE_API_KEY``` environment variable set with your API key, or
        2. Pass your API key using the google_api_key kwarg to the ChatGoogle
           constructor.

    Example:
        .. code-block:: python

            from langchain.chat_models import ChatGooglePalm
            chat = ChatGooglePalm()

    """

    client: Any  #: :meta private:
    model: str = "gpt-3.5-turbo"
    model_name: Optional[str] = None
    """Model name to use."""
    openai_api_key: Optional[str] = None
    azure_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    replicate_api_key: Optional[str] = None
    cohere_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    streaming: bool = False
    api_base: Optional[str] = None
    organization: Optional[str] = None
    custom_llm_provider: Optional[str] = None
    request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    temperature: Optional[float] = 1
    model_kwargs: Dict[str, Any] = Field(default_factory=dict)
    """Run inference with this temperature. Must by in the closed
       interval [0.0, 1.0]."""
    top_p: Optional[float] = None
    """Decode using nucleus sampling: consider the smallest set of tokens whose
       probability sum is at least top_p. Must be in the closed interval [0.0, 1.0]."""
    top_k: Optional[int] = None
    """Decode using top-k sampling: consider the set of top_k most probable tokens.
       Must be positive."""
    n: int = 1
    """Number of chat completions to generate for each prompt. Note that the API may
       not return the full n completions if duplicates are generated."""
    max_tokens: int = 256

    max_retries: int = 6

    @property
    def _default_params(self) -> Dict[str, Any]:
        """Get the default parameters for calling OpenAI API."""
        set_model_value = self.model
        if self.model_name is not None:
            set_model_value = self.model_name
        return {
            "model": set_model_value,
            "force_timeout": self.request_timeout,
            "max_tokens": self.max_tokens,
            "stream": self.streaming,
            "n": self.n,
            "temperature": self.temperature,
            **self.model_kwargs,
        }

    @property
    def _client_params(self) -> Dict[str, Any]:
        """Get the parameters used for the openai client."""
        set_model_value = self.model
        if self.model_name is not None:
            set_model_value = self.model_name
        self.client.api_base = self.api_base
        self.client.organization = self.organization
        creds: Dict[str, Any] = {
            "model": set_model_value,
            "force_timeout": self.request_timeout,
        }
        return {**self._default_params, **creds}

    def completion_with_retry(
        self, run_manager: Optional[CallbackManagerForLLMRun] = None, **kwargs: Any
    ) -> Any:
        """Use tenacity to retry the completion call."""
        retry_decorator = _create_retry_decorator(self, run_manager=run_manager)

        @retry_decorator
        def _completion_with_retry(**kwargs: Any) -> Any:
            return self.client.completion(**kwargs)

        return _completion_with_retry(**kwargs)

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate api key, python package exists, temperature, top_p, and top_k."""
        try:
            import litellm
        except ImportError:
            raise ChatLiteLLMException(
                "Could not import google.generativeai python package. "
                "Please install it with `pip install google-generativeai`"
            )

        values["openai_api_key"] = get_from_dict_or_env(
            values, "openai_api_key", "OPENAI_API_KEY", default=""
        )
        values["azure_api_key"] = get_from_dict_or_env(
            values, "azure_api_key", "AZURE_API_KEY", default=""
        )
        values["anthropic_api_key"] = get_from_dict_or_env(
            values, "anthropic_api_key", "ANTHROPIC_API_KEY", default=""
        )
        values["replicate_api_key"] = get_from_dict_or_env(
            values, "replicate_api_key", "REPLICATE_API_KEY", default=""
        )
        values["openrouter_api_key"] = get_from_dict_or_env(
            values, "openrouter_api_key", "OPENROUTER_API_KEY", default=""
        )
        values["client"] = litellm

        if values["temperature"] is not None and not 0 <= values["temperature"] <= 1:
            raise ValueError("temperature must be in the range [0.0, 1.0]")

        if values["top_p"] is not None and not 0 <= values["top_p"] <= 1:
            raise ValueError("top_p must be in the range [0.0, 1.0]")

        if values["top_k"] is not None and values["top_k"] <= 0:
            raise ValueError("top_k must be positive")

        return values

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        stream: Optional[bool] = None,
        **kwargs: Any,
    ) -> ChatResult:
        if stream if stream is not None else self.streaming:
            generation: Optional[ChatGenerationChunk] = None
            for chunk in self._stream(
                messages=messages, stop=stop, run_manager=run_manager, **kwargs
            ):
                if generation is None:
                    generation = chunk
                else:
                    generation += chunk
            assert generation is not None
            return ChatResult(generations=[generation])

        message_dicts, params = self._create_message_dicts(messages, stop)
        params = {**params, **kwargs}
        response = self.completion_with_retry(
            messages=message_dicts, run_manager=run_manager, **params
        )
        return self._create_chat_result(response)

    def _create_chat_result(self, response: Mapping[str, Any]) -> ChatResult:
        generations = []
        for res in response["choices"]:
            message = _convert_dict_to_message(res["message"])
            gen = ChatGeneration(
                message=message,
                generation_info=dict(finish_reason=res.get("finish_reason")),
            )
            generations.append(gen)
        token_usage = response.get("usage", {})
        set_model_value = self.model
        if self.model_name is not None:
            set_model_value = self.model_name
        llm_output = {"token_usage": token_usage, "model": set_model_value}
        return ChatResult(generations=generations, llm_output=llm_output)

    def _create_message_dicts(
        self, messages: List[BaseMessage], stop: Optional[List[str]]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        params = self._client_params
        if stop is not None:
            if "stop" in params:
                raise ValueError("`stop` found in both the input and default params.")
            params["stop"] = stop
        message_dicts = [_convert_message_to_dict(m) for m in messages]
        return message_dicts, params

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        message_dicts, params = self._create_message_dicts(messages, stop)
        params = {**params, **kwargs, "stream": True}

        default_chunk_class = AIMessageChunk
        for chunk in self.completion_with_retry(
            messages=message_dicts, run_manager=run_manager, **params
        ):
            if len(chunk["choices"]) == 0:
                continue
            delta = chunk["choices"][0]["delta"]
            chunk = _convert_delta_to_message_chunk(delta, default_chunk_class)
            default_chunk_class = chunk.__class__
            yield ChatGenerationChunk(message=chunk)
            if run_manager:
                run_manager.on_llm_new_token(chunk.content)

    async def _astream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> AsyncIterator[ChatGenerationChunk]:
        message_dicts, params = self._create_message_dicts(messages, stop)
        params = {**params, **kwargs, "stream": True}

        default_chunk_class = AIMessageChunk
        async for chunk in await acompletion_with_retry(
            self, messages=message_dicts, run_manager=run_manager, **params
        ):
            if len(chunk["choices"]) == 0:
                continue
            delta = chunk["choices"][0]["delta"]
            chunk = _convert_delta_to_message_chunk(delta, default_chunk_class)
            default_chunk_class = chunk.__class__
            yield ChatGenerationChunk(message=chunk)
            if run_manager:
                await run_manager.on_llm_new_token(chunk.content)

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        stream: Optional[bool] = None,
        **kwargs: Any,
    ) -> ChatResult:
        if stream if stream is not None else self.streaming:
            generation: Optional[ChatGenerationChunk] = None
            async for chunk in self._astream(
                messages=messages, stop=stop, run_manager=run_manager, **kwargs
            ):
                if generation is None:
                    generation = chunk
                else:
                    generation += chunk
            assert generation is not None
            return ChatResult(generations=[generation])

        message_dicts, params = self._create_message_dicts(messages, stop)
        params = {**params, **kwargs}
        response = await acompletion_with_retry(
            self, messages=message_dicts, run_manager=run_manager, **params
        )
        return self._create_chat_result(response)

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Get the identifying parameters."""
        set_model_value = self.model
        if self.model_name is not None:
            set_model_value = self.model_name
        return {
            "model": set_model_value,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "n": self.n,
        }

    @property
    def _llm_type(self) -> str:
        return "litellm-chat"
