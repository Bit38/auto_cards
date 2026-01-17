import argparse
import csv

import wn
import wn.constants

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


def find_definition(word: str, pos: None | str, wn: wn.Wordnet) -> str | None:
    final_pos = POS_TRANSLATION.get(pos, None) if pos is not None else None
    synsets = wn.synsets(word, pos=final_pos)

    if synsets is None or len(synsets) == 0:
        return None
    return synsets[0].definition()


def main():
    args = parser.parse_args()

    download_lexicon(args.wordnet_lexicon)
    wordnet = wn.Wordnet(args.wordnet_lexicon)

    found = 0
    failed = 0
    with args.input, args.output:
        reader = csv.reader(
            args.input, delimiter=args.input_delimiter, quotechar=args.input_quotechar
        )
        writer = csv.writer(
            args.output,
            delimiter=args.output_delimeter,
            quotechar=args.output_quotechar,
        )
        for line in reader:
            if len(line) > 1:
                defi = find_definition(line[0], line[1], wordnet)
            else:
                defi = find_definition(line[0], None, wordnet)

            if defi is None:
                print("[ERROR] Failed to find definition for:", line[0])
                failed += 1
                continue
            writer.writerow((line[0], defi))
            found += 1
    print(
        f"[INFO] Found {found} definition. {failed} word{' do ' if failed == 1 else 's does'} not have defintion."
    )


if __name__ == "__main__":
    main()
