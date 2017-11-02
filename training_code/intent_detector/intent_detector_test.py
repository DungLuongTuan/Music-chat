from sklearn import svm
import numpy as np 
import gensim
import pickle

intents = ['inform', 'other', 'search', 'show']

def main():
	### text
	text = 'mở cho mình bài <title>?'
	### load model
	f = open('../../model/intent_detector/intent_model.pkl', 'rb')
	classify = pickle.load(f)
	### load doc2vec model
	doc2vec = gensim.models.doc2vec.Doc2Vec.load('../../model/doc2vec/best.doc2vec.model')
	### predict
	docvec = doc2vec.infer_vector(text)
	predict = classify.predict_proba(docvec.reshape(1, -1))
	# print(intents[np.argmax(predict[0])])
	print(predict)

if __name__ == '__main__':
	main()

#[[ 0.37994462  0.05447777  0.38030031  0.09745914  0.02523768  0.06258048]]