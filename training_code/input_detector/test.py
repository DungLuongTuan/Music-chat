import numpy as np 
import tensorflow as tf 
import fasttext as ft 
from os import listdir 

labels = ['bot-information', 'music-domain', 'unknown']

def transform(sentence, max_step):
	output = []
	word2vec = ft.load_model('../../model/word2vec/vi.bin')
	sentence_splited = sentence.split(' ')
	for word in sentence_splited:
		output.append(word2vec[word])
	while (len(output) < max_step):
		output.append(np.zeros(100))
	return [output], [len(sentence_splited)]

def main():
	### model
	max_step = 100
	n_hidden = 100
	### enter text
	text = 'tên gì ?'
	data, seqlen = transform(text, max_step)
	print(np.shape(data))
	### build graph
	x = tf.placeholder(tf.float32, [None, max_step, 100])
	sequence_length = tf.placeholder(tf.int32, [None])
	w = tf.get_variable(name = 'w', shape = [n_hidden, 3])
	b = tf.get_variable(name = 'b', shape = [1, 3])
	### LSTM layer
	lstm_cell = tf.contrib.rnn.LSTMCell(num_units = n_hidden)
	output, _ = tf.nn.dynamic_rnn(cell = lstm_cell, inputs = x, dtype = tf.float32)
	current_batch_size = tf.shape(output)[0]
	index = tf.range(0, current_batch_size)*max_step + (sequence_length - 1)
	output_last = tf.gather(tf.reshape(output, [-1, n_hidden]), index)
	pred = tf.nn.softmax(tf.matmul(output_last, w) + b)

	sess = tf.InteractiveSession()
	tf.global_variables_initializer().run()
	saver = tf.train.Saver()
	saver.restore(sess, '../../model/input_detector/model.ckpt')
	prediction = sess.run(pred, feed_dict = {x: data, sequence_length: seqlen})
	print(labels[np.argmax(prediction)])

if __name__ == '__main__':
	main()