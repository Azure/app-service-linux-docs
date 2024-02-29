"""Base interface that all chains should implement."""
import asyncio
import inspect
import json
import logging
import warnings
from abc import ABC, abstractmethod
from functools import partial
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

import langchain
from langchain.callbacks.base import BaseCallbackManager
from langchain.callbacks.manager import (
    AsyncCallbackManager,
    AsyncCallbackManagerForChainRun,
    CallbackManager,
    CallbackManagerForChainRun,
    Callbacks,
)
from langchain.load.dump import dumpd
from langchain.load.serializable import Serializable
from langchain.pydantic_v1 import Field, root_validator, validator
from langchain.schema import RUN_KEY, BaseMemory, RunInfo
from langchain.schema.runnable import Runnable, RunnableConfig

logger = logging.getLogger(__name__)


def _get_verbosity() -> bool:
    return langchain.verbose


class Chain(Serializable, Runnable[Dict[str, Any], Dict[str, Any]], ABC):
    """Abstract base class for creating structured sequences of calls to components.

    Chains should be used to encode a sequence of calls to components like
    models, document retrievers, other chains, etc., and provide a simple interface
    to this sequence.

    The Chain interface makes it easy to create apps that are:
        - Stateful: add Memory to any Chain to give it state,
        - Observable: pass Callbacks to a Chain to execute additional functionality,
            like logging, outside the main sequence of component calls,
        - Composable: the Chain API is flexible enough that it is easy to combine
            Chains with other components, including other Chains.

    The main methods exposed by chains are:
        - `__call__`: Chains are callable. The `__call__` method is the primary way to
            execute a Chain. This takes inputs as a dictionary and returns a
            dictionary output.
        - `run`: A convenience method that takes inputs as args/kwargs and returns the
            output as a string or object. This method can only be used for a subset of
            chains and cannot return as rich of an output as `__call__`.
    """

    def invoke(
        self,
        input: Dict[str, Any],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        config = config or {}
        return self(
            input,
            callbacks=config.get("callbacks"),
            tags=config.get("tags"),
            metadata=config.get("metadata"),
            **kwargs,
        )

    async def ainvoke(
        self,
        input: Dict[str, Any],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        if type(self)._acall == Chain._acall:
            # If the chain does not implement async, fall back to default implementation
            return await asyncio.get_running_loop().run_in_executor(
                None, partial(self.invoke, input, config, **kwargs)
            )

        config = config or {}
        return await self.acall(
            input,
            callbacks=config.get("callbacks"),
            tags=config.get("tags"),
            metadata=config.get("metadata"),
            **kwargs,
        )

    memory: Optional[BaseMemory] = None
    """Optional memory object. Defaults to None.
    Memory is a class that gets called at the start 
    and at the end of every chain. At the start, memory loads variables and passes
    them along in the chain. At the end, it saves any returned variables.
    There are many different types of memory - please see memory docs 
    for the full catalog."""
    callbacks: Callbacks = Field(default=None, exclude=True)
    """Optional list of callback handlers (or callback manager). Defaults to None.
    Callback handlers are called throughout the lifecycle of a call to a chain,
    starting with on_chain_start, ending with on_chain_end or on_chain_error.
    Each custom chain can optionally call additional callback methods, see Callback docs
    for full details."""
    callback_manager: Optional[BaseCallbackManager] = Field(default=None, exclude=True)
    """Deprecated, use `callbacks` instead."""
    verbose: bool = Field(default_factory=_get_verbosity)
    """Whether or not run in verbose mode. In verbose mode, some intermediate logs
    will be printed to the console. Defaults to `langchain.verbose` value."""
    tags: Optional[List[str]] = None
    """Optional list of tags associated with the chain. Defaults to None.
    These tags will be associated with each call to this chain,
    and passed as arguments to the handlers defined in `callbacks`.
    You can use these to eg identify a specific instance of a chain with its use case.
    """
    metadata: Optional[Dict[str, Any]] = None
    """Optional metadata associated with the chain. Defaults to None.
    This metadata will be associated with each call to this chain,
    and passed as arguments to the handlers defined in `callbacks`.
    You can use these to eg identify a specific instance of a chain with its use case.
    """

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    @property
    def _chain_type(self) -> str:
        raise NotImplementedError("Saving not supported for this chain type.")

    @root_validator()
    def raise_callback_manager_deprecation(cls, values: Dict) -> Dict:
        """Raise deprecation warning if callback_manager is used."""
        if values.get("callback_manager") is not None:
            if values.get("callbacks") is not None:
                raise ValueError(
                    "Cannot specify both callback_manager and callbacks. "
                    "callback_manager is deprecated, callbacks is the preferred "
                    "parameter to pass in."
                )
            warnings.warn(
                "callback_manager is deprecated. Please use callbacks instead.",
                DeprecationWarning,
            )
            values["callbacks"] = values.pop("callback_manager", None)
        return values

    @validator("verbose", pre=True, always=True)
    def set_verbose(cls, verbose: Optional[bool]) -> bool:
        """Set the chain verbosity.

        Defaults to the global setting if not specified by the user.
        """
        if verbose is None:
            return _get_verbosity()
        else:
            return verbose

    @property
    @abstractmethod
    def input_keys(self) -> List[str]:
        """Keys expected to be in the chain input."""

    @property
    @abstractmethod
    def output_keys(self) -> List[str]:
        """Keys expected to be in the chain output."""

    def _validate_inputs(self, inputs: Dict[str, Any]) -> None:
        """Check that all inputs are present."""
        missing_keys = set(self.input_keys).difference(inputs)
        if missing_keys:
            raise ValueError(f"Missing some input keys: {missing_keys}")

    def _validate_outputs(self, outputs: Dict[str, Any]) -> None:
        missing_keys = set(self.output_keys).difference(outputs)
        if missing_keys:
            raise ValueError(f"Missing some output keys: {missing_keys}")

    @abstractmethod
    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        """Execute the chain.

        This is a private method that is not user-facing. It is only called within
            `Chain.__call__`, which is the user-facing wrapper method that handles
            callbacks configuration and some input/output processing.

        Args:
            inputs: A dict of named inputs to the chain. Assumed to contain all inputs
                specified in `Chain.input_keys`, including any inputs added by memory.
            run_manager: The callbacks manager that contains the callback handlers for
                this run of the chain.

        Returns:
            A dict of named outputs. Should contain all outputs specified in
                `Chain.output_keys`.
        """

    async def _acall(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[AsyncCallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        """Asynchronously execute the chain.

        This is a private method that is not user-facing. It is only called within
            `Chain.acall`, which is the user-facing wrapper method that handles
            callbacks configuration and some input/output processing.

        Args:
            inputs: A dict of named inputs to the chain. Assumed to contain all inputs
                specified in `Chain.input_keys`, including any inputs added by memory.
            run_manager: The callbacks manager that contains the callback handlers for
                this run of the chain.

        Returns:
            A dict of named outputs. Should contain all outputs specified in
                `Chain.output_keys`.
        """
        raise NotImplementedError("Async call not supported for this chain type.")

    def __call__(
        self,
        inputs: Union[Dict[str, Any], Any],
        return_only_outputs: bool = False,
        callbacks: Callbacks = None,
        *,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        include_run_info: bool = False,
    ) -> Dict[str, Any]:
        """Execute the chain.

        Args:
            inputs: Dictionary of inputs, or single input if chain expects
                only one param. Should contain all inputs specified in
                `Chain.input_keys` except for inputs that will be set by the chain's
                memory.
            return_only_outputs: Whether to return only outputs in the
                response. If True, only new keys generated by this chain will be
                returned. If False, both input keys and new keys generated by this
                chain will be returned. Defaults to False.
            callbacks: Callbacks to use for this chain run. These will be called in
                addition to callbacks passed to the chain during construction, but only
                these runtime callbacks will propagate to calls to other objects.
            tags: List of string tags to pass to all callbacks. These will be passed in
                addition to tags passed to the chain during construction, but only
                these runtime tags will propagate to calls to other objects.
            metadata: Optional metadata associated with the chain. Defaults to None
            include_run_info: Whether to include run info in the response. Defaults
                to False.

        Returns:
            A dict of named outputs. Should contain all outputs specified in
                `Chain.output_keys`.
        """
        inputs = self.prep_inputs(inputs)
        callback_manager = CallbackManager.configure(
            callbacks,
            self.callbacks,
            self.verbose,
            tags,
            self.tags,
            metadata,
            self.metadata,
        )
        new_arg_supported = inspect.signature(self._call).parameters.get("run_manager")
        run_manager = callback_manager.on_chain_start(
            dumpd(self),
            inputs,
        )
        try:
            outputs = (
                self._call(inputs, run_manager=run_manager)
                if new_arg_supported
                else self._call(inputs)
            )
        except (KeyboardInterrupt, Exception) as e:
            run_manager.on_chain_error(e)
            raise e
        run_manager.on_chain_end(outputs)
        final_outputs: Dict[str, Any] = self.prep_outputs(
            inputs, outputs, return_only_outputs
        )
        if include_run_info:
            final_outputs[RUN_KEY] = RunInfo(run_id=run_manager.run_id)
        return final_outputs

    async def acall(
        self,
        inputs: Union[Dict[str, Any], Any],
        return_only_outputs: bool = False,
        callbacks: Callbacks = None,
        *,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        include_run_info: bool = False,
    ) -> Dict[str, Any]:
        """Asynchronously execute the chain.

        Args:
            inputs: Dictionary of inputs, or single input if chain expects
                only one param. Should contain all inputs specified in
                `Chain.input_keys` except for inputs that will be set by the chain's
                memory.
            return_only_outputs: Whether to return only outputs in the
                response. If True, only new keys generated by this chain will be
                returned. If False, both input keys and new keys generated by this
                chain will be returned. Defaults to False.
            callbacks: Callbacks to use for this chain run. These will be called in
                addition to callbacks passed to the chain during construction, but only
                these runtime callbacks will propagate to calls to other objects.
            tags: List of string tags to pass to all callbacks. These will be passed in
                addition to tags passed to the chain during construction, but only
                these runtime tags will propagate to calls to other objects.
            metadata: Optional metadata associated with the chain. Defaults to None
            include_run_info: Whether to include run info in the response. Defaults
                to False.

        Returns:
            A dict of named outputs. Should contain all outputs specified in
                `Chain.output_keys`.
        """
        inputs = self.prep_inputs(inputs)
        callback_manager = AsyncCallbackManager.configure(
            callbacks,
            self.callbacks,
            self.verbose,
            tags,
            self.tags,
            metadata,
            self.metadata,
        )
        new_arg_supported = inspect.signature(self._acall).parameters.get("run_manager")
        run_manager = await callback_manager.on_chain_start(
            dumpd(self),
            inputs,
        )
        try:
            outputs = (
                await self._acall(inputs, run_manager=run_manager)
                if new_arg_supported
                else await self._acall(inputs)
            )
        except (KeyboardInterrupt, Exception) as e:
            await run_manager.on_chain_error(e)
            raise e
        await run_manager.on_chain_end(outputs)
        final_outputs: Dict[str, Any] = self.prep_outputs(
            inputs, outputs, return_only_outputs
        )
        if include_run_info:
            final_outputs[RUN_KEY] = RunInfo(run_id=run_manager.run_id)
        return final_outputs

    def prep_outputs(
        self,
        inputs: Dict[str, str],
        outputs: Dict[str, str],
        return_only_outputs: bool = False,
    ) -> Dict[str, str]:
        """Validate and prepare chain outputs, and save info about this run to memory.

        Args:
            inputs: Dictionary of chain inputs, including any inputs added by chain
                memory.
            outputs: Dictionary of initial chain outputs.
            return_only_outputs: Whether to only return the chain outputs. If False,
                inputs are also added to the final outputs.

        Returns:
            A dict of the final chain outputs.
        """
        self._validate_outputs(outputs)
        if self.memory is not None:
            self.memory.save_context(inputs, outputs)
        if return_only_outputs:
            return outputs
        else:
            return {**inputs, **outputs}

    def prep_inputs(self, inputs: Union[Dict[str, Any], Any]) -> Dict[str, str]:
        """Validate and prepare chain inputs, including adding inputs from memory.

        Args:
            inputs: Dictionary of raw inputs, or single input if chain expects
                only one param. Should contain all inputs specified in
                `Chain.input_keys` except for inputs that will be set by the chain's
                memory.

        Returns:
            A dictionary of all inputs, including those added by the chain's memory.
        """
        if not isinstance(inputs, dict):
            _input_keys = set(self.input_keys)
            if self.memory is not None:
                # If there are multiple input keys, but some get set by memory so that
                # only one is not set, we can still figure out which key it is.
                _input_keys = _input_keys.difference(self.memory.memory_variables)
            if len(_input_keys) != 1:
                raise ValueError(
                    f"A single string input was passed in, but this chain expects "
                    f"multiple inputs ({_input_keys}). When a chain expects "
                    f"multiple inputs, please call it by passing in a dictionary, "
                    "eg `chain({'foo': 1, 'bar': 2})`"
                )
            inputs = {list(_input_keys)[0]: inputs}
        if self.memory is not None:
            external_context = self.memory.load_memory_variables(inputs)
            inputs = dict(inputs, **external_context)
        self._validate_inputs(inputs)
        return inputs

    @property
    def _run_output_key(self) -> str:
        if len(self.output_keys) != 1:
            raise ValueError(
                f"`run` not supported when there is not exactly "
                f"one output key. Got {self.output_keys}."
            )
        return self.output_keys[0]

    def run(
        self,
        *args: Any,
        callbacks: Callbacks = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        """Convenience method for executing chain.

        The main difference between this method and `Chain.__call__` is that this
        method expects inputs to be passed directly in as positional arguments or
        keyword arguments, whereas `Chain.__call__` expects a single input dictionary
        with all the inputs

        Args:
            *args: If the chain expects a single input, it can be passed in as the
                sole positional argument.
            callbacks: Callbacks to use for this chain run. These will be called in
                addition to callbacks passed to the chain during construction, but only
                these runtime callbacks will propagate to calls to other objects.
            tags: List of string tags to pass to all callbacks. These will be passed in
                addition to tags passed to the chain during construction, but only
                these runtime tags will propagate to calls to other objects.
            **kwargs: If the chain expects multiple inputs, they can be passed in
                directly as keyword arguments.

        Returns:
            The chain output.

        Example:
            .. code-block:: python

                # Suppose we have a single-input chain that takes a 'question' string:
                chain.run("What's the temperature in Boise, Idaho?")
                # -> "The temperature in Boise is..."

                # Suppose we have a multi-input chain that takes a 'question' string
                # and 'context' string:
                question = "What's the temperature in Boise, Idaho?"
                context = "Weather report for Boise, Idaho on 07/03/23..."
                chain.run(question=question, context=context)
                # -> "The temperature in Boise is..."
        """
        # Run at start to make sure this is possible/defined
        _output_key = self._run_output_key

        if args and not kwargs:
            if len(args) != 1:
                raise ValueError("`run` supports only one positional argument.")
            return self(args[0], callbacks=callbacks, tags=tags, metadata=metadata)[
                _output_key
            ]

        if kwargs and not args:
            return self(kwargs, callbacks=callbacks, tags=tags, metadata=metadata)[
                _output_key
            ]

        if not kwargs and not args:
            raise ValueError(
                "`run` supported with either positional arguments or keyword arguments,"
                " but none were provided."
            )
        else:
            raise ValueError(
                f"`run` supported with either positional arguments or keyword arguments"
                f" but not both. Got args: {args} and kwargs: {kwargs}."
            )

    async def arun(
        self,
        *args: Any,
        callbacks: Callbacks = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        """Convenience method for executing chain.

        The main difference between this method and `Chain.__call__` is that this
        method expects inputs to be passed directly in as positional arguments or
        keyword arguments, whereas `Chain.__call__` expects a single input dictionary
        with all the inputs


        Args:
            *args: If the chain expects a single input, it can be passed in as the
                sole positional argument.
            callbacks: Callbacks to use for this chain run. These will be called in
                addition to callbacks passed to the chain during construction, but only
                these runtime callbacks will propagate to calls to other objects.
            tags: List of string tags to pass to all callbacks. These will be passed in
                addition to tags passed to the chain during construction, but only
                these runtime tags will propagate to calls to other objects.
            **kwargs: If the chain expects multiple inputs, they can be passed in
                directly as keyword arguments.

        Returns:
            The chain output.

        Example:
            .. code-block:: python

                # Suppose we have a single-input chain that takes a 'question' string:
                await chain.arun("What's the temperature in Boise, Idaho?")
                # -> "The temperature in Boise is..."

                # Suppose we have a multi-input chain that takes a 'question' string
                # and 'context' string:
                question = "What's the temperature in Boise, Idaho?"
                context = "Weather report for Boise, Idaho on 07/03/23..."
                await chain.arun(question=question, context=context)
                # -> "The temperature in Boise is..."
        """
        if len(self.output_keys) != 1:
            raise ValueError(
                f"`run` not supported when there is not exactly "
                f"one output key. Got {self.output_keys}."
            )
        elif args and not kwargs:
            if len(args) != 1:
                raise ValueError("`run` supports only one positional argument.")
            return (
                await self.acall(
                    args[0], callbacks=callbacks, tags=tags, metadata=metadata
                )
            )[self.output_keys[0]]

        if kwargs and not args:
            return (
                await self.acall(
                    kwargs, callbacks=callbacks, tags=tags, metadata=metadata
                )
            )[self.output_keys[0]]

        raise ValueError(
            f"`run` supported with either positional arguments or keyword arguments"
            f" but not both. Got args: {args} and kwargs: {kwargs}."
        )

    def dict(self, **kwargs: Any) -> Dict:
        """Dictionary representation of chain.

        Expects `Chain._chain_type` property to be implemented and for memory to be
            null.

        Args:
            **kwargs: Keyword arguments passed to default `pydantic.BaseModel.dict`
                method.

        Returns:
            A dictionary representation of the chain.

        Example:
            .. code-block:: python

                chain.dict(exclude_unset=True)
                # -> {"_type": "foo", "verbose": False, ...}
        """
        if self.memory is not None:
            raise ValueError("Saving of memory is not yet supported.")
        _dict = super().dict(**kwargs)
        _dict["_type"] = self._chain_type
        return _dict

    def save(self, file_path: Union[Path, str]) -> None:
        """Save the chain.

        Expects `Chain._chain_type` property to be implemented and for memory to be
            null.

        Args:
            file_path: Path to file to save the chain to.

        Example:
            .. code-block:: python

                chain.save(file_path="path/chain.yaml")
        """
        # Convert file to Path object.
        if isinstance(file_path, str):
            save_path = Path(file_path)
        else:
            save_path = file_path

        directory_path = save_path.parent
        directory_path.mkdir(parents=True, exist_ok=True)

        # Fetch dictionary to save
        chain_dict = self.dict()

        if save_path.suffix == ".json":
            with open(file_path, "w") as f:
                json.dump(chain_dict, f, indent=4)
        elif save_path.suffix == ".yaml":
            with open(file_path, "w") as f:
                yaml.dump(chain_dict, f, default_flow_style=False)
        else:
            raise ValueError(f"{save_path} must be json or yaml")

    def apply(
        self, input_list: List[Dict[str, Any]], callbacks: Callbacks = None
    ) -> List[Dict[str, str]]:
        """Call the chain on all inputs in the list."""
        return [self(inputs, callbacks=callbacks) for inputs in input_list]
