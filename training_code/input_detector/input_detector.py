import numpy as np 
import tensorflow as tf 
import fasttext as ft 
from os import listdir 

labels = ['bot-information', 'music-domain', 'unknown']

def load_data(max_step):
	### load word2vec model
	word2vec = ft.load_model('../../model/word2vec/vi.bin')
	### load all data file names
	file_names = listdir('../../data/input_detector')
	### define output
	training_set = []
	training_labels = []
	training_seqlen = []
	### process
	for file_name in file_names:
		f = open('../../data/input_detector/' + file_name)
		next(f)
		for row in f:
			tokenizers = row.split('\t')[1][:-1].split(' ')
			sentence_embedding = []
			for token in tokenizers:
				sentence_embedding.append(word2vec[token])
			while (len(sentence_embedding) < max_step):
				sentence_embedding.append(np.zeros(100))
			training_set.append(sentence_embedding)
			sentence_label = np.zeros(3)
			sentence_label[labels.index(file_name[:-4])] = 1
			training_labels.append(sentence_label)
			training_seqlen.append(len(tokenizers))
	### make training set randomly
	zip_ = list(zip(training_set, training_labels, training_seqlen))
	np.random.shuffle(zip_)
	training_set, training_labels, training_seqlen = zip(*zip_)
	return training_set, training_labels, training_seqlen

def main():
	max_step = 100
	n_hidden = 100
	batch_size = 32
	epochs = 20
	### load data
	training_set, training_labels, training_seqlen = load_data(max_step)
	### build graph
	x = tf.placeholder(tf.float32, [None, max_step, 100])
	y = tf.placeholder(tf.float32, [None, 3])
	sequence_length = tf.placeholder(tf.int32, [None])
	w = tf.Variable(tf.truncated_normal([n_hidden, 3]), name = 'w')
	b = tf.Variable(tf.truncated_normal([1, 3]), name = 'b')
	### LSTM layer
	lstm_cell = tf.contrib.rnn.LSTMCell(num_units = n_hidden)
	output, _ = tf.nn.dynamic_rnn(cell = lstm_cell, inputs = x, dtype = tf.float32)
	current_batch_size = tf.shape(output)[0]
	index = tf.range(0, current_batch_size)*max_step + (sequence_length - 1)
	output_last = tf.gather(tf.reshape(output, [-1, n_hidden]), index)
	pred = tf.nn.softmax(tf.matmul(output_last, w) + b)

	loss = tf.reduce_mean(-tf.reduce_sum(y * tf.log(pred), axis = 1), axis = 0)
	optimizer = tf.train.AdamOptimizer(0.01).minimize(loss)

	sess = tf.InteractiveSession()
	tf.global_variables_initializer().run()
	saver = tf.train.Saver()
	for epoch in range(epochs):
		start = 0
		sum_loss = 0
		while (start < len(training_seqlen)):
			batch_data = training_set[start:start+batch_size]
			batch_labels = training_labels[start:start+batch_size]
			batch_seqlen = training_seqlen[start:start+batch_size]
			start += batch_size
			batch_loss, _ = sess.run((loss, optimizer), feed_dict = {x: batch_data, y: batch_labels, sequence_length: batch_seqlen})
			sum_loss += batch_loss
		cnt = 0
		sum_cnt = 0
		prediction = sess.run(pred, feed_dict = {x: training_set, y: training_labels, sequence_length: training_seqlen})
		for i in range(len(training_seqlen)):
			sum_cnt += 1
			if (np.argmax(prediction[i]) == np.argmax(training_labels[i])):
				cnt += 1
		print('epoch: ', epoch, ' loss: ', sum_loss, ' accuracy: ', cnt/sum_cnt)
	saver.save(sess, '../../model/input_detector/model.ckpt')

if __name__ == '__main__':
	main()