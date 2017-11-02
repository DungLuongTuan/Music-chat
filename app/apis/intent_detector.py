from sklearn import svm
import numpy as np 
import gensim
import pickle

class IntentDetector(object):
	"""

	"""
	def __init__(self, doc2vec):
		self.doc2vec = doc2vec
		self.intents = ['change', 'inform', 'other', 'search', 'show']
		self.load_model()

	def load_model(self):
		f = open('./model/intent_detector/intent_model.pkl', 'rb')
		self.classify = pickle.load(f)
		f.close()

	def predict(self, text):
		vec = self.doc2vec.infer_vector(text.lower())
		predict = self.classify.predict_proba(vec.reshape(1, -1))
		label = self.intents[np.argmax(predict[0])]
		proba = np.amax(predict[0])
		return label, proba