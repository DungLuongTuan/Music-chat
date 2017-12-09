import math
import numpy as np 
import tensorflow as tf 
from tensorflow.python.layers.core import Dense 

def whitespace(text):
	punctuation = ['.', ',', '!', '?']
	sentence = ''
	for i in range(len(text)):
		if (text[i] in punctuation) and (i > 0) and (text[i-1] != ' '):
			sentence += ' '
		sentence += text[i]
	return sentence

def make_dictionary():
	### make dictionary form dialog source
	f = open('../../data/NLG/dialog.csv', 'r')
	dictionary = ['<PAD>', '<GO>', '<EOS>', '<UNK>']
	next(f)
	for row in f:
		split_row = row[:-1].split('\t')
		split_req = whitespace(split_row[1]).split(' ')
		split_res = whitespace(split_row[2]).split(' ')
		dictionary += split_req
		dictionary += split_res
	dictionary = set(dictionary)
	### save dictionary in to file
	fo = open('../../data/NLG/dictionary', 'w')
	for word in dictionary:
		fo.write(word + '\n')
	f.close()
	fo.close()
	return list(dictionary)

def load_data(max_step):
	### load dictionary
	f = open('../../data/NLG/dictionary', 'r')
	dictionary = []
	for row in f:
		dictionary.append(row[:-1])
	f.close()
	### make data
	f = open('../../data/NLG/dialog.csv', 'r')
	next(f)
	enc_inputs = []
	enc_inputs_length = []
	dec_inputs = []
	dec_inputs_length = []
	for row in f:
		# split row in to no, input sentences, output sentences
		split_row = row[:-1].split('\t')
		# make encoder input
		enc_input = []
		enc_input_split = whitespace(split_row[1]).split(' ')
		for word in enc_input_split:
			enc_input.append(dictionary.index(word))
		while (len(enc_input) < max_step):
			enc_input.append(dictionary.index('<PAD>'))
		# add encoder input to encoder inputs
		enc_inputs.append(enc_input)
		# add encoder input length to encoder inputs length
		enc_inputs_length.append(len(enc_input_split))
		# make decoder input
		dec_input = []
		dec_input_split = whitespace(split_row[2]).split(' ')
		for word in dec_input_split:
			dec_input.append(dictionary.index(word))
		while (len(dec_input) < max_step):
			dec_input.append(dictionary.index('<PAD>'))
		# add decoder input to decoder inputs
		dec_inputs.append(dec_input)
		# add decoder input length to decoder inputs length
		dec_inputs_length.append(len(dec_input_split))
	f.close()
	return enc_inputs, enc_inputs_length, dec_inputs, dec_inputs_length

def main():
	### make dictionary
	dictionary = make_dictionary()
	tf.reset_default_graph()
	### parameters
	epochs = 50
	batch_size = 4
	max_step = 20
	n_hidden = 100
	embedding_size = 100
	start_token = dictionary.index('<GO>')
	end_token = dictionary.index('<EOS>')

	### load data
	enc_inputs, enc_inputs_length, dec_inputs, dec_inputs_length = load_data(max_step)

	### init placeholder
	# encoder inputs: [batch size, max step]
	encoder_inputs = tf.placeholder(tf.int32, [None, max_step], name = 'encoder_inputs')
	# encoder inputs length: [batch_size]
	encoder_inputs_length = tf.placeholder(tf.int32, [None], name = 'encoder_inputs_length')
	# decoder inputs: [batch size, max step]
	decoder_inputs = tf.placeholder(tf.int32, [None, max_step], name = 'decoder_inputs')
	# decoder inputs length: [batch size]
	decoder_inputs_length = tf.placeholder(tf.int32, [None])
	# get training batch size
	train_batch_size = tf.shape(encoder_inputs)[0]
	# decoder start tokens: [batch size]
	decoder_start_tokens = tf.ones([train_batch_size, 1], dtype = tf.int32)*start_token
	# decoder end tokens: [batch size]
	decoder_end_token = tf.ones([train_batch_size, 1], dtype = tf.int32)*end_token
	# decoder inputs train: add GO to the begining => [batch size, max train step + 1] 
	max_train_step = tf.reduce_max(decoder_inputs_length)
	decoder_inputs_cut = tf.transpose(tf.transpose(decoder_inputs, [1, 0])[:max_train_step], [1, 0])
	decoder_inputs_train = tf.concat([decoder_start_tokens, decoder_inputs_cut], axis = 1)
	# decoder inputs length train:
	decoder_inputs_length_train = decoder_inputs_length + 1
	# decoder target train: add EOS to the end => [batch size, max step + 1]
	decoder_target_train = tf.concat([decoder_inputs_cut, decoder_end_token], axis = 1)

	### build encoder
	with tf.variable_scope('encoder'):
		# initialize encoder cell
		encoder_cell = tf.contrib.rnn.LSTMCell(num_units = n_hidden)
		# initialize encoder embedding have variance = 1
		sqrt3 = math.sqrt(3)
		initializer = tf.random_uniform_initializer(-sqrt3, sqrt3, dtype = tf.float32)
		encoder_embedding = tf.get_variable(name = 'embedding', shape = [len(dictionary), embedding_size], initializer = initializer, dtype = tf.float32)
		# encoder inputs embedding: [batch size, max_step, embedding size]
		encoder_inputs_embedded = tf.nn.embedding_lookup(params = encoder_embedding, ids = encoder_inputs)
		# input layer
		input_layer = Dense(n_hidden, dtype = tf.float32, name = 'input_projection')
		encoder_inputs_embedded = input_layer(encoder_inputs_embedded)
		# feed all to rnn
		encoder_output, encoder_last_state = tf.nn.dynamic_rnn(cell = encoder_cell, inputs = encoder_inputs_embedded, sequence_length = encoder_inputs_length, dtype = tf.float32)

	### build decoder
	with tf.variable_scope('decoder'):
		# initialize decoder cell
		decoder_cell = tf.contrib.rnn.LSTMCell(num_units = n_hidden)
		# initialize decoder embedding have variance = 1
		sqrt3 = math.sqrt(3)
		initializer = tf.random_uniform_initializer(-sqrt3, sqrt3, dtype = tf.float32)
		decoder_embedding = tf.get_variable(name = 'embedding', shape = [len(dictionary), embedding_size], initializer = initializer, dtype = tf.float32)
		# input layer
		input_layer = Dense(n_hidden, dtype = tf.float32, name = 'input_projection')
		# output layer
		output_layer = Dense(len(dictionary), dtype = tf.float32, name = 'output_projection')
		
		## for training
		# decoder inputs embedding: [batch size, max step + 1, embedding size]
		decoder_inputs_embedded = tf.nn.embedding_lookup(params = decoder_embedding, ids = decoder_inputs_train)
		decoder_inputs_embedded = input_layer(decoder_inputs_embedded)
		# helper to feed input for training
		training_helper = tf.contrib.seq2seq.TrainingHelper(inputs = decoder_inputs_embedded, sequence_length = decoder_inputs_length_train, name = 'training_helper')
		training_decoder = tf.contrib.seq2seq.BasicDecoder(cell = decoder_cell, helper = training_helper, initial_state = encoder_last_state, output_layer = output_layer)
		# max decoder input in current batch
		max_decoder_length = tf.reduce_max(decoder_inputs_length_train)
		# decoder_output_train = (rnn_output, sample id)
		# rnn_output: [batch size, max step + 1, len(dictionary)]
		decoder_output_train, decoder_last_state_train, decoder_outputs_length_train = tf.contrib.seq2seq.dynamic_decode(decoder = training_decoder, impute_finished = True, maximum_iterations = max_decoder_length)
		
		## for inference
		def embed_and_input_proj(inputs):
			return input_layer(tf.nn.embedding_lookup(decoder_embedding, inputs))
		vector_start_tokens = tf.ones([train_batch_size, ], dtype = tf.int32)*start_token
		inference_helper = tf.contrib.seq2seq.GreedyEmbeddingHelper(start_tokens = vector_start_tokens, end_token = end_token, embedding = embed_and_input_proj)
		inference_decoder = tf.contrib.seq2seq.BasicDecoder(cell = decoder_cell, helper = inference_helper, initial_state = encoder_last_state, output_layer = output_layer)
		# decoder_output_inference = (rnn_output + sample id)
		# rnn_output: [batch size, max step + 1, len(dictionary)]
		decoder_output_inference, decoder_last_state_inference, decoder_outputs_length_inference = tf.contrib.seq2seq.dynamic_decode(decoder = inference_decoder)
		predict = decoder_output_inference.rnn_output

	### loss + optimization
	# decoder logits train
	decoder_logits_train = tf.identity(decoder_output_train.rnn_output)
	# masking
	mask = tf.sequence_mask(lengths = decoder_inputs_length_train, maxlen = max_decoder_length, dtype = tf.float32)
	# loss function
	loss = tf.contrib.seq2seq.sequence_loss(logits = decoder_logits_train, targets = decoder_target_train, weights = mask)
	# optimization algorithm
	optimizer = tf.train.AdamOptimizer(0.001).minimize(loss)

	# training...
	sess = tf.InteractiveSession()
	tf.global_variables_initializer().run()
	saver = tf.train.Saver()
	cnt_input = len(enc_inputs_length)
	for epoch in range(epochs):
		start = 0
		sum_loss = 0
		while (start < cnt_input):
			batch_enc_inputs = enc_inputs[start:min(start+batch_size, cnt_input)]
			batch_enc_inputs_length = enc_inputs_length[start:min(start+batch_size, cnt_input)]
			batch_dec_inputs = dec_inputs[start:min(start+batch_size, cnt_input)]
			batch_dec_inputs_length = dec_inputs_length[start:min(start+batch_size, cnt_input)]
			start += batch_size
			loss_, _ = sess.run((loss, optimizer), feed_dict = {encoder_inputs: batch_enc_inputs, encoder_inputs_length: batch_enc_inputs_length, decoder_inputs: batch_dec_inputs, decoder_inputs_length: batch_dec_inputs_length})
			sum_loss += loss_
		print('epoch: ', epoch, ' loss: ', sum_loss)
	saver.save(sess, '../../model/end-to-end_language_generator/model.ckpt')


	# ### evaluate
	# for i in range(len(enc_inputs_length)):
	# 	pred = sess.run(predict, feed_dict = {encoder_inputs: np.array([enc_inputs[i]]), encoder_inputs_length: np.array([enc_inputs_length[i]])})
	# 	# input sentence
	# 	input_sentence = ''
	# 	for j in range(enc_inputs_length[i]):
	# 		input_sentence += ' ' + dictionary[enc_inputs[i][j]]
	# 	# predict output sentence
	# 	output_sentence = ''
	# 	for j in range(len(pred[0])):
	# 		output_sentence += ' ' + dictionary[np.argmax(pred[0][j])]
	# 	# print pair of sentence
	# 	print(input_sentence, ' => ', output_sentence)

if __name__ == '__main__':
	main()