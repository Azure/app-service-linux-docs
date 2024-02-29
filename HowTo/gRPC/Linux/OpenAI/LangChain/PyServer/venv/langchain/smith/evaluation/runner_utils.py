"""Utilities for running language models or Chains over datasets."""

from __future__ import annotations

import asyncio
import functools
import inspect
import itertools
import logging
import uuid
import warnings
from enum import Enum
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Coroutine,
    Dict,
    Iterator,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
    cast,
)
from urllib.parse import urlparse, urlunparse

from langsmith import Client, RunEvaluator
from langsmith.schemas import Dataset, DataType, Example

from langchain.callbacks.base import BaseCallbackHandler
from langchain.callbacks.manager import Callbacks
from langchain.callbacks.tracers.base import BaseTracer
from langchain.callbacks.tracers.evaluation import EvaluatorCallbackHandler
from langchain.callbacks.tracers.langchain import LangChainTracer
from langchain.chains.base import Chain
from langchain.chat_models.openai import ChatOpenAI
from langchain.evaluation.loading import load_evaluator
from langchain.evaluation.schema import EvaluatorType, StringEvaluator
from langchain.schema import ChatResult, LLMResult
from langchain.schema.language_model import BaseLanguageModel
from langchain.schema.messages import BaseMessage, messages_from_dict
from langchain.schema.runnable import Runnable, RunnableConfig, RunnableLambda
from langchain.smith.evaluation.config import EvalConfig, RunEvalConfig
from langchain.smith.evaluation.string_run_evaluator import StringRunEvaluatorChain

if TYPE_CHECKING:
    import pandas as pd

logger = logging.getLogger(__name__)

MODEL_OR_CHAIN_FACTORY = Union[
    Callable[[], Union[Chain, Runnable]],
    BaseLanguageModel,
    Callable[[dict], Any],
    Runnable,
    Chain,
]
MCF = Union[Callable[[], Union[Chain, Runnable]], BaseLanguageModel]


class InputFormatError(Exception):
    """Raised when the input format is invalid."""


## Shared Utilities


class TestResult(dict):
    """A dictionary of the results of a single test run."""

    def to_dataframe(self) -> pd.DataFrame:
        """Convert the results to a dataframe."""
        try:
            import pandas as pd
        except ImportError as e:
            raise ImportError(
                "Pandas is required to convert the results to a dataframe."
                " to install pandas, run `pip install pandas`."
            ) from e

        indices = []
        records = []
        for example_id, result in self["results"].items():
            feedback = result["feedback"]
            records.append(
                {**{f.key: f.score for f in feedback}, "output": result["output"]}
            )
            indices.append(example_id)

        return pd.DataFrame(records, index=indices)


def _get_eval_project_url(api_url: str, project_id: str) -> str:
    """Get the project url from the api url."""
    parsed = urlparse(api_url)
    hostname = parsed.hostname or ""
    if "api." in hostname:
        hostname = hostname.replace("api.", "", 1)
    if "localhost" in hostname:
        # Remove the port
        hostname = "localhost"
    url = urlunparse(parsed._replace(netloc=hostname))
    return f"{url}/projects/p/{project_id}?eval=true"


def _wrap_in_chain_factory(
    llm_or_chain_factory: MODEL_OR_CHAIN_FACTORY,
    dataset_name: str = "<my_dataset>",
) -> MCF:
    """Forgive the user if they pass in a chain without memory instead of a chain
    factory. It's a common mistake. Raise a more helpful error message as well."""
    if isinstance(llm_or_chain_factory, Chain):
        chain = llm_or_chain_factory
        chain_class = chain.__class__.__name__
        if llm_or_chain_factory.memory is not None:
            memory_class = chain.memory.__class__.__name__
            raise ValueError(
                "Cannot directly evaluate a chain with stateful memory."
                " To evaluate this chain, pass in a chain constructor"
                " that initializes fresh memory each time it is called."
                "  This will safegaurd against information"
                " leakage between dataset examples."
                "\nFor example:\n\n"
                "def chain_constructor():\n"
                f"    new_memory = {memory_class}(...)\n"
                f"    return {chain_class}"
                "(memory=new_memory, ...)\n\n"
                f'run_on_dataset("{dataset_name}", chain_constructor, ...)'
            )
        logger.warning(
            "Directly passing in a chain is not recommended as chains may have state."
            " This can lead to unexpected behavior as the "
            "same chain instance could be used across multiple datasets. Instead,"
            " please pass a chain constructor that creates a new "
            "chain with fresh memory each time it is called. This will safeguard"
            " against information leakage between dataset examples. "
            "\nFor example:\n\n"
            "def chain_constructor():\n"
            f"    return {chain_class}(memory=new_memory, ...)\n\n"
            f'run_on_dataset("{dataset_name}", chain_constructor, ...)'
        )

        return lambda: chain
    elif isinstance(llm_or_chain_factory, BaseLanguageModel):
        return llm_or_chain_factory
    elif isinstance(llm_or_chain_factory, Runnable):
        # Memory may exist here, but it's not elegant to check all those cases.
        lcf = llm_or_chain_factory
        return lambda: lcf
    elif callable(llm_or_chain_factory):
        try:
            _model = llm_or_chain_factory()  # type: ignore[call-arg]
        except TypeError:
            # It's an arbitrary function, wrap it in a RunnableLambda
            user_func = cast(Callable, llm_or_chain_factory)
            sig = inspect.signature(user_func)
            logger.info(f"Wrapping function {sig} as RunnableLambda.")
            wrapped = RunnableLambda(user_func)
            return lambda: wrapped
        constructor = cast(Callable, llm_or_chain_factory)
        if isinstance(_model, BaseLanguageModel):
            # It's not uncommon to do an LLM constructor instead of raw LLM,
            # so we'll unpack it for the user.
            return _model
        elif not isinstance(_model, Runnable):
            # This is unlikely to happen - a constructor for a model function
            return lambda: RunnableLambda(constructor)
        else:
            # Typical correct case
            return constructor  # noqa
    return llm_or_chain_factory


def _first_example(examples: Iterator[Example]) -> Tuple[Example, Iterator[Example]]:
    """Get the first example while chaining it back and preserving the iterator."""
    try:
        example: Example = next(examples)
    except StopIteration:
        raise ValueError("No examples provided.")
    return example, itertools.chain([example], examples)


def _get_prompt(inputs: Dict[str, Any]) -> str:
    """Get prompt from inputs.

    Args:
        inputs: The input dictionary.

    Returns:
        A string prompt.
    Raises:
        InputFormatError: If the input format is invalid.
    """
    if not inputs:
        raise InputFormatError("Inputs should not be empty.")

    prompts = []
    if "prompt" in inputs:
        if not isinstance(inputs["prompt"], str):
            raise InputFormatError(
                "Expected string for 'prompt', got"
                f" {type(inputs['prompt']).__name__}"
            )
        prompts = [inputs["prompt"]]
    elif "prompts" in inputs:
        if not isinstance(inputs["prompts"], list) or not all(
            isinstance(i, str) for i in inputs["prompts"]
        ):
            raise InputFormatError(
                "Expected list of strings for 'prompts',"
                f" got {type(inputs['prompts']).__name__}"
            )
        prompts = inputs["prompts"]
    elif len(inputs) == 1:
        prompt_ = next(iter(inputs.values()))
        if isinstance(prompt_, str):
            prompts = [prompt_]
        elif isinstance(prompt_, list) and all(isinstance(i, str) for i in prompt_):
            prompts = prompt_
        else:
            raise InputFormatError(f"LLM Run expects string prompt input. Got {inputs}")
    else:
        raise InputFormatError(
            f"LLM Run expects 'prompt' or 'prompts' in inputs. Got {inputs}"
        )
    if len(prompts) == 1:
        return prompts[0]
    else:
        raise InputFormatError(
            f"LLM Run expects single prompt input. Got {len(prompts)} prompts."
        )


def _get_messages(inputs: Dict[str, Any]) -> List[BaseMessage]:
    """Get Chat Messages from inputs.

    Args:
        inputs: The input dictionary.

    Returns:
        A list of chat messages.
    Raises:
        InputFormatError: If the input format is invalid.
    """
    if not inputs:
        raise InputFormatError("Inputs should not be empty.")

    if "messages" in inputs:
        single_input = inputs["messages"]
    elif len(inputs) == 1:
        single_input = next(iter(inputs.values()))
    else:
        raise InputFormatError(
            f"Chat Run expects 'messages' in inputs when example has multiple"
            f" input keys. Got {inputs}"
        )
    if isinstance(single_input, list) and all(
        isinstance(i, dict) for i in single_input
    ):
        raw_messages = [single_input]
    elif isinstance(single_input, list) and all(
        isinstance(i, list) for i in single_input
    ):
        raw_messages = single_input
    else:
        raise InputFormatError(
            f"Chat Run expects List[dict] or List[List[dict]] values for"
            f" 'messages' key input. Got {inputs}"
        )
    if len(raw_messages) == 1:
        return messages_from_dict(raw_messages[0])
    else:
        raise InputFormatError(
            f"Chat Run expects single List[dict] or List[List[dict]] 'messages'"
            f" input. Got {len(raw_messages)} messages from inputs {inputs}"
        )


def _get_project_name(
    project_name: Optional[str],
    llm_or_chain_factory: MCF,
) -> str:
    """
    Get the project name.

    Args:
        project_name: The project name if manually specified.
        llm_or_chain_factory: The Chain or language model constructor.

    Returns:
        The project name.
    """
    if project_name is not None:
        return project_name
    if isinstance(llm_or_chain_factory, BaseLanguageModel):
        model_name = llm_or_chain_factory.__class__.__name__
    else:
        model_name = llm_or_chain_factory().__class__.__name__
    hex = uuid.uuid4().hex
    return f"{hex}-{model_name}"


## Shared Validation Utilities
def _validate_example_inputs_for_language_model(
    first_example: Example,
    input_mapper: Optional[Callable[[Dict], Any]],
) -> None:
    if input_mapper:
        prompt_input = input_mapper(first_example.inputs)
        if not isinstance(prompt_input, str) and not (
            isinstance(prompt_input, list)
            and all(isinstance(msg, BaseMessage) for msg in prompt_input)
        ):
            raise InputFormatError(
                "When using an input_mapper to prepare dataset example inputs"
                " for an LLM or chat model, the output must a single string or"
                " a list of chat messages."
                f"\nGot: {prompt_input} of type {type(prompt_input)}."
            )
    else:
        try:
            _get_prompt(first_example.inputs)
        except InputFormatError:
            try:
                _get_messages(first_example.inputs)
            except InputFormatError:
                raise InputFormatError(
                    "Example inputs do not match language model input format. "
                    "Expected a dictionary with messages or a single prompt."
                    f" Got: {first_example.inputs}"
                    " Please update your dataset OR provide an input_mapper"
                    " to convert the example.inputs to a compatible format"
                    " for the llm or chat model you wish to evaluate."
                )


def _validate_example_inputs_for_chain(
    first_example: Example,
    chain: Chain,
    input_mapper: Optional[Callable[[Dict], Any]],
) -> None:
    """Validate that the example inputs match the chain input keys."""
    if input_mapper:
        first_inputs = input_mapper(first_example.inputs)
        missing_keys = set(chain.input_keys).difference(first_inputs)
        if not isinstance(first_inputs, dict):
            raise InputFormatError(
                "When using an input_mapper to prepare dataset example"
                " inputs for a chain, the mapped value must be a dictionary."
                f"\nGot: {first_inputs} of type {type(first_inputs)}."
            )
        if missing_keys:
            raise InputFormatError(
                "Missing keys after loading example using input_mapper."
                f"\nExpected: {chain.input_keys}. Got: {first_inputs.keys()}"
            )
    else:
        first_inputs = first_example.inputs
        missing_keys = set(chain.input_keys).difference(first_inputs)
        if len(first_inputs) == 1 and len(chain.input_keys) == 1:
            # We can pass this through the run method.
            # Refrain from calling to validate.
            pass
        elif missing_keys:
            raise InputFormatError(
                "Example inputs missing expected chain input keys."
                " Please provide an input_mapper to convert the example.inputs"
                " to a compatible format for the chain you wish to evaluate."
                f"Expected: {chain.input_keys}. "
                f"Got: {first_inputs.keys()}"
            )


def _validate_example_inputs(
    examples: Iterator[Example],
    llm_or_chain_factory: MCF,
    input_mapper: Optional[Callable[[Dict], Any]],
) -> Iterator[Example]:
    """Validate that the example inputs are valid for the model."""
    first_example, examples = _first_example(examples)
    if isinstance(llm_or_chain_factory, BaseLanguageModel):
        _validate_example_inputs_for_language_model(first_example, input_mapper)
    else:
        chain = llm_or_chain_factory()
        if isinstance(chain, Chain):
            # Otherwise it's a runnable
            _validate_example_inputs_for_chain(first_example, chain, input_mapper)
        elif isinstance(chain, Runnable):
            logger.debug(f"Skipping input validation for {chain}")
    return examples


## Shared Evaluator Setup Utilities


def _setup_evaluation(
    llm_or_chain_factory: MCF,
    examples: Iterator[Example],
    evaluation: Optional[RunEvalConfig],
    data_type: DataType,
) -> Tuple[Optional[List[RunEvaluator]], Iterator[Example]]:
    """Configure the evaluators to run on the results of the chain."""
    if evaluation:
        first_example, examples = _first_example(examples)
        if isinstance(llm_or_chain_factory, BaseLanguageModel):
            run_inputs, run_outputs = None, None
            run_type = "llm"
        else:
            run_type = "chain"
            if data_type in (DataType.chat, DataType.llm):
                val = data_type.value if isinstance(data_type, Enum) else data_type
                raise ValueError(
                    "Cannot evaluate a chain on dataset with "
                    f"data_type={val}. "
                    "Please specify a dataset with the default 'kv' data type."
                )
            chain = llm_or_chain_factory()
            run_inputs = chain.input_keys if isinstance(chain, Chain) else None
            run_outputs = chain.output_keys if isinstance(chain, Chain) else None
        run_evaluators = _load_run_evaluators(
            evaluation,
            run_type,
            data_type,
            list(first_example.outputs) if first_example.outputs else None,
            run_inputs,
            run_outputs,
        )
    else:
        # TODO: Create a default helpfulness evaluator
        run_evaluators = None
    return run_evaluators, examples


def _determine_input_key(
    config: RunEvalConfig,
    run_inputs: Optional[List[str]],
) -> Optional[str]:
    input_key = None
    if config.input_key:
        input_key = config.input_key
        if run_inputs and input_key not in run_inputs:
            raise ValueError(f"Input key {input_key} not in run inputs {run_inputs}")
    elif run_inputs and len(run_inputs) == 1:
        input_key = run_inputs[0]
    elif run_inputs is not None and len(run_inputs) > 1:
        raise ValueError(
            f"Must specify input key for model with multiple inputs: {run_inputs}"
        )

    return input_key


def _determine_prediction_key(
    config: RunEvalConfig,
    run_outputs: Optional[List[str]],
) -> Optional[str]:
    prediction_key = None
    if config.prediction_key:
        prediction_key = config.prediction_key
        if run_outputs and prediction_key not in run_outputs:
            raise ValueError(
                f"Prediction key {prediction_key} not in run outputs {run_outputs}"
            )
    elif run_outputs and len(run_outputs) == 1:
        prediction_key = run_outputs[0]
    elif run_outputs is not None and len(run_outputs) > 1:
        raise ValueError(
            f"Must specify prediction key for model"
            f" with multiple outputs: {run_outputs}"
        )
    return prediction_key


def _determine_reference_key(
    config: RunEvalConfig,
    example_outputs: Optional[List[str]],
) -> Optional[str]:
    if config.reference_key:
        reference_key = config.reference_key
        if example_outputs and reference_key not in example_outputs:
            raise ValueError(
                f"Reference key {reference_key} not in Dataset"
                f" example outputs: {example_outputs}"
            )
    elif example_outputs and len(example_outputs) == 1:
        reference_key = list(example_outputs)[0]
    else:
        reference_key = None
    return reference_key


def _construct_run_evaluator(
    eval_config: Union[EvaluatorType, str, EvalConfig],
    eval_llm: BaseLanguageModel,
    run_type: str,
    data_type: DataType,
    example_outputs: Optional[List[str]],
    reference_key: Optional[str],
    input_key: Optional[str],
    prediction_key: Optional[str],
) -> RunEvaluator:
    if isinstance(eval_config, (EvaluatorType, str)):
        if not isinstance(eval_config, EvaluatorType):
            eval_config = EvaluatorType(eval_config)
        evaluator_ = load_evaluator(eval_config, llm=eval_llm)
        eval_type_tag = eval_config.value
    else:
        kwargs = {"llm": eval_llm, **eval_config.get_kwargs()}
        evaluator_ = load_evaluator(eval_config.evaluator_type, **kwargs)
        eval_type_tag = eval_config.evaluator_type.value

    if isinstance(evaluator_, StringEvaluator):
        if evaluator_.requires_reference and reference_key is None:
            raise ValueError(
                f"Must specify reference_key in RunEvalConfig to use"
                f" evaluator of type {eval_type_tag} with"
                f" dataset with multiple output keys: {example_outputs}."
            )
        run_evaluator = StringRunEvaluatorChain.from_run_and_data_type(
            evaluator_,
            run_type,
            data_type,
            input_key=input_key,
            prediction_key=prediction_key,
            reference_key=reference_key,
            tags=[eval_type_tag],
        )
    else:
        raise NotImplementedError(
            f"Run evaluator for {eval_type_tag} is not implemented"
        )
    return run_evaluator


def _get_keys(
    config: RunEvalConfig,
    run_inputs: Optional[List[str]],
    run_outputs: Optional[List[str]],
    example_outputs: Optional[List[str]],
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    input_key = _determine_input_key(config, run_inputs)
    prediction_key = _determine_prediction_key(config, run_outputs)
    reference_key = _determine_reference_key(config, example_outputs)
    return input_key, prediction_key, reference_key


def _load_run_evaluators(
    config: RunEvalConfig,
    run_type: str,
    data_type: DataType,
    example_outputs: Optional[List[str]],
    run_inputs: Optional[List[str]],
    run_outputs: Optional[List[str]],
) -> List[RunEvaluator]:
    """
    Load run evaluators from a configuration.

    Args:
        config: Configuration for the run evaluators.

    Returns:
        A list of run evaluators.
    """
    eval_llm = config.eval_llm or ChatOpenAI(model="gpt-4", temperature=0.0)
    run_evaluators = []
    input_key, prediction_key, reference_key = None, None, None
    if (
        config.evaluators
        or any([isinstance(e, EvaluatorType) for e in config.evaluators])
        or (
            config.custom_evaluators
            and any([isinstance(e, StringEvaluator) for e in config.custom_evaluators])
        )
    ):
        input_key, prediction_key, reference_key = _get_keys(
            config, run_inputs, run_outputs, example_outputs
        )
    for eval_config in config.evaluators:
        run_evaluator = _construct_run_evaluator(
            eval_config,
            eval_llm,
            run_type,
            data_type,
            example_outputs,
            reference_key,
            input_key,
            prediction_key,
        )
        run_evaluators.append(run_evaluator)
    custom_evaluators = config.custom_evaluators or []
    for custom_evaluator in custom_evaluators:
        if isinstance(custom_evaluator, RunEvaluator):
            run_evaluators.append(custom_evaluator)
        elif isinstance(custom_evaluator, StringEvaluator):
            run_evaluators.append(
                StringRunEvaluatorChain.from_run_and_data_type(
                    custom_evaluator,
                    run_type,
                    data_type,
                    input_key=input_key,
                    prediction_key=prediction_key,
                    reference_key=reference_key,
                )
            )
        else:
            raise ValueError(
                f"Unsupported custom evaluator: {custom_evaluator}."
                f" Expected RunEvaluator or StringEvaluator."
            )

    return run_evaluators


### Async Helpers


async def _arun_llm(
    llm: BaseLanguageModel,
    inputs: Dict[str, Any],
    *,
    tags: Optional[List[str]] = None,
    callbacks: Callbacks = None,
    input_mapper: Optional[Callable[[Dict], Any]] = None,
) -> Union[str, BaseMessage]:
    """Asynchronously run the language model.

    Args:
        llm: The language model to run.
        inputs: The input dictionary.
        tags: Optional tags to add to the run.
        callbacks: Optional callbacks to use during the run.
        input_mapper: Optional function to map inputs to the expected format.

    Returns:
        The LLMResult or ChatResult.
    Raises:
        ValueError: If the LLM type is unsupported.
        InputFormatError: If the input format is invalid.
    """
    if input_mapper is not None:
        prompt_or_messages = input_mapper(inputs)
        if isinstance(prompt_or_messages, str):
            return await llm.apredict(
                prompt_or_messages, callbacks=callbacks, tags=tags
            )
        elif isinstance(prompt_or_messages, list) and all(
            isinstance(msg, BaseMessage) for msg in prompt_or_messages
        ):
            return await llm.apredict_messages(
                prompt_or_messages, callbacks=callbacks, tags=tags
            )
        else:
            raise InputFormatError(
                "Input mapper returned invalid format"
                f" {prompt_or_messages}"
                "\nExpected a single string or list of chat messages."
            )

    else:
        try:
            prompt = _get_prompt(inputs)
            llm_output: Union[str, BaseMessage] = await llm.apredict(
                prompt, callbacks=callbacks, tags=tags
            )
        except InputFormatError:
            messages = _get_messages(inputs)
            llm_output = await llm.apredict_messages(
                messages, callbacks=callbacks, tags=tags
            )
    return llm_output


async def _arun_chain(
    chain: Union[Chain, Runnable],
    inputs: Dict[str, Any],
    callbacks: Callbacks,
    *,
    tags: Optional[List[str]] = None,
    input_mapper: Optional[Callable[[Dict], Any]] = None,
) -> Union[dict, str]:
    """Run a chain asynchronously on inputs."""
    inputs_ = inputs if input_mapper is None else input_mapper(inputs)
    if isinstance(chain, Chain):
        if isinstance(inputs_, dict) and len(inputs_) == 1:
            val = next(iter(inputs_.values()))
            output = await chain.acall(val, callbacks=callbacks, tags=tags)
        else:
            output = await chain.acall(inputs_, callbacks=callbacks, tags=tags)
    else:
        runnable_config = RunnableConfig(tags=tags or [], callbacks=callbacks)
        output = await chain.ainvoke(inputs_, config=runnable_config)
    return output


async def _arun_llm_or_chain(
    example: Example,
    llm_or_chain_factory: MCF,
    *,
    tags: Optional[List[str]] = None,
    callbacks: Optional[List[BaseCallbackHandler]] = None,
    input_mapper: Optional[Callable[[Dict], Any]] = None,
) -> Union[dict, str, LLMResult, ChatResult]:
    """Asynchronously run the Chain or language model.

    Args:
        example: The example to run.
        llm_or_chain_factory: The Chain or language model constructor to run.
        tags: Optional tags to add to the run.
        callbacks: Optional callbacks to use during the run.
        input_mapper: Optional function to map the input to the expected format.

    Returns:
        A list of outputs.
    """
    if callbacks:
        previous_example_ids = [
            getattr(tracer, "example_id", None) for tracer in callbacks
        ]
        for tracer in callbacks:
            if hasattr(tracer, "example_id"):
                tracer.example_id = example.id
    else:
        previous_example_ids = None
    chain_or_llm = (
        "LLM" if isinstance(llm_or_chain_factory, BaseLanguageModel) else "Chain"
    )
    result = None
    try:
        if isinstance(llm_or_chain_factory, BaseLanguageModel):
            output: Any = await _arun_llm(
                llm_or_chain_factory,
                example.inputs,
                tags=tags,
                callbacks=callbacks,
                input_mapper=input_mapper,
            )
        else:
            chain = llm_or_chain_factory()
            output = await _arun_chain(
                chain,
                example.inputs,
                tags=tags,
                callbacks=callbacks,
                input_mapper=input_mapper,
            )
        result = output
    except Exception as e:
        logger.warning(f"{chain_or_llm} failed for example {example.id}. Error: {e}")
        result = {"Error": str(e)}
    if callbacks and previous_example_ids:
        for example_id, tracer in zip(previous_example_ids, callbacks):
            if hasattr(tracer, "example_id"):
                tracer.example_id = example_id
    return result


async def _gather_with_concurrency(
    n: int,
    initializer: Callable[[], Coroutine[Any, Any, Any]],
    *async_funcs: Callable[
        [Sequence[BaseCallbackHandler], Dict], Coroutine[Any, Any, Any]
    ],
) -> List[Any]:
    """Run coroutines with a concurrency limit.

    Args:
        n: The maximum number of concurrent tasks.
        initializer: A coroutine that initializes shared resources for the tasks.
        async_funcs: The async_funcs to be run concurrently.

    Returns:
        A list of results from the coroutines.
    """
    semaphore = asyncio.Semaphore(n)
    job_state = {"num_processed": 0}

    callback_queue: asyncio.Queue[Sequence[BaseCallbackHandler]] = asyncio.Queue()
    for _ in range(n):
        callback_queue.put_nowait(await initializer())

    async def run_coroutine_with_semaphore(
        async_func: Callable[
            [Sequence[BaseCallbackHandler], Dict], Coroutine[Any, Any, Any]
        ]
    ) -> Any:
        async with semaphore:
            callbacks = await callback_queue.get()
            try:
                result = await async_func(callbacks, job_state)
            finally:
                callback_queue.put_nowait(callbacks)
            return result

    results = await asyncio.gather(
        *(run_coroutine_with_semaphore(function) for function in async_funcs)
    )
    while callback_queue:
        try:
            callbacks = callback_queue.get_nowait()
        except asyncio.QueueEmpty:
            break
        for callback in callbacks:
            if isinstance(callback, (LangChainTracer, EvaluatorCallbackHandler)):
                callback.wait_for_futures()
    return results


async def _callbacks_initializer(
    project_name: Optional[str],
    client: Client,
    run_evaluators: Sequence[RunEvaluator],
    evaluation_handler_collector: List[EvaluatorCallbackHandler],
) -> List[BaseTracer]:
    """
    Initialize a tracer to share across tasks.

    Args:
        project_name: The project name for the tracer.
        client: The client to use for the tracer.
        run_evaluators: The evaluators to run.
        evaluation_handler_collector: A list to collect the evaluators.
            Used to wait for the evaluators to finish.

    Returns:
        The callbacks for this thread.
    """
    callbacks: List[BaseTracer] = []
    if project_name:
        callbacks.append(
            LangChainTracer(
                project_name=project_name, client=client, use_threading=False
            )
        )
    if run_evaluators:
        callback = EvaluatorCallbackHandler(
            client=client,
            evaluators=run_evaluators,
            # We already have concurrency, don't want to overload the machine
            max_workers=1,
        )
        callbacks.append(callback)
        evaluation_handler_collector.append(callback)
    return callbacks


async def _arun_on_examples(
    client: Client,
    examples: Iterator[Example],
    llm_or_chain_factory: MODEL_OR_CHAIN_FACTORY,
    *,
    evaluation: Optional[RunEvalConfig] = None,
    concurrency_level: int = 5,
    project_name: Optional[str] = None,
    verbose: bool = False,
    tags: Optional[List[str]] = None,
    input_mapper: Optional[Callable[[Dict], Any]] = None,
    data_type: DataType = DataType.kv,
) -> Dict[str, Any]:
    """
    Asynchronously run the chain on examples and store traces
        to the specified project name.

    Args:
        client: LangSmith client to use to log feedback and runs.
        examples: Examples to run the model or chain over.
        llm_or_chain_factory: Language model or Chain constructor to run
            over the dataset. The Chain constructor is used to permit
            independent calls on each example without carrying over state.
        evaluation: Optional evaluation configuration to use when evaluating
        concurrency_level: The number of async tasks to run concurrently.
        project_name: Project name to use when tracing runs.
            Defaults to {dataset_name}-{chain class name}-{datetime}.
        verbose: Whether to print progress.
        tags: Tags to add to each run in the project.
        input_mapper: function to map to the inputs dictionary from an Example
            to the format expected by the model to be evaluated. This is useful if
            your model needs to deserialize more complex schema or if your dataset
            has inputs with keys that differ from what is expected by your chain
            or agent.
        data_type: The dataset's data type. This is used to determine determine
            how to deserialize the reference data and model compatibility.
    Returns:
        A dictionary mapping example ids to the model outputs.
    """
    wrapped_model = _wrap_in_chain_factory(llm_or_chain_factory)
    project_name = _get_project_name(project_name, wrapped_model)
    run_evaluators, examples = _setup_evaluation(
        wrapped_model, examples, evaluation, data_type
    )
    examples = _validate_example_inputs(examples, wrapped_model, input_mapper)
    results: Dict[str, dict] = {}

    async def process_example(
        example: Example, callbacks: List[BaseCallbackHandler], job_state: dict
    ) -> None:
        """Process a single example."""
        result = await _arun_llm_or_chain(
            example,
            wrapped_model,
            tags=tags,
            callbacks=callbacks,
            input_mapper=input_mapper,
        )
        results[str(example.id)] = {"output": result}
        job_state["num_processed"] += 1
        if verbose:
            print(
                f"Processed examples: {job_state['num_processed']}",
                end="\r",
                flush=True,
            )

    evaluation_handlers: List[EvaluatorCallbackHandler] = []
    await _gather_with_concurrency(
        concurrency_level,
        functools.partial(
            _callbacks_initializer,
            project_name=project_name,
            client=client,
            evaluation_handler_collector=evaluation_handlers,
            run_evaluators=run_evaluators or [],
        ),
        *(functools.partial(process_example, e) for e in examples),
    )
    all_feedback = {}
    for handler in evaluation_handlers:
        handler.wait_for_futures()
        all_feedback.update(handler.logged_feedback)
    # join the results and feedback on the example id
    for example_id, output_dict in results.items():
        feedback = all_feedback.get(example_id, [])
        output_dict["feedback"] = feedback
    return results


## Sync Utilities


def _run_llm(
    llm: BaseLanguageModel,
    inputs: Dict[str, Any],
    callbacks: Callbacks,
    *,
    tags: Optional[List[str]] = None,
    input_mapper: Optional[Callable[[Dict], Any]] = None,
) -> Union[str, BaseMessage]:
    """
    Run the language model on the example.

    Args:
        llm: The language model to run.
        inputs: The input dictionary.
        callbacks: The callbacks to use during the run.
        tags: Optional tags to add to the run.
        input_mapper: function to map to the inputs dictionary from an Example
    Returns:
        The LLMResult or ChatResult.
    Raises:
        ValueError: If the LLM type is unsupported.
        InputFormatError: If the input format is invalid.
    """
    if input_mapper is not None:
        prompt_or_messages = input_mapper(inputs)
        if isinstance(prompt_or_messages, str):
            llm_output: Union[str, BaseMessage] = llm.predict(
                prompt_or_messages, callbacks=callbacks, tags=tags
            )
        elif isinstance(prompt_or_messages, list) and all(
            isinstance(msg, BaseMessage) for msg in prompt_or_messages
        ):
            llm_output = llm.predict_messages(
                prompt_or_messages, callbacks=callbacks, tags=tags
            )
        else:
            raise InputFormatError(
                "Input mapper returned invalid format: "
                f" {prompt_or_messages}"
                "\nExpected a single string or list of chat messages."
            )
    else:
        try:
            llm_prompts = _get_prompt(inputs)
            llm_output = llm.predict(llm_prompts, callbacks=callbacks, tags=tags)
        except InputFormatError:
            llm_messages = _get_messages(inputs)
            llm_output = llm.predict_messages(llm_messages, callbacks=callbacks)
    return llm_output


def _run_chain(
    chain: Union[Chain, Runnable],
    inputs: Dict[str, Any],
    callbacks: Callbacks,
    *,
    tags: Optional[List[str]] = None,
    input_mapper: Optional[Callable[[Dict], Any]] = None,
) -> Union[Dict, str]:
    """Run a chain on inputs."""
    inputs_ = inputs if input_mapper is None else input_mapper(inputs)
    if isinstance(chain, Chain):
        if isinstance(inputs_, dict) and len(inputs_) == 1:
            val = next(iter(inputs_.values()))
            output = chain(val, callbacks=callbacks, tags=tags)
        else:
            output = chain(inputs_, callbacks=callbacks, tags=tags)
    else:
        runnable_config = RunnableConfig(tags=tags or [], callbacks=callbacks)
        output = chain.invoke(inputs_, config=runnable_config)
    return output


def _run_llm_or_chain(
    example: Example,
    llm_or_chain_factory: MCF,
    *,
    tags: Optional[List[str]] = None,
    callbacks: Optional[List[BaseCallbackHandler]] = None,
    input_mapper: Optional[Callable[[Dict], Any]] = None,
) -> Union[dict, str, LLMResult, ChatResult]:
    """
    Run the Chain or language model synchronously.

    Args:
        example: The example to run.
        llm_or_chain_factory: The Chain or language model constructor to run.
        tags: Optional tags to add to the run.
        callbacks: Optional callbacks to use during the run.

    Returns:
        Union[List[dict], List[str], List[LLMResult], List[ChatResult]]:
          The outputs of the model or chain.
    """
    if callbacks:
        previous_example_ids = [
            getattr(tracer, "example_id", None) for tracer in callbacks
        ]
        for tracer in callbacks:
            if hasattr(tracer, "example_id"):
                tracer.example_id = example.id
    else:
        previous_example_ids = None
    chain_or_llm = (
        "LLM" if isinstance(llm_or_chain_factory, BaseLanguageModel) else "Chain"
    )
    result = None
    try:
        if isinstance(llm_or_chain_factory, BaseLanguageModel):
            output: Any = _run_llm(
                llm_or_chain_factory,
                example.inputs,
                callbacks,
                tags=tags,
                input_mapper=input_mapper,
            )
        else:
            chain = llm_or_chain_factory()
            output = _run_chain(
                chain,
                example.inputs,
                callbacks,
                tags=tags,
                input_mapper=input_mapper,
            )
        result = output
    except Exception as e:
        logger.warning(
            f"{chain_or_llm} failed for example {example.id} with inputs:"
            f" {example.inputs}.\nError: {e}",
        )
        result = {"Error": str(e)}
    if callbacks and previous_example_ids:
        for example_id, tracer in zip(previous_example_ids, callbacks):
            if hasattr(tracer, "example_id"):
                tracer.example_id = example_id
    return result


def _run_on_examples(
    client: Client,
    examples: Iterator[Example],
    llm_or_chain_factory: MODEL_OR_CHAIN_FACTORY,
    *,
    evaluation: Optional[RunEvalConfig] = None,
    project_name: Optional[str] = None,
    verbose: bool = False,
    tags: Optional[List[str]] = None,
    input_mapper: Optional[Callable[[Dict], Any]] = None,
    data_type: DataType = DataType.kv,
) -> Dict[str, Any]:
    """
    Run the Chain or language model on examples and store
    traces to the specified project name.

    Args:
        client: LangSmith client to use to log feedback and runs.
        examples: Examples to run the model or chain over.
        llm_or_chain_factory: Language model or Chain constructor to run
            over the dataset. The Chain constructor is used to permit
            independent calls on each example without carrying over state.
        evaluation: Optional evaluation configuration to use when evaluating
        project_name: Name of the project to store the traces in.
            Defaults to {dataset_name}-{chain class name}-{datetime}.
        verbose: Whether to print progress.
        tags: Tags to add to each run in the project.
        input_mapper: A function to map to the inputs dictionary from an Example
            to the format expected by the model to be evaluated. This is useful if
            your model needs to deserialize more complex schema or if your dataset
            has inputs with keys that differ from what is expected by your chain
            or agent.
        data_type: The dataset's data type. This is used to determine determine
            how to deserialize the reference data and model compatibility.

    Returns:
        A dictionary mapping example ids to the model outputs.
    """
    results: Dict[str, dict] = {}
    wrapped_model = _wrap_in_chain_factory(llm_or_chain_factory)
    project_name = _get_project_name(project_name, wrapped_model)
    tracer = LangChainTracer(
        project_name=project_name, client=client, use_threading=False
    )
    run_evaluators, examples = _setup_evaluation(
        wrapped_model, examples, evaluation, data_type
    )
    examples = _validate_example_inputs(examples, wrapped_model, input_mapper)
    evaluation_handler = EvaluatorCallbackHandler(
        evaluators=run_evaluators or [],
        client=client,
    )
    callbacks: List[BaseCallbackHandler] = [tracer, evaluation_handler]
    for i, example in enumerate(examples):
        result = _run_llm_or_chain(
            example,
            wrapped_model,
            tags=tags,
            callbacks=callbacks,
            input_mapper=input_mapper,
        )
        if verbose:
            print(f"{i+1} processed", flush=True, end="\r")
        results[str(example.id)] = {"output": result}
    tracer.wait_for_futures()
    evaluation_handler.wait_for_futures()
    all_feedback = evaluation_handler.logged_feedback
    # join the results and feedback on the example id
    for example_id, output_dict in results.items():
        feedback = all_feedback.get(example_id, [])
        output_dict["feedback"] = feedback
    return results


## Public API


def _prepare_eval_run(
    client: Client,
    dataset_name: str,
    llm_or_chain_factory: MODEL_OR_CHAIN_FACTORY,
    project_name: Optional[str],
) -> Tuple[MCF, str, Dataset, Iterator[Example]]:
    wrapped_model = _wrap_in_chain_factory(llm_or_chain_factory, dataset_name)
    project_name = _get_project_name(project_name, wrapped_model)
    try:
        project = client.create_project(project_name)
    except ValueError as e:
        if "already exists " not in str(e):
            raise e
        raise ValueError(
            f"Project {project_name} already exists. Please use a different name."
        )
    project_url = _get_eval_project_url(client.api_url, project.id)
    print(
        f"View the evaluation results for project '{project_name}' at:\n{project_url}"
    )
    dataset = client.read_dataset(dataset_name=dataset_name)
    examples = client.list_examples(dataset_id=str(dataset.id))
    return wrapped_model, project_name, dataset, examples


async def arun_on_dataset(
    client: Client,
    dataset_name: str,
    llm_or_chain_factory: MODEL_OR_CHAIN_FACTORY,
    *,
    evaluation: Optional[RunEvalConfig] = None,
    concurrency_level: int = 5,
    project_name: Optional[str] = None,
    verbose: bool = False,
    tags: Optional[List[str]] = None,
    input_mapper: Optional[Callable[[Dict], Any]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Asynchronously run the Chain or language model on a dataset
    and store traces to the specified project name.

    Args:
        client: LangSmith client to use to read the dataset, and to
            log feedback and run traces.
        dataset_name: Name of the dataset to run the chain on.
        llm_or_chain_factory: Language model or Chain constructor to run
            over the dataset. The Chain constructor is used to permit
            independent calls on each example without carrying over state.
        evaluation: Optional evaluation configuration to use when evaluating
        concurrency_level: The number of async tasks to run concurrently.
        project_name: Name of the project to store the traces in.
            Defaults to {dataset_name}-{chain class name}-{datetime}.
        verbose: Whether to print progress.
        tags: Tags to add to each run in the project.
        input_mapper: A function to map to the inputs dictionary from an Example
            to the format expected by the model to be evaluated. This is useful if
            your model needs to deserialize more complex schema or if your dataset
            has inputs with keys that differ from what is expected by your chain
            or agent.

    Returns:
        A dictionary containing the run's project name and the
        resulting model outputs.

    For the synchronous version, see :func:`run_on_dataset`.

    Examples
    --------

    .. code-block:: python

        from langsmith import Client
        from langchain.chat_models import ChatOpenAI
        from langchain.chains import LLMChain
        from langchain.smith import RunEvalConfig, arun_on_dataset

        # Chains may have memory. Passing in a constructor function lets the
        # evaluation framework avoid cross-contamination between runs.
        def construct_chain():
            llm = ChatOpenAI(temperature=0)
            chain = LLMChain.from_string(
                llm,
                "What's the answer to {your_input_key}"
            )
            return chain

        # Load off-the-shelf evaluators via config or the EvaluatorType (string or enum)
        evaluation_config = RunEvalConfig(
            evaluators=[
                "qa",  # "Correctness" against a reference answer
                "embedding_distance",
                RunEvalConfig.Criteria("helpfulness"),
                RunEvalConfig.Criteria({
                    "fifth-grader-score": "Do you have to be smarter than a fifth grader to answer this question?"
                }),
            ]
        )

        client = Client()
        await arun_on_dataset(
            client,
            "<my_dataset_name>",
            construct_chain,
            evaluation=evaluation_config,
        )

    You can also create custom evaluators by subclassing the
    :class:`StringEvaluator <langchain.evaluation.schema.StringEvaluator>`
    or LangSmith's `RunEvaluator` classes.

    .. code-block:: python

        from typing import Optional
        from langchain.evaluation import StringEvaluator

        class MyStringEvaluator(StringEvaluator):

            @property
            def requires_input(self) -> bool:
                return False

            @property
            def requires_reference(self) -> bool:
                return True

            @property
            def evaluation_name(self) -> str:
                return "exact_match"

            def _evaluate_strings(self, prediction, reference=None, input=None, **kwargs) -> dict:
                return {"score": prediction == reference}


        evaluation_config = RunEvalConfig(
            custom_evaluators = [MyStringEvaluator()],
        )

        await arun_on_dataset(
            client,
            "<my_dataset_name>",
            construct_chain,
            evaluation=evaluation_config,
        )
    """  # noqa: E501
    if kwargs:
        warnings.warn(
            "The following arguments are deprecated and will "
            "be removed in a future release: "
            f"{kwargs.keys()}.",
            DeprecationWarning,
        )
    wrapped_model, project_name, dataset, examples = _prepare_eval_run(
        client, dataset_name, llm_or_chain_factory, project_name
    )
    results = await _arun_on_examples(
        client,
        examples,
        wrapped_model,
        concurrency_level=concurrency_level,
        project_name=project_name,
        verbose=verbose,
        tags=tags,
        evaluation=evaluation,
        input_mapper=input_mapper,
        data_type=dataset.data_type,
    )
    return TestResult(
        project_name=project_name,
        results=results,
    )


def _handle_coroutine(coro: Coroutine) -> Any:
    """
    Handles a coroutine from a sync context.

    Args:
        coro (asyncio.coroutine): The coroutine to be handled.

    Returns:
        any: The result of the executed coroutine.
    """
    # Check if there's a running event loop
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:  # No event loop
        return asyncio.run(coro)
    if loop.is_running():
        return loop.run_until_complete(coro)
    else:
        return asyncio.run(coro)


def run_on_dataset(
    client: Client,
    dataset_name: str,
    llm_or_chain_factory: MODEL_OR_CHAIN_FACTORY,
    *,
    evaluation: Optional[RunEvalConfig] = None,
    concurrency_level: int = 5,
    project_name: Optional[str] = None,
    verbose: bool = False,
    tags: Optional[List[str]] = None,
    input_mapper: Optional[Callable[[Dict], Any]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Run the Chain or language model on a dataset and store traces
    to the specified project name.

    Args:
        client: LangSmith client to use to access the dataset and to
            log feedback and run traces.
        dataset_name: Name of the dataset to run the chain on.
        llm_or_chain_factory: Language model or Chain constructor to run
            over the dataset. The Chain constructor is used to permit
            independent calls on each example without carrying over state.
        evaluation: Configuration for evaluators to run on the
            results of the chain
        concurrency_level: The number of async tasks to run concurrently.
        project_name: Name of the project to store the traces in.
            Defaults to {dataset_name}-{chain class name}-{datetime}.
        verbose: Whether to print progress.
        tags: Tags to add to each run in the project.
        input_mapper: A function to map to the inputs dictionary from an Example
            to the format expected by the model to be evaluated. This is useful if
            your model needs to deserialize more complex schema or if your dataset
            has inputs with keys that differ from what is expected by your chain
            or agent.

    Returns:
        A dictionary containing the run's project name and the resulting model outputs.


    For the (usually faster) async version of this function, see :func:`arun_on_dataset`.

    Examples
    --------

    .. code-block:: python

        from langsmith import Client
        from langchain.chat_models import ChatOpenAI
        from langchain.chains import LLMChain
        from langchain.smith import RunEvalConfig, run_on_dataset

        # Chains may have memory. Passing in a constructor function lets the
        # evaluation framework avoid cross-contamination between runs.
        def construct_chain():
            llm = ChatOpenAI(temperature=0)
            chain = LLMChain.from_string(
                llm,
                "What's the answer to {your_input_key}"
            )
            return chain

        # Load off-the-shelf evaluators via config or the EvaluatorType (string or enum)
        evaluation_config = RunEvalConfig(
            evaluators=[
                "qa",  # "Correctness" against a reference answer
                "embedding_distance",
                RunEvalConfig.Criteria("helpfulness"),
                RunEvalConfig.Criteria({
                    "fifth-grader-score": "Do you have to be smarter than a fifth grader to answer this question?"
                }),
            ]
        )

        client = Client()
        run_on_dataset(
            client,
            "<my_dataset_name>",
            construct_chain,
            evaluation=evaluation_config,
        )

    You can also create custom evaluators by subclassing the
    :class:`StringEvaluator <langchain.evaluation.schema.StringEvaluator>`
    or LangSmith's `RunEvaluator` classes.

    .. code-block:: python

        from typing import Optional
        from langchain.evaluation import StringEvaluator

        class MyStringEvaluator(StringEvaluator):

            @property
            def requires_input(self) -> bool:
                return False

            @property
            def requires_reference(self) -> bool:
                return True

            @property
            def evaluation_name(self) -> str:
                return "exact_match"

            def _evaluate_strings(self, prediction, reference=None, input=None, **kwargs) -> dict:
                return {"score": prediction == reference}


        evaluation_config = RunEvalConfig(
            custom_evaluators = [MyStringEvaluator()],
        )

        run_on_dataset(
            client,
            "<my_dataset_name>",
            construct_chain,
            evaluation=evaluation_config,
        )
    """  # noqa: E501
    if kwargs:
        warnings.warn(
            "The following arguments are deprecated and "
            "will be removed in a future release: "
            f"{kwargs.keys()}.",
            DeprecationWarning,
        )
    wrapped_model, project_name, dataset, examples = _prepare_eval_run(
        client, dataset_name, llm_or_chain_factory, project_name
    )
    if concurrency_level in (0, 1):
        results = _run_on_examples(
            client,
            examples,
            wrapped_model,
            project_name=project_name,
            verbose=verbose,
            tags=tags,
            evaluation=evaluation,
            input_mapper=input_mapper,
            data_type=dataset.data_type,
        )
    else:
        # TODO: Use runnables and the batch method
        coro = _arun_on_examples(
            client,
            examples,
            wrapped_model,
            concurrency_level=concurrency_level,
            project_name=project_name,
            verbose=verbose,
            tags=tags,
            evaluation=evaluation,
            input_mapper=input_mapper,
            data_type=dataset.data_type,
        )
        results = _handle_coroutine(coro)
    return TestResult(
        project_name=project_name,
        results=results,
    )
