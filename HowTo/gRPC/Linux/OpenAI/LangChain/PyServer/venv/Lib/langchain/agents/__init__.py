"""
**Agent** is a class that uses an LLM to choose a sequence of actions to take.

In Chains, a sequence of actions is hardcoded. In Agents,
a language model is used as a reasoning engine to determine which actions
to take and in which order.

Agents select and use **Tools** and **Toolkits** for actions.

**Class hierarchy:**

.. code-block::

    BaseSingleActionAgent --> LLMSingleActionAgent
                              OpenAIFunctionsAgent
                              XMLAgent
                              Agent --> <name>Agent  # Examples: ZeroShotAgent, ChatAgent
                                        

    BaseMultiActionAgent  --> OpenAIMultiFunctionsAgent
    
    
**Main helpers:**

.. code-block::

    AgentType, AgentExecutor, AgentOutputParser, AgentExecutorIterator,
    AgentAction, AgentFinish
    
"""  # noqa: E501
from langchain.agents.agent import (
    Agent,
    AgentExecutor,
    AgentOutputParser,
    BaseMultiActionAgent,
    BaseSingleActionAgent,
    LLMSingleActionAgent,
)
from langchain.agents.agent_iterator import AgentExecutorIterator
from langchain.agents.agent_toolkits import (
    create_csv_agent,
    create_json_agent,
    create_openapi_agent,
    create_pandas_dataframe_agent,
    create_pbi_agent,
    create_pbi_chat_agent,
    create_spark_dataframe_agent,
    create_spark_sql_agent,
    create_sql_agent,
    create_vectorstore_agent,
    create_vectorstore_router_agent,
    create_xorbits_agent,
)
from langchain.agents.agent_types import AgentType
from langchain.agents.conversational.base import ConversationalAgent
from langchain.agents.conversational_chat.base import ConversationalChatAgent
from langchain.agents.initialize import initialize_agent
from langchain.agents.load_tools import (
    get_all_tool_names,
    load_huggingface_tool,
    load_tools,
)
from langchain.agents.loading import load_agent
from langchain.agents.mrkl.base import MRKLChain, ZeroShotAgent
from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent
from langchain.agents.openai_functions_multi_agent.base import OpenAIMultiFunctionsAgent
from langchain.agents.react.base import ReActChain, ReActTextWorldAgent
from langchain.agents.self_ask_with_search.base import SelfAskWithSearchChain
from langchain.agents.structured_chat.base import StructuredChatAgent
from langchain.agents.tools import Tool, tool
from langchain.agents.xml.base import XMLAgent

__all__ = [
    "Agent",
    "AgentExecutor",
    "AgentExecutorIterator",
    "AgentOutputParser",
    "AgentType",
    "BaseMultiActionAgent",
    "BaseSingleActionAgent",
    "ConversationalAgent",
    "ConversationalChatAgent",
    "LLMSingleActionAgent",
    "MRKLChain",
    "OpenAIFunctionsAgent",
    "OpenAIMultiFunctionsAgent",
    "ReActChain",
    "ReActTextWorldAgent",
    "SelfAskWithSearchChain",
    "StructuredChatAgent",
    "Tool",
    "ZeroShotAgent",
    "create_csv_agent",
    "create_json_agent",
    "create_openapi_agent",
    "create_pandas_dataframe_agent",
    "create_pbi_agent",
    "create_pbi_chat_agent",
    "create_spark_dataframe_agent",
    "create_spark_sql_agent",
    "create_sql_agent",
    "create_vectorstore_agent",
    "create_vectorstore_router_agent",
    "get_all_tool_names",
    "initialize_agent",
    "load_agent",
    "load_huggingface_tool",
    "load_tools",
    "tool",
    "create_xorbits_agent",
    "XMLAgent",
]
