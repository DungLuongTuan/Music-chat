from sklearn import svm
import numpy as np 
import gensim
from os import listdir
import pickle
import random

def load_data():
	doc2vec = gensim.models.doc2vec.Doc2Vec.load('../../model/doc2vec/best.doc2vec.model')
	file_names = listdir('../../data/intent_detector')
	data = []
	labels = []
	for file_name in file_names:
		f = open('../../data/intent_detector/' + file_name)
		next(f)
		for row in f:
			split_row = row.split('\t')
			data.append(doc2vec.infer_vector(split_row[1][:-1]))
			labels.append(file_name[:-4])
		f.close()
	z = list(zip(data, labels))
	random.shuffle(z)
	data, labels = zip(*z)
	return data, labels

def train_new_model(training_data, training_labels):
	### train model
	classify = svm.SVC(C = 1.0, kernel = 'linear', probability = True)
	classify.fit(training_data, training_labels)
	### save model
	f = open('../../model/intent_detector/intent_model.pkl', 'wb')
	pickle.dump(classify, f)
	f.close()

def main():
	### load data
	training_data, training_labels = load_data()
	### process
	train_new_model(training_data, training_labels)

if __name__ == '__main__':
	main()
