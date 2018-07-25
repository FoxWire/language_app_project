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

    def ask_question(self):

        sentence = self.sentence.sentence
        close_deletion = sentence.replace(self.chunk, '_' * len(self.chunk))
        spaces = ' ' * (len(close_deletion.split("_")[0].strip()) - 1)
        question = "{}\n{}<{}>".format(close_deletion, spaces, self.chunk_translation)
        return question

    def give_answer(self, answer):
        return answer.strip() == self.chunk.strip(), self.chunk.strip()

    def _format_tree_string(self, tree_string):
        # remove the newlines and whitespace that comes with tree string
        return "".join(tree_string.split())

    def __str__(self):
        s = "\nsentence: {}\n chunk: {}\n chunk translation: {}\n tree_string: {}\n".format(
            self.sentence, self.chunk, self.chunk_translation, self.tree_string)
        return s


