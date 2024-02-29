"""LLM Chain for generating examples for question answering."""
from __future__ import annotations

from typing import Any

from langchain.chains.llm import LLMChain
from langchain.evaluation.qa.generate_prompt import PROMPT
from langchain.output_parsers.regex import RegexParser
from langchain.pydantic_v1 import Field
from langchain.schema.language_model import BaseLanguageModel
from langchain.schema.output_parser import BaseLLMOutputParser

_QA_OUTPUT_PARSER = RegexParser(
    regex=r"QUESTION: (.*?)\n+ANSWER: (.*)", output_keys=["query", "answer"]
)


class QAGenerateChain(LLMChain):
    """LLM Chain for generating examples for question answering."""

    output_parser: BaseLLMOutputParser = Field(default=_QA_OUTPUT_PARSER)
    output_key: str = "qa_pairs"

    @classmethod
    def from_llm(cls, llm: BaseLanguageModel, **kwargs: Any) -> QAGenerateChain:
        """Load QA Generate Chain from LLM."""
        return cls(llm=llm, prompt=PROMPT, **kwargs)
