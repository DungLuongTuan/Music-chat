import os
import numpy as np 
import tensorflow as tf 
import gensim
from pymongo import MongoClient
from apis.seq2seq import Seq2Seq
from apis.entity_detector.song_detector_LM import SongDetectorLM
from apis.entity_detector.singer_composer_detector import SingerComposerDetector
from apis.entity_detector.type_detector import TypeDetector 
from apis.entity_detector.property_detector import PropertyDetector 
from apis.music_checker import MusicChecker
from apis.intent_detector import IntentDetector
from apis.dialog_manager import DialogManager


######========================================================================================######
######=============================== main code ==============================================######
######========================================================================================######

#================================= connect database ==========================================
client = MongoClient()
db = client['projectNLP']
collection = db.songCollection

#================================ load pretrain model ========================================
Doc2vec = gensim.models.doc2vec.Doc2Vec.load('./model/doc2vec/best.doc2vec.model')
sess = tf.InteractiveSession()
seq2seq = Seq2Seq(sess)

#================================ declare all object =========================================
music_checker = MusicChecker()
song_detector = SongDetectorLM()
singer_composer_detector = SingerComposerDetector()
type_detector = TypeDetector()
property_detector = PropertyDetector()
intent_detector = IntentDetector(Doc2vec)
dialog_manager = DialogManager()

#==================================== process ================================================

reqqq = ''
last_inform = []
def get_response(req, last_inform):
	# get input sentence of user
	response = ''
	# check sentence belong to music domain
	isMusic = music_checker.check(req)
	# response
	if (isMusic):
		### process music domain ###
		# replace all specific NP by general words
		text = req
		text, song = song_detector.detect(text, collection)
		text, names = singer_composer_detector.detect(text, collection)
		text, types = type_detector.detect(text, collection)
		text, properties = property_detector.detect(text, collection)
		# detect intent of request sentence
		intent, proba = intent_detector.predict(text)
		# dialog manager
		print(intent)
		response, last_inform = dialog_manager.get_response(intent, text, song, names, types, properties, collection, last_inform)
		if ((response == '') and (intent != 'other')):
			response = 'mình không biết về vấn đề này :('
	# get response from seq to seq model
	if (response == ''):
		response = seq2seq.predict(req)
	response
	return response, last_inform


def whitespace(text):
	punctuation = ['.', ',', '!', '?']
	sentence = ''
	for i in range(len(text)):
		if (text[i] in punctuation):
			sentence += ' '
		sentence += text[i]
	return sentence


while reqqq != 'stop':
	reqqq = input('user: ')
	res, last_inform = get_response(reqqq, last_inform)
	print('bot: ', res)
	f = open('./data/NLG/dialog.csv', 'a')
	ok = input('mình trả lời thế được chưa? type "ok" hoặc enter:  ')
	if not ok:
		new_res = input('câu trả lời đúng là: ')
		f.write('\t' + whitespace(reqqq) + '\t' + new_res + '\n')
	f.close()