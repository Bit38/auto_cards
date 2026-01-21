import argparse
import csv
from collections import namedtuple

import ollama
import wn
import wn.constants
from tqdm import tqdm

OllamaConfig = namedtuple("OllamaConfig", ("host", "model", "client"))

parser = argparse.ArgumentParser(description="Finds defintion for a word list")
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
    "-l", "--wordnet-lexicon", help="Which wordnet lexicon to use", default="oewn:2024"
)
parser.add_argument(
    "-s",
    "--ollama-server",
    help="Url of ollama server",
    default="http://localhost:11434",
)
parser.add_argument(
    "-m", "--ollama-model", help="Which local AI model to use", default="gemma3:4b"
)
parser.add_argument(
    "--ollama",
    help="Use AI (ollama) if wordnet does not have defintion",
    action="store_true",
)

# Recoginsed POS
POS_TRANSLATION = {
    "v": wn.constants.VERB,
    "V": wn.constants.VERB,
    "n": wn.constants.NOUN,
    "N": wn.constants.NOUN,
    "adv": wn.constants.ADVERB,
    "adj": wn.constants.ADJECTIVE,
    "phrase": wn.constants.PHRASE,
}


def download_lexicon(name: str):
    lexicons = [lexicon.id for lexicon in wn.lexicons()] + [
        f"{lexicon.id}:{lexicon.version}" for lexicon in wn.lexicons()
    ]
    if not name in lexicons:
        print(f"[INFO] Lexicon {name} not found. Downloading...")
        p = wn.download(name)
        print(f"[INFO] Lexicon {name} downloaded to: {p}")


def wordnet_lookup(word: str, pos: None | str, wn: wn.Wordnet) -> str | None:
    final_pos = POS_TRANSLATION.get(pos, None) if pos is not None else None
    synsets = wn.synsets(word, pos=final_pos)

    if synsets is None or len(synsets) == 0:
        return None
    return synsets[0].definition()


SYSTEM_MESSAGE = """You task is to provide a definition to a word or idiom. The user will provide you with the word. Sometimes requests will also include part of speech e.g.:
- adj -> adjective
- adv -> adverb
- V -> verb
- n -> noun
- idiom
- phr. v -> phrasal verb
The part of speech will usually be separated from the word with comma or semicolon.
There may be situations where user provides corrupted or invalid or does not provide part of speech at all. In such case try to guess what part of speech is the expression provided.
You shall not respond with anything else that the definition.
Good example of reponses are:

1.
  User: glue, V
  Assistant: fasten or join with or as if with glue
2. 
  User: Beer gut
  Assistant: A prominent, protruding belly caused by excessive consumption of beer.
3.
  User: Pull the woll over someone; idiom
  Assistant: To deceive or fool someone.
"""


def ollama_lookup(
    word: str, pos: None | str, ollama_config: OllamaConfig
) -> str | None:
    try:
        pos_str = "" if pos is None else f"; {pos}"
        resp = ollama_config.client.chat(
            model=ollama_config.model,
            messages=[
                {"role": "system", "content": SYSTEM_MESSAGE},
                {"role": "user", "content": word + pos_str},
            ],
            stream=False,
        )
    except ConnectionError:
        print("[ERROR] Failed to connect to ollama server!")
        return None
    except ollama.ResponseError:
        print("[ERROR] Invalid reponse from ollama server!")
        return None
    except ollama.RequestError:
        print("[ERROR] Invalid request was sent!")
        return None

    return resp["message"]["content"]


def find_definition(
    word: str, pos: None | str, wn: wn.Wordnet, ollama_config: OllamaConfig
) -> str | None:
    wd = wordnet_lookup(word, pos, wn)
    if wd is not None:
        return wd

    if ollama_config.client is not None:
        return ollama_lookup(word, pos, ollama_config)

    return None


def main():
    args = parser.parse_args()

    download_lexicon(args.wordnet_lexicon)
    wordnet = wn.Wordnet(args.wordnet_lexicon)

    ollama_client = None
    if args.ollama:
        ollama_client = ollama.Client(args.ollama_server)
    ollama_config = OllamaConfig(args.ollama_server, args.ollama_model, ollama_client)

    found = 0
    failed = 0
    with args.input, args.output:
        reader = csv.reader(
            tqdm(args.input),
            delimiter=args.input_delimiter,
            quotechar=args.input_quotechar,
        )
        writer = csv.writer(
            args.output,
            delimiter=args.output_delimeter,
            quotechar=args.output_quotechar,
        )
        for line in reader:
            if len(line) > 1:
                defi = find_definition(line[0], line[1], wordnet, ollama_config)
            else:
                defi = find_definition(line[0], None, wordnet, ollama_config)

            if defi is None:
                print("[WARNING] Failed to find definition for:", line[0])
                failed += 1
                continue
            writer.writerow((line[0], defi))
            found += 1
    print(
        f"[INFO] Found {found} definition. {failed} word{' do ' if failed == 1 else 's does'} not have defintion."
    )


if __name__ == "__main__":
    main()
