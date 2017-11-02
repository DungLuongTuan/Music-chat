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

req = ''
last_inform = []

def get_response(req):
	# get input sentence of user
	response = {'text' : '', 'link' : ''}
	global last_inform
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
		response, last_inform = dialog_manager.get_response(intent, text, song, names, types, properties, collection, last_inform)
		if ((response['text'] == '') and (intent != 'other')):
			response['text'] = 'mình không biết về vấn đề này :('
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
	global last_inform
	text = dict(request.form)['req'][0]
	res = get_response(text)
	res['link'] = res['link'].replace('https://www.youtube.com/watch?v=', '')
	
	return str(res).replace("'", '"', 1000)