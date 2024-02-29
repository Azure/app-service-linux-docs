"""Power BI agent."""
from typing import Any, Dict, List, Optional

from langchain.agents import AgentExecutor
from langchain.agents.agent_toolkits.powerbi.prompt import (
    POWERBI_PREFIX,
    POWERBI_SUFFIX,
)
from langchain.agents.agent_toolkits.powerbi.toolkit import PowerBIToolkit
from langchain.agents.mrkl.base import ZeroShotAgent
from langchain.agents.mrkl.prompt import FORMAT_INSTRUCTIONS
from langchain.callbacks.base import BaseCallbackManager
from langchain.chains.llm import LLMChain
from langchain.schema.language_model import BaseLanguageModel
from langchain.utilities.powerbi import PowerBIDataset


def create_pbi_agent(
    llm: BaseLanguageModel,
    toolkit: Optional[PowerBIToolkit] = None,
    powerbi: Optional[PowerBIDataset] = None,
    callback_manager: Optional[BaseCallbackManager] = None,
    prefix: str = POWERBI_PREFIX,
    suffix: str = POWERBI_SUFFIX,
    format_instructions: str = FORMAT_INSTRUCTIONS,
    examples: Optional[str] = None,
    input_variables: Optional[List[str]] = None,
    top_k: int = 10,
    verbose: bool = False,
    agent_executor_kwargs: Optional[Dict[str, Any]] = None,
    **kwargs: Dict[str, Any],
) -> AgentExecutor:
    """Construct a Power BI agent from an LLM and tools."""
    if toolkit is None:
        if powerbi is None:
            raise ValueError("Must provide either a toolkit or powerbi dataset")
        toolkit = PowerBIToolkit(powerbi=powerbi, llm=llm, examples=examples)
    tools = toolkit.get_tools()
    tables = powerbi.table_names if powerbi else toolkit.powerbi.table_names
    agent = ZeroShotAgent(
        llm_chain=LLMChain(
            llm=llm,
            prompt=ZeroShotAgent.create_prompt(
                tools,
                prefix=prefix.format(top_k=top_k).format(tables=tables),
                suffix=suffix,
                format_instructions=format_instructions,
                input_variables=input_variables,
            ),
            callback_manager=callback_manager,  # type: ignore
            verbose=verbose,
        ),
        allowed_tools=[tool.name for tool in tools],
        **kwargs,
    )
    return AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        callback_manager=callback_manager,
        verbose=verbose,
        **(agent_executor_kwargs or {}),
    )
