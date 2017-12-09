import numpy as np 
import tensorflow as tf 
import math
from tensorflow.python.layers.core import Dense 

class Seq2Seq(object):
	def __init__(self, sess):
		### input parameters
		self.sess = sess
		### fixed parameters
		self.max_step = 20
		self.n_hidden = 100
		self.embedding_size = 100
		### load model when initialized
		self.build_model()
		self.saver = tf.train.Saver()
		self.saver.restore(self.sess, './model/end-to-end_language_generator/model.ckpt')

	def build_model(self):
		### load dictionary
		self.load_dictionary()
		### merge all model
		self.init_placeholder()
		self.build_encoder()
		self.build_decoder()

	def load_dictionary(self):
		### load dictionary
		f = open('./data/NLG/dictionary', 'r')
		self.dictionary = []
		for row in f:
			self.dictionary.append(row[:-1])

	def transform(self, text):
		### transform text to input vector
		text_split = text.split(' ')
		enc_input = []
		for word in text_split:
			if not (word in self.dictionary):
				enc_input.append(self.dictionary.index('<UNK>'))
			else:
				enc_input.append(self.dictionary.index(word))
		while (len(enc_input) < self.max_step):
			enc_input.append(self.dictionary.index('<PAD>'))
		enc_input_length = [len(text_split)]
		return enc_input, enc_input_length

	def init_placeholder(self):
		### init placeholder
		self.start_token = self.dictionary.index('<GO>')
		self.end_token = self.dictionary.index('<EOS>')
		# encoder inputs: [batch size, max step]
		self.encoder_inputs = tf.placeholder(tf.int32, [None, self.max_step], name = 'encoder_inputs')
		# encoder inputs length: [batch_size]
		self.encoder_inputs_length = tf.placeholder(tf.int32, [None], name = 'encoder_inputs_length')
		# decoder inputs: [batch size, max step]
		self.decoder_inputs = tf.placeholder(tf.int32, [None, self.max_step], name = 'decoder_inputs')
		# decoder inputs length: [batch size]
		self.decoder_inputs_length = tf.placeholder(tf.int32, [None])
		# get training batch size
		self.train_batch_size = tf.shape(self.encoder_inputs)[0]

	def build_encoder(self):
		### build encoder
		with tf.variable_scope('encoder'):
			# initialize encoder cell
			self.encoder_cell = tf.contrib.rnn.LSTMCell(num_units = self.n_hidden)
			# initialize encoder embedding have variance = 1
			sqrt3 = math.sqrt(3)
			initializer = tf.random_uniform_initializer(-sqrt3, sqrt3, dtype = tf.float32)
			self.encoder_embedding = tf.get_variable(name = 'embedding', shape = [len(self.dictionary), self.embedding_size], initializer = initializer, dtype = tf.float32)
			# encoder inputs embedding: [batch size, max_step, embedding size]
			self.encoder_inputs_embedded = tf.nn.embedding_lookup(params = self.encoder_embedding, ids = self.encoder_inputs)
			# input layer
			input_layer = Dense(self.n_hidden, dtype = tf.float32, name = 'input_projection')
			self.encoder_inputs_embedded = input_layer(self.encoder_inputs_embedded)
			# feed all to rnn
			self.encoder_output, self.encoder_last_state = tf.nn.dynamic_rnn(cell = self.encoder_cell, inputs = self.encoder_inputs_embedded, sequence_length = self.encoder_inputs_length, dtype = tf.float32)

	def build_decoder(self):
		### build decoder
		with tf.variable_scope('decoder'):
			# initialize decoder cell
			self.decoder_cell = tf.contrib.rnn.LSTMCell(num_units = self.n_hidden)
			# initialize decoder embedding have variance = 1
			sqrt3 = math.sqrt(3)
			initializer = tf.random_uniform_initializer(-sqrt3, sqrt3, dtype = tf.float32)
			self.decoder_embedding = tf.get_variable(name = 'embedding', shape = [len(self.dictionary), self.embedding_size], initializer = initializer, dtype = tf.float32)
			# input layer
			input_layer = Dense(self.n_hidden, dtype = tf.float32, name = 'input_projection')
			# output layer
			output_layer = Dense(len(self.dictionary), dtype = tf.float32, name = 'output_projection')
			
			## for inference
			def embed_and_input_proj(inputs):
				return input_layer(tf.nn.embedding_lookup(self.decoder_embedding, inputs))
			vector_start_tokens = tf.ones([self.train_batch_size, ], dtype = tf.int32)*self.start_token
			self.inference_helper = tf.contrib.seq2seq.GreedyEmbeddingHelper(start_tokens = vector_start_tokens, end_token = self.end_token, embedding = embed_and_input_proj)
			self.inference_decoder = tf.contrib.seq2seq.BasicDecoder(cell = self.decoder_cell, helper = self.inference_helper, initial_state = self.encoder_last_state, output_layer = output_layer)
			# decoder_output_inference = (rnn_output + sample id)
			# rnn_output: [batch size, max step + 1, len(dictionary)]
			self.decoder_output_inference, self.decoder_last_state_inference, self.decoder_outputs_length_inference = tf.contrib.seq2seq.dynamic_decode(decoder = self.inference_decoder)
			self.prediction = self.decoder_output_inference.rnn_output

	def whitespace(self, text):
		punctuation = ['.', ',', '!', '?']
		sentence = ''
		for i in range(len(text)):
			if (text[i] in punctuation) and (i > 0) and (text[i-1] != ' '):
				sentence += ' '
			sentence += text[i]
		return sentence

	def predict(self, text):
		### using whitespace to separate all text
		sentence = self.whitespace(text.lower())
		### transform...
		enc_input, enc_input_length = self.transform(sentence)
		### predict...
		pred = self.sess.run(self.prediction, feed_dict = {self.encoder_inputs: np.array([enc_input]), self.encoder_inputs_length: enc_input_length})
		response = ''
		for i in range(len(pred[0])):
			if (self.dictionary[np.argmax(pred[0][i])] in ['<GO>', '<PAD>', '<UNK>', '<EOS>']):
				break
			response += ' ' + self.dictionary[np.argmax(pred[0][i])]
		return response


