
# auto_cards

Simple cli tool for composing flashcards. Finds definition to a list of words.




## Installation

Recommended installation method is through [pip](https://pip.pypa.io/en/stable/)

```bash
  pip install git+https://github.com/Bit38/auto_cards.git
```

After installing just use:
```bash
auto_cards
```

Alternatively, you can use [uv][https://docs.astral.sh/uv/]:
```bash
uvx --from git+https://github.com/Bit38/auto_cards.git auto_cards
```
    
## Usage

```bash
Usage: auto_cards [-h] [-d INPUT_DELIMITER] [-q INPUT_QUOTECHAR]
                  [--output-delimeter OUTPUT_DELIMETER]
                  [--output-quotechar OUTPUT_QUOTECHAR] [--config CONFIG_PARAMS]
                  [-s SOURCES]
                  input output

Finds defintion for a word list

Positional Arguments:
  input                 CSV file with one (word) or two columns (word, part of speech)
  output                Output csv file with flashcards

Options:
  -h, --help            show this help message and exit
  -d, --input-delimiter INPUT_DELIMITER
                        CSV delimiter for `input`
  -q, --input-quotechar INPUT_QUOTECHAR
                        CSV quotechar for `input`
  --output-delimeter OUTPUT_DELIMETER
                        CSV delimeter for `output`
  --output-quotechar OUTPUT_QUOTECHAR
                        CSV quotechar for `input`
  --config CONFIG_PARAMS
                        Sepcifies config values for any source. Expected format {source
                        name/id}.{value name/id}={value}
  -s, --sources SOURCES
                        Define what sources and in what order to use (by default "wordnet")
```

The script requires a CSV file with one or two columns. The first column (mandatory) should contain the word or expression to be defined, while the second column (optional) specifies the part of speech. 

For now following sources and config values are supported:
* `wordnet` - uses wordnet for looking up definitions
    * `wordnet.lexicon` - what lexicon to use. Should be either a *url* or [*id*](https://github.com/goodmami/wn#available-wordnets). By default: `oewn:2024` (Open English Wordnet)
    * `wordnet.default_pos` - what part of speech should be used if one is not provided
* `ollama` - uses local AI to *generate* definitions
    * `ollama.server` - url to ollama server (default: `http://localhost:11434`)
    * `ollama.model` - what ai model to use (default: `gemma3:4b`)

### Sample input files
```csv
serendipity
break a leg
ephemeral
cold shoulder
```

```csv
bark,noun
bark,verb
fast,adjective
fast,adverb
set,verb
```

## License

This project is licensed under [MIT](./LICENSE)


