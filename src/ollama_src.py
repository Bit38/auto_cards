from typing import Any, Mapping, override

import ollama

from .abc_definition_source import (
    AbstractDefinitionSrc,
    ConfigOption,
    classmethodproperty,
)

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


class OllamaSrc(AbstractDefinitionSrc):
    @classmethodproperty
    def name(cls) -> str:
        return "ollama"

    @classmethodproperty
    def description(cls) -> str:
        return "Uses AI through ollama server to generate definitions"

    @classmethodproperty
    def config_values(cls) -> Mapping[str, ConfigOption]:
        return {
            "server": ConfigOption(
                "http://localhost:11434", "uri", "Ollama server url"
            ),
            "model": ConfigOption("gemma3:4b", str, "AI model to use"),
        }

    @override
    def setup(self, config: Mapping[str, Any]) -> bool:
        self._client = ollama.Client(config["server"])
        self._model = config["model"]

        try:
            models = [str(model.model) for model in self._client.list().models]
            if self._model not in models:
                models_text = "\n - ".join(models)
                self._set_error_msg(
                    f'Invalid model "{self._model}"! Available:\n - {models_text}'
                )
                return False
        except ConnectionError:
            self._set_error_msg("Failed to connect to ollama server!")
            return False
        except ollama.ResponseError:
            self._set_error_msg("Invalid reponse from ollama server!")
            return False

        return True

    @override
    def find_definition(self, word: str, pos: str | None) -> tuple[str, ...]:
        try:
            pos_str = "" if pos is None else f"; {pos}"
            resp = self._client.chat(
                model=self._model,
                messages=[
                    {"role": "system", "content": SYSTEM_MESSAGE},
                    {"role": "user", "content": word + pos_str},
                ],
                stream=False,
            )
        except ConnectionError:
            self._set_error_msg("[ERROR] Failed to connect to ollama server!")
            return ()
        except ollama.ResponseError:
            self._set_error_msg("[ERROR] Invalid reponse from ollama server!")
            return ()
        except ollama.RequestError:
            self._set_error_msg("[ERROR] Invalid request was sent!")
            return ()

        return (resp["message"]["content"],)

    @override
    def cleanup(self) -> bool:
        return True 
