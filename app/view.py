import os
import numpy as np 
import tensorflow as tf 
import gensim
from flask import render_template, request
from app import app
from pymongo import MongoClient
from .apis.seq2seq import Seq2Seq
from .apis.entity_detector.song_detector_LM import SongDetectorLM
from .apis.entity_detector.singer_composer_detector import SingerComposerDetector
from .apis.entity_detector.type_detector import TypeDetector 
from .apis.entity_detector.property_detector import PropertyDetector 
from .apis.music_checker import MusicChecker
from .apis.intent_detector import IntentDetector
from .apis.dialog_manager import DialogManager


######========================================================================================######
######=============================== main code ==============================================######
######========================================================================================######

#================================= connect database ==========================================
client = MongoClient()
db = client['project-nlp']
song_collection = db.songCollection
artist_collection = db.artistCollection

#================================ load pretrain model ========================================
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
		text = req
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

#================================== SERVER ==================================================
@app.route('/')
def index():
	return render_template('index.html')

@app.route('/', methods = ['POST'])
def get_request():
	global dialog_history
	text = dict(request.form)['req'][0]
	res = get_response(text)
	res['link'] = res['link'].replace('https://www.youtube.com/watch?v=', '')
	
	return str(res).replace("'", '"', 1000)