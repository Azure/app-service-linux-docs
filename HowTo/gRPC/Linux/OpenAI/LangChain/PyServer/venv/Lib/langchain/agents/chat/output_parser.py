import json
import re
from typing import Union

from langchain.agents.agent import AgentOutputParser
from langchain.agents.chat.prompt import FORMAT_INSTRUCTIONS
from langchain.schema import AgentAction, AgentFinish, OutputParserException

FINAL_ANSWER_ACTION = "Final Answer:"


class ChatOutputParser(AgentOutputParser):
    """Output parser for the chat agent."""

    pattern = re.compile(r"^.*?`{3}(?:json)?\n(.*?)`{3}.*?$", re.DOTALL)
    """Regex pattern to parse the output."""

    def get_format_instructions(self) -> str:
        return FORMAT_INSTRUCTIONS

    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        includes_answer = FINAL_ANSWER_ACTION in text
        try:
            found = self.pattern.search(text)
            if not found:
                # Fast fail to parse Final Answer.
                raise ValueError("action not found")
            action = found.group(1)
            response = json.loads(action.strip())
            includes_action = "action" in response
            if includes_answer and includes_action:
                raise OutputParserException(
                    "Parsing LLM output produced a final answer "
                    f"and a parse-able action: {text}"
                )
            return AgentAction(
                response["action"], response.get("action_input", {}), text
            )

        except Exception:
            if not includes_answer:
                raise OutputParserException(f"Could not parse LLM output: {text}")
            output = text.split(FINAL_ANSWER_ACTION)[-1].strip()
            return AgentFinish({"output": output}, text)

    @property
    def _type(self) -> str:
        return "chat"
