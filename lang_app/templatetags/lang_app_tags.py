from django import template
from lang_app.models import Question
import re

register = template.Library()


@register.simple_tag
def get_longest_length(question_pk):
    # Get the longest of the two question chunks.
    question = Question.objects.get(pk=question_pk)
    items = [question.chunk, question.chunk_translation, "Translate into English"]
    return len(sorted(items, key=lambda x: len(x), reverse=True)[0])


# Removes non-alphanumeric characters from a string
# This is needed for the java script hint updater.
@register.simple_tag
def remove_non_alpha(lem_string):
    return re.sub(r'[\W^-]', '', lem_string)
