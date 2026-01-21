# Auto cards
Simple cli tool for composing English flashcards (word -> definition).

## Installation
1. Clone this git repo
```bash
git clone https://github.com/Bit38/auto_cards.git
```
2. Run with uv 
```bash
uv run src/auto_cards.py
```

## Usage 
```bash
usage: auto_cards.py [-h] [-d INPUT_DELIMITER] [-q INPUT_QUOTECHAR] [--output-delimeter OUTPUT_DELIMETER] [--output-quotechar OUTPUT_QUOTECHAR] [-l WORDNET_LEXICON] [-s OLLAMA_SERVER]
               [-m OLLAMA_MODEL] [--ollama]
               input output

Finds defintion for a word list

positional arguments:
  input                 CSV file with one (word) or two columns (word, part of speech)
  output                Output csv file with flashcards

options:
  -h, --help            show this help message and exit
  -d INPUT_DELIMITER, --input-delimiter INPUT_DELIMITER
                        CSV delimiter for `input`
  -q INPUT_QUOTECHAR, --input-quotechar INPUT_QUOTECHAR
                        CSV quotechar for `input`
  --output-delimeter OUTPUT_DELIMETER
                        CSV delimeter for `output`
  --output-quotechar OUTPUT_QUOTECHAR
                        CSV quotechar for `input`
  -l WORDNET_LEXICON, --wordnet-lexicon WORDNET_LEXICON
                        Which wordnet lexicon to use
  -s OLLAMA_SERVER, --ollama-server OLLAMA_SERVER
                        Url of ollama server
  -m OLLAMA_MODEL, --ollama-model OLLAMA_MODEL
                        Which local AI model to use
  --ollama              Use AI (ollama) if wordnet does not have defintion
```

## License
This project is licensed under [MIT License](./LICENSE)
