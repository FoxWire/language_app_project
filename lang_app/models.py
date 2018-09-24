from django.db import models


# Create your models here.

class Sentence(models.Model):

    sentence = models.CharField(max_length=1024, unique=True)

    def __str__(self):
        return self.sentence


class Card(models.Model):

    sentence = models.ForeignKey('Sentence', default=None, blank=True, related_name='cards', on_delete=models.CASCADE)
    chunk = models.CharField(max_length=1024)
    chunk_translation = models.CharField(max_length=1024)
    tree_string = models.CharField(max_length=1024)
    similar_cards = models.CharField(max_length=128, default='this')

    def ask_question(self):

        # sentence = self.sentence.sentence
        # close_deletion = sentence.replace(self.chunk, '_' * len(self.chunk))
        # spaces = ' ' * (len(close_deletion.split("_")[0].strip()) - 1)
        # question = "{}\n{}<{}>".format(close_deletion, spaces, self.chunk_translation)

        # In order to use the question in the html, we need to sentence, split on the chunk
        # we will return both parts and the chunk

        sentence = self.sentence.sentence
        data = {'b': self.chunk_translation}

        if sentence.startswith(self.chunk):
            data['a'] = None
            data['c'] = sentence.replace(self.chunk, '')
        elif sentence.endswith(self.chunk):
            data['a'] = sentence.replace(self.chunk, '')
            data['c'] = None
        else:
            parts = sentence.split(self.chunk)
            data['a'] = parts[0]
            data['c'] = parts[1]

        return data

    def give_answer(self, answer, score=False):
        return answer.strip().lower() == self.chunk.strip().lower(), self.chunk.strip()

    def _format_tree_string(self, tree_string):
        # remove the newlines and whitespace that comes with tree string
        return "".join(tree_string.split())

    def __str__(self):
        s = "\nsentence: {}\n chunk: {}\n chunk translation: {}\n tree_string: {}\n".format(
            self.sentence, self.chunk, self.chunk_translation, self.tree_string)
        return s

