'''
This module will read in a file and convert it to a list of sentences. 

Notes: At the moment this deals with unicode characters, because the sample text we took from the guardian 
was in that format. You might want to make sure at some point that it can cope with all formats.
'''

from nltk.tokenize import sent_tokenize


class SentenceReader():

    def get_sentences(self, path_to_file):
        lines = []
        with open(path_to_file, 'r', encoding='utf-8') as input:
            for line in input:
                line = line.replace(u'’', "'")
                line = line.encode('ascii', 'ignore')
                line = line.decode()
                if line != '\n':
                    lines.append(line.replace('\n', ''))

        sentence_list = []
        for line in lines:
            for sentence in sent_tokenize(line):
                sentence_list.append(sentence)

        return sentence_list


if __name__ == "__main__":
    sr = SentenceReader()
    for sentence in sr.get_sentences('exper.txt'):
        print(sentence)


