import os
import numpy as np 
import tensorflow as tf 
import gensim
from pymongo import MongoClient
from app.apis.seq2seq import Seq2Seq
from app.apis.entity_detector.song_detector_LM import SongDetectorLM
from app.apis.entity_detector.singer_composer_detector import SingerComposerDetector
from app.apis.entity_detector.type_detector import TypeDetector 
from app.apis.entity_detector.property_detector import PropertyDetector 
from app.apis.music_checker import MusicChecker
from app.apis.intent_detector import IntentDetector
from app.apis.dialog_manager import DialogManager


######========================================================================================######
######=============================== main code ==============================================######
######========================================================================================######

#================================= connect database ==========================================
client = MongoClient()
db = client['project-nlp']
song_collection = db.songCollection
artist_collection = db.artistCollection

#================================ load pretrain model ========================================
tf.reset_default_graph()
Doc2vec = gensim.models.doc2vec.Doc2Vec.load('./model/doc2vec/best.doc2vec.model')
sess = tf.InteractiveSession()
seq2seq = Seq2Seq(sess)

#================================ declare all object =========================================
music_checker = MusicChecker()
song_detector = SongDetectorLM(song_collection)
singer_composer_detector = SingerComposerDetector(song_collection)
type_detector = TypeDetector()
property_detector = PropertyDetector()
intent_detector = IntentDetector(Doc2vec)
dialog_manager = DialogManager()

#==================================== process ================================================

req = ''
dialog_history = {'songs' : None, 'names' : None, 'types' : None, 'properties' : None}

def normalize(text):
	text_ = ''
	for i in range(len(text)):
		if (text[i] in ['?', ',', '.', '!']):
			text_ += ' '
		text_ += text[i]
	return text_

def get_response(req):
	# get input sentence of user
	response = {'text' : '', 'link' : ''}
	global dialog_history
	# check sentence belong to music domain
	isMusic = music_checker.check(req)
	# response
	if (isMusic):
		### process music domain ###
		# replace all specific NP by general words
		text = normalize(req)
		text, song = song_detector.detect(text)
		text, names = singer_composer_detector.detect(text)
		text, types = type_detector.detect(text)
		text, properties = property_detector.detect(text)
		# detect intent of request sentence
		intent, proba = intent_detector.predict(text)
		print(text)
		print(song)
		print(names)
		print(types)
		print(properties)
		print(intent)
		# dialog manager
		response, dialog_history = dialog_manager.get_response(intent, text, song, names, types, properties, song_collection, artist_collection, dialog_history)
		if ((response['text'] == '') and (intent != 'other')):
			response['text'] = 'mình không biết về vấn đề này :('
	print(dialog_history)
	# get response from seq to seq model
	if (response['text'] == ''):
		response['text'] = seq2seq.predict(req)
	#response
	return response

req = ''

while (req != 'stop'):
	req = input('user: ')
	res = get_response(req)
	print('bot: ', res)
