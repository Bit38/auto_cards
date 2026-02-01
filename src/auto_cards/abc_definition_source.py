from abc import ABCMeta, abstractmethod
from collections import namedtuple
from typing import Any, Callable, Mapping

from httpx import Client
from rich.console import Console


class classmethodproperty:
    def __init__(self, func: Callable) -> None:
        self._getter = func

    def __get__(self, _instance, cls):  # _instance is unused
        return self._getter(cls)


ConfigOption = namedtuple("ConfigOption", ("default", "cli_type", "description"))
type ConfigOptionDict = Mapping[str, ConfigOption]
type ConfigData = Mapping[str, Any]

class AbstractDefinitionSrc(metaclass=ABCMeta):
    def __init__(self, console: Console, session: Client, raise_on_error=False) -> None:
        self.raise_on_error = raise_on_error
        self._err_msg = None
        self.session = session
        self.console = console

    def __repr__(self) -> str:
        return f"<Source {self.name}>"

    @classmethodproperty
    @abstractmethod
    def name(cls) -> str:
        """Human‑readable name of the source (e.g. ``"worndet"``)."""
        ...

    @classmethodproperty
    @abstractmethod
    def description(cls) -> str:
        """Short description explaining how the source works."""
        ...

    @classmethodproperty
    @abstractmethod
    def config_values(cls) -> ConfigOptionDict: 
        """
        Mapping of configuration values that are expected to be passed to the
        ``setup`` method.

        Returns
        -------
        ConfigOptionDict
            A mapping where each key is the name of a configuration
            option and each value is a :class:`ConfigOption` namedtuple containing:

            * **default** – The default value for the option.
            * **cli_type** – The expected type (not used)
            * **description** – Human‑readable description of the option’s purpose. (not used)

        Example
        -------
        >>> MyClass.config_values
        {
            "lexicon": ConfigOption(
                default="oewn:2024",
                cli_type="string",
                description="What lexicon to use"
            ),
        }

        Notes
        -----
        * The **cli_type** and **description** properties of :class:`ConfigOption` 
          are currently unused, but will be in the future 
        """
        ...

    @property
    def error_msg(self) -> str | None:
        """
        Retrieve the last error message recorded by the source.

        Returns
        -------
        str | None
            The stored error message, or ``None`` if no error has been set.
        """
        return self._err_msg

    def _set_error_msg(self, msg: str | None) -> str | None:
        self._err_msg = msg
        if self._err_msg is not None and self.raise_on_error:
            raise RuntimeError(f"{self.name} failed: {msg}")
        return msg

    @abstractmethod
    def setup(
        self,
        config: ConfigData,
    ) -> bool:
        """
        Prepare the source for use.

        Implementations should validate values provided in ``config`` and
        initialise any required connections.

        Parameters
        ----------
        config : ConfigData
            A mapping with configuration values that were defined in :meth:`config_values`
            `cli_type` is ignored and all values are passed as strings

        Returns
        -------
        bool
            ``True`` if the source was successfully initialised, ``False``
            otherwise.  On failure error message should be set using
            :meth:`_set_error_msg`

        Raises
        ------
        RuntimeError
            If ``self.raise_on_error`` is ``True`` and source fails to initialise. 
        """
        ...

    @abstractmethod
    def find_definition(self, word: str, pos: str | None) -> tuple[str, ...]: 
        """
        Look up definitions for a given word.

        Parameters
        ----------
        word : str
            The lexical item to look up.
        pos : str | None
            Optional part‑of‑speech tag. May be ignored.

        Returns
        -------
        tuple[str, ...]
            One or more definition strings. An empty tuple indicates that the
            definition could not be found.

        Raises
        ------
        RuntimeError
            If ``self.raise_on_error`` is ``True`` and an error occurs while
            querying the backend.
        """

    @abstractmethod
    def cleanup(
        self,
    ) -> bool:
        """
        Release any connections, resources held by the source 

        Returns
        -------
        bool
            ``True`` if cleanup succeeded, ``False`` otherwise.  Error message 
            should be set by :meth:`_set_err_msg`.
        """
        ...

def prepare_config_data(conf: ConfigOptionDict) -> dict[str, Any]:
    out = dict()
    for name, opt in conf.items():
        out[name] = opt.default
    return out
