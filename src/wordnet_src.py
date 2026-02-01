from typing import Any, Mapping, override

import wn
import wn.constants

from .abc_definition_source import (
    AbstractDefinitionSrc,
    ConfigOption,
    classmethodproperty,
)

POS_TRANSLATION = {
    "v": wn.constants.VERB,
    "V": wn.constants.VERB,
    "n": wn.constants.NOUN,
    "N": wn.constants.NOUN,
    "adv": wn.constants.ADVERB,
    "adj": wn.constants.ADJECTIVE,
    "phrase": wn.constants.PHRASE,
}


class WordNetSrc(AbstractDefinitionSrc):
    @classmethodproperty
    @override
    def name(cls) -> str:
        return "wordnet"

    @classmethodproperty
    @override
    def description(cls) -> str:
        return """Uses wordnet (https://en.wikipedia.org/wiki/WordNet) to find definitions.
By default uses Open English Wordnet (https://en-word.net/).
To use diffrent one use --config wordnet.lexicon={id} where {id} is url to the wordnet.
Alternatively, you can use identifiers which can be found at https://github.com/goodmami/wn"""

    @classmethodproperty
    @override
    def config_values(cls) -> Mapping[str, ConfigOption]:
        return {
            "lexicon": ConfigOption(
                "oewn:2024", str, "What lexicon to use for definitions"
            ),
            "default_pos": ConfigOption(
                None, str, "What part of speech should be default if not provided"
            ),
        }

    @override
    def setup(
        self,
        config: Mapping[str, Any],
    ) -> bool:
        if len(wn.lexicons(lexicon=config["lexicon"])) <= 0:
            try:
                wn.download(config["lexicon"])
            except wn.Error as err:
                self._set_error_msg(f"Error while downloading: {err}")
                return False

        self._lexicon = wn.Wordnet(config["lexicon"])
        self._default_pos = config["default_pos"]
        return True

    @override
    def find_definition(self, word: str, pos: str | None) -> tuple[str, ...]:
        final_pos = (
            POS_TRANSLATION.get(pos, None) if pos is not None else self._default_pos
        )
        synsets = self._lexicon.synsets(word, pos=final_pos)

        if synsets is None or len(synsets) == 0:
            return ()
        return tuple(synsets[0].definitions())

    @override
    def cleanup(self) -> bool:
        return True 
