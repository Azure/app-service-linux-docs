# flake8: noqa
"""Load tools."""
import warnings
from typing import Any, Dict, List, Optional, Callable, Tuple
from mypy_extensions import Arg, KwArg

from langchain.agents.tools import Tool
from langchain.schema.language_model import BaseLanguageModel
from langchain.callbacks.base import BaseCallbackManager
from langchain.callbacks.manager import Callbacks
from langchain.chains.api import news_docs, open_meteo_docs, podcast_docs, tmdb_docs
from langchain.chains.api.base import APIChain
from langchain.chains.llm_math.base import LLMMathChain
from langchain.utilities.dalle_image_generator import DallEAPIWrapper
from langchain.utilities.requests import TextRequestsWrapper
from langchain.tools.arxiv.tool import ArxivQueryRun
from langchain.tools.golden_query.tool import GoldenQueryRun
from langchain.tools.pubmed.tool import PubmedQueryRun
from langchain.tools.base import BaseTool
from langchain.tools.bing_search.tool import BingSearchRun
from langchain.tools.ddg_search.tool import DuckDuckGoSearchRun
from langchain.tools.google_search.tool import GoogleSearchResults, GoogleSearchRun
from langchain.tools.metaphor_search.tool import MetaphorSearchResults
from langchain.tools.google_serper.tool import GoogleSerperResults, GoogleSerperRun
from langchain.tools.graphql.tool import BaseGraphQLTool
from langchain.tools.human.tool import HumanInputRun
from langchain.tools.python.tool import PythonREPLTool
from langchain.tools.requests.tool import (
    RequestsDeleteTool,
    RequestsGetTool,
    RequestsPatchTool,
    RequestsPostTool,
    RequestsPutTool,
)
from langchain.tools.scenexplain.tool import SceneXplainTool
from langchain.tools.searx_search.tool import SearxSearchResults, SearxSearchRun
from langchain.tools.shell.tool import ShellTool
from langchain.tools.sleep.tool import SleepTool
from langchain.tools.wikipedia.tool import WikipediaQueryRun
from langchain.tools.wolfram_alpha.tool import WolframAlphaQueryRun
from langchain.tools.openweathermap.tool import OpenWeatherMapQueryRun
from langchain.tools.dataforseo_api_search import DataForSeoAPISearchRun
from langchain.tools.dataforseo_api_search import DataForSeoAPISearchResults
from langchain.utilities import ArxivAPIWrapper
from langchain.utilities import GoldenQueryAPIWrapper
from langchain.utilities import PubMedAPIWrapper
from langchain.utilities.bing_search import BingSearchAPIWrapper
from langchain.utilities.duckduckgo_search import DuckDuckGoSearchAPIWrapper
from langchain.utilities.google_search import GoogleSearchAPIWrapper
from langchain.utilities.google_serper import GoogleSerperAPIWrapper
from langchain.utilities.metaphor_search import MetaphorSearchAPIWrapper
from langchain.utilities.awslambda import LambdaWrapper
from langchain.utilities.graphql import GraphQLAPIWrapper
from langchain.utilities.searx_search import SearxSearchWrapper
from langchain.utilities.serpapi import SerpAPIWrapper
from langchain.utilities.twilio import TwilioAPIWrapper
from langchain.utilities.wikipedia import WikipediaAPIWrapper
from langchain.utilities.wolfram_alpha import WolframAlphaAPIWrapper
from langchain.utilities.openweathermap import OpenWeatherMapAPIWrapper
from langchain.utilities.dataforseo_api_search import DataForSeoAPIWrapper


def _get_python_repl() -> BaseTool:
    return PythonREPLTool()


def _get_tools_requests_get() -> BaseTool:
    return RequestsGetTool(requests_wrapper=TextRequestsWrapper())


def _get_tools_requests_post() -> BaseTool:
    return RequestsPostTool(requests_wrapper=TextRequestsWrapper())


def _get_tools_requests_patch() -> BaseTool:
    return RequestsPatchTool(requests_wrapper=TextRequestsWrapper())


def _get_tools_requests_put() -> BaseTool:
    return RequestsPutTool(requests_wrapper=TextRequestsWrapper())


def _get_tools_requests_delete() -> BaseTool:
    return RequestsDeleteTool(requests_wrapper=TextRequestsWrapper())


def _get_terminal() -> BaseTool:
    return ShellTool()


def _get_sleep() -> BaseTool:
    return SleepTool()


_BASE_TOOLS: Dict[str, Callable[[], BaseTool]] = {
    "python_repl": _get_python_repl,
    "requests": _get_tools_requests_get,  # preserved for backwards compatibility
    "requests_get": _get_tools_requests_get,
    "requests_post": _get_tools_requests_post,
    "requests_patch": _get_tools_requests_patch,
    "requests_put": _get_tools_requests_put,
    "requests_delete": _get_tools_requests_delete,
    "terminal": _get_terminal,
    "sleep": _get_sleep,
}


def _get_llm_math(llm: BaseLanguageModel) -> BaseTool:
    return Tool(
        name="Calculator",
        description="Useful for when you need to answer questions about math.",
        func=LLMMathChain.from_llm(llm=llm).run,
        coroutine=LLMMathChain.from_llm(llm=llm).arun,
    )


def _get_open_meteo_api(llm: BaseLanguageModel) -> BaseTool:
    chain = APIChain.from_llm_and_api_docs(llm, open_meteo_docs.OPEN_METEO_DOCS)
    return Tool(
        name="Open Meteo API",
        description="Useful for when you want to get weather information from the OpenMeteo API. The input should be a question in natural language that this API can answer.",
        func=chain.run,
    )


_LLM_TOOLS: Dict[str, Callable[[BaseLanguageModel], BaseTool]] = {
    "llm-math": _get_llm_math,
    "open-meteo-api": _get_open_meteo_api,
}


def _get_news_api(llm: BaseLanguageModel, **kwargs: Any) -> BaseTool:
    news_api_key = kwargs["news_api_key"]
    chain = APIChain.from_llm_and_api_docs(
        llm, news_docs.NEWS_DOCS, headers={"X-Api-Key": news_api_key}
    )
    return Tool(
        name="News API",
        description="Use this when you want to get information about the top headlines of current news stories. The input should be a question in natural language that this API can answer.",
        func=chain.run,
    )


def _get_tmdb_api(llm: BaseLanguageModel, **kwargs: Any) -> BaseTool:
    tmdb_bearer_token = kwargs["tmdb_bearer_token"]
    chain = APIChain.from_llm_and_api_docs(
        llm,
        tmdb_docs.TMDB_DOCS,
        headers={"Authorization": f"Bearer {tmdb_bearer_token}"},
    )
    return Tool(
        name="TMDB API",
        description="Useful for when you want to get information from The Movie Database. The input should be a question in natural language that this API can answer.",
        func=chain.run,
    )


def _get_podcast_api(llm: BaseLanguageModel, **kwargs: Any) -> BaseTool:
    listen_api_key = kwargs["listen_api_key"]
    chain = APIChain.from_llm_and_api_docs(
        llm,
        podcast_docs.PODCAST_DOCS,
        headers={"X-ListenAPI-Key": listen_api_key},
    )
    return Tool(
        name="Podcast API",
        description="Use the Listen Notes Podcast API to search all podcasts or episodes. The input should be a question in natural language that this API can answer.",
        func=chain.run,
    )


def _get_lambda_api(**kwargs: Any) -> BaseTool:
    return Tool(
        name=kwargs["awslambda_tool_name"],
        description=kwargs["awslambda_tool_description"],
        func=LambdaWrapper(**kwargs).run,
    )


def _get_wolfram_alpha(**kwargs: Any) -> BaseTool:
    return WolframAlphaQueryRun(api_wrapper=WolframAlphaAPIWrapper(**kwargs))


def _get_google_search(**kwargs: Any) -> BaseTool:
    return GoogleSearchRun(api_wrapper=GoogleSearchAPIWrapper(**kwargs))


def _get_wikipedia(**kwargs: Any) -> BaseTool:
    return WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(**kwargs))


def _get_arxiv(**kwargs: Any) -> BaseTool:
    return ArxivQueryRun(api_wrapper=ArxivAPIWrapper(**kwargs))


def _get_golden_query(**kwargs: Any) -> BaseTool:
    return GoldenQueryRun(api_wrapper=GoldenQueryAPIWrapper(**kwargs))


def _get_pubmed(**kwargs: Any) -> BaseTool:
    return PubmedQueryRun(api_wrapper=PubMedAPIWrapper(**kwargs))


def _get_google_serper(**kwargs: Any) -> BaseTool:
    return GoogleSerperRun(api_wrapper=GoogleSerperAPIWrapper(**kwargs))


def _get_google_serper_results_json(**kwargs: Any) -> BaseTool:
    return GoogleSerperResults(api_wrapper=GoogleSerperAPIWrapper(**kwargs))


def _get_google_search_results_json(**kwargs: Any) -> BaseTool:
    return GoogleSearchResults(api_wrapper=GoogleSearchAPIWrapper(**kwargs))


def _get_serpapi(**kwargs: Any) -> BaseTool:
    return Tool(
        name="Search",
        description="A search engine. Useful for when you need to answer questions about current events. Input should be a search query.",
        func=SerpAPIWrapper(**kwargs).run,
        coroutine=SerpAPIWrapper(**kwargs).arun,
    )


def _get_dalle_image_generator(**kwargs: Any) -> Tool:
    return Tool(
        "Dall-E Image Generator",
        DallEAPIWrapper(**kwargs).run,
        "A wrapper around OpenAI DALL-E API. Useful for when you need to generate images from a text description. Input should be an image description.",
    )


def _get_twilio(**kwargs: Any) -> BaseTool:
    return Tool(
        name="Text Message",
        description="Useful for when you need to send a text message to a provided phone number.",
        func=TwilioAPIWrapper(**kwargs).run,
    )


def _get_searx_search(**kwargs: Any) -> BaseTool:
    return SearxSearchRun(wrapper=SearxSearchWrapper(**kwargs))


def _get_searx_search_results_json(**kwargs: Any) -> BaseTool:
    wrapper_kwargs = {k: v for k, v in kwargs.items() if k != "num_results"}
    return SearxSearchResults(wrapper=SearxSearchWrapper(**wrapper_kwargs), **kwargs)


def _get_bing_search(**kwargs: Any) -> BaseTool:
    return BingSearchRun(api_wrapper=BingSearchAPIWrapper(**kwargs))


def _get_metaphor_search(**kwargs: Any) -> BaseTool:
    return MetaphorSearchResults(api_wrapper=MetaphorSearchAPIWrapper(**kwargs))


def _get_ddg_search(**kwargs: Any) -> BaseTool:
    return DuckDuckGoSearchRun(api_wrapper=DuckDuckGoSearchAPIWrapper(**kwargs))


def _get_human_tool(**kwargs: Any) -> BaseTool:
    return HumanInputRun(**kwargs)


def _get_scenexplain(**kwargs: Any) -> BaseTool:
    return SceneXplainTool(**kwargs)


def _get_graphql_tool(**kwargs: Any) -> BaseTool:
    graphql_endpoint = kwargs["graphql_endpoint"]
    wrapper = GraphQLAPIWrapper(graphql_endpoint=graphql_endpoint)
    return BaseGraphQLTool(graphql_wrapper=wrapper)


def _get_openweathermap(**kwargs: Any) -> BaseTool:
    return OpenWeatherMapQueryRun(api_wrapper=OpenWeatherMapAPIWrapper(**kwargs))


def _get_dataforseo_api_search(**kwargs: Any) -> BaseTool:
    return DataForSeoAPISearchRun(api_wrapper=DataForSeoAPIWrapper(**kwargs))


def _get_dataforseo_api_search_json(**kwargs: Any) -> BaseTool:
    return DataForSeoAPISearchResults(api_wrapper=DataForSeoAPIWrapper(**kwargs))


_EXTRA_LLM_TOOLS: Dict[
    str,
    Tuple[Callable[[Arg(BaseLanguageModel, "llm"), KwArg(Any)], BaseTool], List[str]],
] = {
    "news-api": (_get_news_api, ["news_api_key"]),
    "tmdb-api": (_get_tmdb_api, ["tmdb_bearer_token"]),
    "podcast-api": (_get_podcast_api, ["listen_api_key"]),
}

_EXTRA_OPTIONAL_TOOLS: Dict[str, Tuple[Callable[[KwArg(Any)], BaseTool], List[str]]] = {
    "wolfram-alpha": (_get_wolfram_alpha, ["wolfram_alpha_appid"]),
    "google-search": (_get_google_search, ["google_api_key", "google_cse_id"]),
    "google-search-results-json": (
        _get_google_search_results_json,
        ["google_api_key", "google_cse_id", "num_results"],
    ),
    "searx-search-results-json": (
        _get_searx_search_results_json,
        ["searx_host", "engines", "num_results", "aiosession"],
    ),
    "bing-search": (_get_bing_search, ["bing_subscription_key", "bing_search_url"]),
    "metaphor-search": (_get_metaphor_search, ["metaphor_api_key"]),
    "ddg-search": (_get_ddg_search, []),
    "google-serper": (_get_google_serper, ["serper_api_key", "aiosession"]),
    "google-serper-results-json": (
        _get_google_serper_results_json,
        ["serper_api_key", "aiosession"],
    ),
    "serpapi": (_get_serpapi, ["serpapi_api_key", "aiosession"]),
    "dalle-image-generator": (_get_dalle_image_generator, ["openai_api_key"]),
    "twilio": (_get_twilio, ["account_sid", "auth_token", "from_number"]),
    "searx-search": (_get_searx_search, ["searx_host", "engines", "aiosession"]),
    "wikipedia": (_get_wikipedia, ["top_k_results", "lang"]),
    "arxiv": (
        _get_arxiv,
        ["top_k_results", "load_max_docs", "load_all_available_meta"],
    ),
    "golden-query": (_get_golden_query, ["golden_api_key"]),
    "pubmed": (_get_pubmed, ["top_k_results"]),
    "human": (_get_human_tool, ["prompt_func", "input_func"]),
    "awslambda": (
        _get_lambda_api,
        ["awslambda_tool_name", "awslambda_tool_description", "function_name"],
    ),
    "sceneXplain": (_get_scenexplain, []),
    "graphql": (_get_graphql_tool, ["graphql_endpoint"]),
    "openweathermap-api": (_get_openweathermap, ["openweathermap_api_key"]),
    "dataforseo-api-search": (
        _get_dataforseo_api_search,
        ["api_login", "api_password", "aiosession"],
    ),
    "dataforseo-api-search-json": (
        _get_dataforseo_api_search_json,
        ["api_login", "api_password", "aiosession"],
    ),
}


def _handle_callbacks(
    callback_manager: Optional[BaseCallbackManager], callbacks: Callbacks
) -> Callbacks:
    if callback_manager is not None:
        warnings.warn(
            "callback_manager is deprecated. Please use callbacks instead.",
            DeprecationWarning,
        )
        if callbacks is not None:
            raise ValueError(
                "Cannot specify both callback_manager and callbacks arguments."
            )
        return callback_manager
    return callbacks


def load_huggingface_tool(
    task_or_repo_id: str,
    model_repo_id: Optional[str] = None,
    token: Optional[str] = None,
    remote: bool = False,
    **kwargs: Any,
) -> BaseTool:
    """Loads a tool from the HuggingFace Hub.

    Args:
        task_or_repo_id: Task or model repo id.
        model_repo_id: Optional model repo id.
        token: Optional token.
        remote: Optional remote. Defaults to False.
        **kwargs:

    Returns:
        A tool.

    """
    try:
        from transformers import load_tool
    except ImportError:
        raise ImportError(
            "HuggingFace tools require the libraries `transformers>=4.29.0`"
            " and `huggingface_hub>=0.14.1` to be installed."
            " Please install it with"
            " `pip install --upgrade transformers huggingface_hub`."
        )
    hf_tool = load_tool(
        task_or_repo_id,
        model_repo_id=model_repo_id,
        token=token,
        remote=remote,
        **kwargs,
    )
    outputs = hf_tool.outputs
    if set(outputs) != {"text"}:
        raise NotImplementedError("Multimodal outputs not supported yet.")
    inputs = hf_tool.inputs
    if set(inputs) != {"text"}:
        raise NotImplementedError("Multimodal inputs not supported yet.")
    return Tool.from_function(
        hf_tool.__call__, name=hf_tool.name, description=hf_tool.description
    )


def load_tools(
    tool_names: List[str],
    llm: Optional[BaseLanguageModel] = None,
    callbacks: Callbacks = None,
    **kwargs: Any,
) -> List[BaseTool]:
    """Load tools based on their name.

    Args:
        tool_names: name of tools to load.
        llm: An optional language model, may be needed to initialize certain tools.
        callbacks: Optional callback manager or list of callback handlers.
            If not provided, default global callback manager will be used.

    Returns:
        List of tools.
    """
    tools = []
    callbacks = _handle_callbacks(
        callback_manager=kwargs.get("callback_manager"), callbacks=callbacks
    )
    for name in tool_names:
        if name == "requests":
            warnings.warn(
                "tool name `requests` is deprecated - "
                "please use `requests_all` or specify the requests method"
            )

        if name == "requests_all":
            # expand requests into various methods
            requests_method_tools = [
                _tool for _tool in _BASE_TOOLS if _tool.startswith("requests_")
            ]
            tool_names.extend(requests_method_tools)
        elif name in _BASE_TOOLS:
            tools.append(_BASE_TOOLS[name]())
        elif name in _LLM_TOOLS:
            if llm is None:
                raise ValueError(f"Tool {name} requires an LLM to be provided")
            tool = _LLM_TOOLS[name](llm)
            tools.append(tool)
        elif name in _EXTRA_LLM_TOOLS:
            if llm is None:
                raise ValueError(f"Tool {name} requires an LLM to be provided")
            _get_llm_tool_func, extra_keys = _EXTRA_LLM_TOOLS[name]
            missing_keys = set(extra_keys).difference(kwargs)
            if missing_keys:
                raise ValueError(
                    f"Tool {name} requires some parameters that were not "
                    f"provided: {missing_keys}"
                )
            sub_kwargs = {k: kwargs[k] for k in extra_keys}
            tool = _get_llm_tool_func(llm=llm, **sub_kwargs)
            tools.append(tool)
        elif name in _EXTRA_OPTIONAL_TOOLS:
            _get_tool_func, extra_keys = _EXTRA_OPTIONAL_TOOLS[name]
            sub_kwargs = {k: kwargs[k] for k in extra_keys if k in kwargs}
            tool = _get_tool_func(**sub_kwargs)
            tools.append(tool)
        else:
            raise ValueError(f"Got unknown tool {name}")
    if callbacks is not None:
        for tool in tools:
            tool.callbacks = callbacks
    return tools


def get_all_tool_names() -> List[str]:
    """Get a list of all possible tool names."""
    return (
        list(_BASE_TOOLS)
        + list(_EXTRA_OPTIONAL_TOOLS)
        + list(_EXTRA_LLM_TOOLS)
        + list(_LLM_TOOLS)
    )
