import argparse
import csv
from typing import Mapping

import httpx
from rich.console import Console
from rich.progress import track

from .abc_definition_source import AbstractDefinitionSrc, ConfigOption, prepare_config_data
from .args_parser import ConfigDataRaw, ConfigPluginAction, RichArgumentParser, SourcesAction
from .ollama_src import OllamaSrc
from .wordnet_src import WordNetSrc

console = Console()
parser = RichArgumentParser(console, description="Finds defintion for a word list")
parser.add_argument(
    "input",
    help="CSV file with one (word) or two columns (word, part of speech)",
    type=argparse.FileType("r"),
)
parser.add_argument(
    "output", help="Output csv file with flashcards", type=argparse.FileType("w")
)
parser.add_argument(
    "-d", "--input-delimiter", help="CSV delimiter for `input`", default=","
)
parser.add_argument(
    "-q", "--input-quotechar", help="CSV quotechar for `input`", default='"'
)
parser.add_argument(
    "--output-delimeter", help="CSV delimeter for `output`", default=","
)
parser.add_argument("--output-quotechar", help="CSV quotechar for `input`", default='"')
parser.add_argument(
    "--config",
    action=ConfigPluginAction,
    help="Sepcifies config values for any source. Expected format {source name/id}.{value name/id}={value}",
    dest="config_params",
)
parser.add_argument(
    "-s",
    "--sources",
    action=SourcesAction,
    help="Define what sources and in what order to use",
)

SOURCES: dict = {OllamaSrc.name: OllamaSrc, WordNetSrc.name: WordNetSrc}
DEFAULT_SRCS = [WordNetSrc.name]


def validate_config(config: ConfigDataRaw, used_sources: list[str]):
    for source, vals in config.items():
        if source.lower() not in SOURCES:
            console.print(
                f"[dark_orange][bold]WARNING[/bold] Config value for unknown source: {source}"
            )
            continue
        if source.lower() not in used_sources:
            console.print(
                f"[dark_orange][bold]WARNING[/bold] Config value for unused source: {source}"
            )
            continue

        config_info: Mapping[str, ConfigOption] = SOURCES[source.lower()].config_values

        for name, _val in vals.items():
            if name.lower() not in config_info.keys():
                parser.error(f"Invalid config option: {source}.{name}")

            # config_option = config_info[name.lower()]
            # TODO: Verify config_option.cli_type


def prepare_sources(used_sources: list[str], config: ConfigDataRaw) -> list[AbstractDefinitionSrc]:
    prepared_sources = []
    session = httpx.Client()

    for src in used_sources:
        src_class = SOURCES[src.lower()]
        config_data = prepare_config_data(src_class.config_values)
        config_data.update(config.get(src_class.name, {}))

        source: AbstractDefinitionSrc = src_class(console, session)
        if not source.setup(config_data):
            parser.error(f"Failed to configure {source.name}! Got this error message: [italic]{source.error_msg}[/italic]")

        prepared_sources.append(source)

    return prepared_sources

def main():
    args = parser.parse_args()
    console.print(args)

    # Validate sources
    sources = args.sources or DEFAULT_SRCS
    if not all((src in SOURCES for src in sources)):
        invalid_srcs = tuple(filter(lambda src: src not in SOURCES, sources))
        parser.error(
            f"Invalid source{'s' if len(invalid_srcs) > 1 else ''}: {', '.join(invalid_srcs)}"
        )

    validate_config(args.config_params, sources)

    sources = prepare_sources(sources, args.config_params)
    console.print("[green]Sources successfully configured!")
    console.print("Sources will be used in the following order:")
    for nr, src in enumerate(sources):
        console.print(f"    {nr+1}. {src.name}")

    found = 0
    failed = 0
    with args.input, args.output:
        reader = csv.reader(
            track(args.input, console=console),
            delimiter=args.input_delimiter,
            quotechar=args.input_quotechar,
        )
        writer = csv.writer(
            args.output,
            delimiter=args.output_delimeter,
            quotechar=args.output_quotechar,
        )
        for line in reader:
            defi = []
            for source in sources:
                if len(line) > 1:
                    defi = source.find_definition(line[0], line[1])
                else:
                    defi = source.find_definition(line[0], None)

                if len(defi) > 0:
                    break
                

            if len(defi) == 0:
                console.print(f"[dark_orange]WARNING Failed to find definition for: [italic]{line[0]}[/italic]")
                failed += 1
                continue
            writer.writerow((line[0], defi[0]))
            found += 1
    console.print(
        f"[blue][INFO] [green]Found {found} definition.[/green] [red]{failed} word{' do ' if failed == 1 else 's does'} not have defintion."
    )

    for src in sources:
        if not src.cleanup():
            console.print(f"[dark_orange]WARNING {src.name} failed to cleanup! Got this error message: [italic]{src.error_msg}[/italic]")

