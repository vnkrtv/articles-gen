import os
from typing import Generator
import markovify


class MarkovModel:

    model: markovify.Text

    def __init__(self, train_input, model=None, state_size=2):
        if model:
            self.model = model
        elif isinstance(train_input, str):
            self.model = markovify.NewlineText(train_input, state_size=state_size)
        elif isinstance(train_input, Generator):
            self.model = markovify.Text(next(train_input), state_size=state_size)
            for sent in train_input:
                self.model = markovify.combine([self.model, markovify.Text(sent, state_size=state_size)])

    def compile(self):
        self.model.compile(inplace=True)
        return self

    @classmethod
    def load(cls, model_name='model1.0-habr-10000.json', models_path='models/markov/bin'):
        with open(os.path.join(models_path, model_name), 'r') as f:
            model_json = f.read()
        model = markovify.Text.from_json(model_json)
        return cls(model=model)

    def save(self, model_name):
        with open(f'models/markov/bin/{model_name}.json', 'w') as f:
            f.write(self.model.to_json())

    def generate_sample(self, beginning: str) -> str:
        return self.model.make_sentence_with_start(beginning)

    def get_phrases_for_t9(self, beginning: str, first_words_count=1, count=20) -> list:
        phrases = set()
        for i in range(count):
            phrase = self.generate_sample(beginning)
            if phrase:
                words_list = phrase.split()
                if len(words_list) > 1:
                    phrases.add(" ".join(words_list[first_words_count:]))
        return list(phrases)

