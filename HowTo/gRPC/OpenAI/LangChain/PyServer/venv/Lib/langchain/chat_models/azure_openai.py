"""Azure OpenAI chat wrapper."""
from __future__ import annotations

import logging
from typing import Any, Dict, Mapping

from langchain.chat_models.openai import ChatOpenAI
from langchain.pydantic_v1 import root_validator
from langchain.schema import ChatResult
from langchain.utils import get_from_dict_or_env

logger = logging.getLogger(__name__)


class AzureChatOpenAI(ChatOpenAI):
    """`Azure OpenAI` Chat Completion API.

    To use this class you
    must have a deployed model on Azure OpenAI. Use `deployment_name` in the
    constructor to refer to the "Model deployment name" in the Azure portal.

    In addition, you should have the ``openai`` python package installed, and the
    following environment variables set or passed in constructor in lower case:
    - ``OPENAI_API_TYPE`` (default: ``azure``)
    - ``OPENAI_API_KEY``
    - ``OPENAI_API_BASE``
    - ``OPENAI_API_VERSION``
    - ``OPENAI_PROXY``

    For example, if you have `gpt-35-turbo` deployed, with the deployment name
    `35-turbo-dev`, the constructor should look like:

    .. code-block:: python

        AzureChatOpenAI(
            deployment_name="35-turbo-dev",
            openai_api_version="2023-05-15",
        )

    Be aware the API version may change.

    You can also specify the version of the model using ``model_version`` constructor
    parameter, as Azure OpenAI doesn't return model version with the response.

    Default is empty. When you specify the version, it will be appended to the
    model name in the response. Setting correct version will help you to calculate the
    cost properly. Model version is not validated, so make sure you set it correctly
    to get the correct cost.

    Any parameters that are valid to be passed to the openai.create call can be passed
    in, even if not explicitly saved on this class.
    """

    deployment_name: str = ""
    model_version: str = ""
    openai_api_type: str = ""
    openai_api_base: str = ""
    openai_api_version: str = ""
    openai_api_key: str = ""
    openai_organization: str = ""
    openai_proxy: str = ""

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that api key and python package exists in environment."""
        values["openai_api_key"] = get_from_dict_or_env(
            values,
            "openai_api_key",
            "OPENAI_API_KEY",
        )
        values["openai_api_base"] = get_from_dict_or_env(
            values,
            "openai_api_base",
            "OPENAI_API_BASE",
        )
        values["openai_api_version"] = get_from_dict_or_env(
            values,
            "openai_api_version",
            "OPENAI_API_VERSION",
        )
        values["openai_api_type"] = get_from_dict_or_env(
            values, "openai_api_type", "OPENAI_API_TYPE", default="azure"
        )
        values["openai_organization"] = get_from_dict_or_env(
            values,
            "openai_organization",
            "OPENAI_ORGANIZATION",
            default="",
        )
        values["openai_proxy"] = get_from_dict_or_env(
            values,
            "openai_proxy",
            "OPENAI_PROXY",
            default="",
        )
        try:
            import openai

        except ImportError:
            raise ImportError(
                "Could not import openai python package. "
                "Please install it with `pip install openai`."
            )
        try:
            values["client"] = openai.ChatCompletion
        except AttributeError:
            raise ValueError(
                "`openai` has no `ChatCompletion` attribute, this is likely "
                "due to an old version of the openai package. Try upgrading it "
                "with `pip install --upgrade openai`."
            )
        if values["n"] < 1:
            raise ValueError("n must be at least 1.")
        if values["n"] > 1 and values["streaming"]:
            raise ValueError("n must be 1 when streaming.")
        return values

    @property
    def _default_params(self) -> Dict[str, Any]:
        """Get the default parameters for calling OpenAI API."""
        return {
            **super()._default_params,
            "engine": self.deployment_name,
        }

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Get the identifying parameters."""
        return {**self._default_params}

    @property
    def _client_params(self) -> Dict[str, Any]:
        """Get the config params used for the openai client."""
        return {
            **super()._client_params,
            "api_type": self.openai_api_type,
            "api_version": self.openai_api_version,
        }

    @property
    def _llm_type(self) -> str:
        return "azure-openai-chat"

    def _create_chat_result(self, response: Mapping[str, Any]) -> ChatResult:
        for res in response["choices"]:
            if res.get("finish_reason", None) == "content_filter":
                raise ValueError(
                    "Azure has not provided the response due to a content filter "
                    "being triggered"
                )
        chat_result = super()._create_chat_result(response)

        if "model" in response:
            model = response["model"]
            if self.model_version:
                model = f"{model}-{self.model_version}"

            if chat_result.llm_output is not None and isinstance(
                chat_result.llm_output, dict
            ):
                chat_result.llm_output["model_name"] = model

        return chat_result
