from gensim.models import KeyedVectors


# load the google word2vec model
filename = '~/Documents/masters_project/GoogleNews-vectors-negative300.bin'
model = KeyedVectors.load_word2vec_format(filename, binary=True, limit=500000)
# model.init_sims(replace=True)
# calculate: (king - man) + woman = ?
# result = model.most_similar(positive=['woman', 'king'], negative=['man'], topn=1)
# print(result)

# a = "We like to chat with eachother."
# b = "We like to jog with eachother."
# x = model.wmdistance(a.split(), b.split())
# print(x)

x = model['to']
# import pdb; pdb.set_trace()