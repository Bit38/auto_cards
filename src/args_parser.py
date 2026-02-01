import argparse
import re
from typing import Any, Callable, Iterable, Mapping, NoReturn, Sequence

from rich.console import Console
from rich_argparse import RichHelpFormatter
from typing_extensions import override

CONFIG_ARGS_REGEX = re.compile(r"^(\w+).(\w+)\s*=\s*(.+)$")


class RichArgumentParser(argparse.ArgumentParser):
    def __init__(self, console: Console, *args, **kwargs) -> None:
        self._console = console
        super().__init__(*args, **kwargs)

    def _get_formatter(self):
        formatter = RichHelpFormatter(prog=self.prog, console=self._console)
        return formatter

    @override
    def error(self, message: str) -> NoReturn:
        self.print_usage()
        with self._console.capture() as cap:
            self._console.print(
                f"[{self._get_formatter().styles['argparse.prog']}]{self.prog}[/] [red][bold]Error:[/bold] {message}"
            )
        self.exit(2, cap.get())

type ConfigDataRaw = Mapping[str, Mapping[str, str]]
class ConfigPluginAction(argparse.Action):
    def __init__(
        self,
        option_strings: Sequence[str],
        dest: str,
        nargs: int | str | None = None,
        const: Any | None = None,
        default: Any | str | None = None,
        type: Callable[[str], Any] | argparse.FileType | None = None,
        choices: Iterable[Any] | None = None,
        required: bool = False,
        help: str | None = None,
        metavar: str | tuple[str, ...] | None = None,
    ) -> None:
        super().__init__(
            option_strings,
            dest,
            nargs,
            const,
            default or {},
            type,
            choices,
            required,
            help,
            metavar,
        )

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: str | Sequence[Any] | None,
        option_string: str | None = None,
    ) -> None:
        if not isinstance(values, str):
            return

        conf_params: dict = getattr(namespace, "config_params", {})
        m = CONFIG_ARGS_REGEX.match(values)
        if m is None:
            parser.error(
                f'{option_string} expected a value in format {{source id/name}}.{{value name}}={{value}}, but got "{values}"'
            )
        groups = m.groups()
        if conf_params.get(groups[0], None) is None:
            conf_params[groups[0]] = {}

        conf_params[groups[0]][groups[1]] = groups[2]

        setattr(namespace, "config_params", conf_params)

    def format_usage(self) -> str:
        return "Specify config value for any source. Expected format: {source id/name}.{value name}={value}"


class SourcesAction(argparse.Action):
    def __init__(
        self,
        option_strings: Sequence[str],
        dest: str,
        nargs: int | str | None = None,
        const: Any | None = None,
        default: Any | str | None = None,
        type: Callable[[str], Any] | argparse.FileType | None = None,
        choices: Iterable[Any] | None = None,
        required: bool = False,
        help: str | None = None,
        metavar: str | tuple[str, ...] | None = None,
    ) -> None:
        super().__init__(
            option_strings,
            dest,
            nargs,
            const,
            default,
            type,
            choices,
            required,
            help,
            metavar,
        )

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: str | Sequence[Any] | None,
        option_string: str | None = None,
    ) -> None:
        if not isinstance(values, str):
            return

        conf_params: list[str] = getattr(namespace, "sources", []) or []
        to_add = [part.strip() for part in values.split(",")]

        setattr(namespace, "sources", conf_params + to_add)
