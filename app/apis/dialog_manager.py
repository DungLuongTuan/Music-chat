from .intent_response.inform_processor import InformProcessor
from .intent_response.search_processor import SearchProcessor
from .intent_response.show_processor import ShowProcessor
from .intent_response.change_processor import ChangeProcessor


class DialogManager(object):
	def __init__(self):
		self.load_dictionary()
		self.inform_processor = InformProcessor(self.whatever_dictionary, self.non_specific_dictionary)
		self.search_processor = SearchProcessor(self.non_specific_dictionary, self.composer_words, self.singer_words, self.title_words, self.type_words, self.property_words)
		self.show_processor = ShowProcessor(self.non_specific_dictionary, self.composer_words, self.singer_words, self.title_words, self.type_words, self.property_words, self.number_dictionary, self.negative_dictionary, self.lyric_words, self.all_words)
		self.change_processor = ChangeProcessor()


	def load_dictionary(self):
		# load composer dictionary
		f = open('./data/dictionary/entity_dictionary/composer_dictionary', 'r')
		self.composer_words = []
		for row in f:
			self.composer_words.append(row[:-1])
		f.close()
		# load singer dictionary
		f = open('./data/dictionary/entity_dictionary/singer_dictionary', 'r')
		self.singer_words = []
		for row in f:
			self.singer_words.append(row[:-1])
		f.close()
		# load title dictionary
		f = open('./data/dictionary/entity_dictionary/title_dictionary', 'r')
		self.title_words = []
		for row in f:
			self.title_words.append(row[:-1])
		f.close()
		# load lyric dictionary
		f = open('./data/dictionary/entity_dictionary/lyric_dictionary', 'r')
		self.lyric_words = []
		for row in f:
			self.lyric_words.append(row[:-1])
		f.close()
		# load type dictionary
		f = open('./data/dictionary/entity_dictionary/type_dictionary', 'r')
		self.type_words = []
		self.type_labels = []
		for row in f:
			row_split = row[:-1].split('\t')
			self.type_words.append(row_split[0])
			self.type_labels.append(row_split[1])
		f.close()
		# load property dictionary
		f = open('./data/dictionary/entity_dictionary/property_dictionary', 'r')
		self.property_words = []
		self.property_labels = []
		for row in f:
			row_split = row[:-1].split('\t')
			self.property_words.append(row_split[0])
			self.property_labels.append(row_split[1])
		f.close()
		# load all dictionary
		f = open('./data/dictionary/entity_dictionary/all_dictionary', 'r')
		self.all_words = []
		for row in f:
			self.all_words.append(row[:-1])
		f.close()
		# load negative dictionary
		f = open('./data/dictionary/negative_dictionary', 'r')
		self.negative_dictionary = []
		for row in f:
			self.negative_dictionary.append(row[:-1])
		f.close()
		# load number dictionary
		f = open('./data/dictionary/number_dictionary', 'r')
		self.number_dictionary = []
		for row in f:
			self.number_dictionary.append(row[:-1])
		f.close()
		# load whatever dictionary
		f = open('./data/dictionary/whatever_dictionary', 'r')
		self.whatever_dictionary = []
		for row in f:
			self.whatever_dictionary.append(row[:-1])
		f.close()
		# load non specific dictionary
		f = open('./data/dictionary/non_specific_dictionary', 'r')
		self.non_specific_dictionary = []
		for row in f:
			self.non_specific_dictionary.append(row[:-1])
		f.close()


	def get_response(self, intent, text, songs, names, types, properties, song_collection, artist_collection, dialog_history):
		res = {'text' : '', 'link' : ''}
		if (intent == 'inform'):
			res, dialog_history = self.inform_processor.get_response(text, songs, names, types, properties, song_collection, dialog_history)

		if (intent == 'search'):
			res, dialog_history = self.search_processor.get_response(text, songs, names, types, properties, song_collection, dialog_history)

		if (intent == 'show'):
			res, dialog_history = self.show_processor.get_response(text, songs, names, types, properties, song_collection, artist_collection, dialog_history)
		
		if (intent == 'change'):
			res, dialog_history = self.change_processor.get_response(text, songs, names, types, properties, song_collection, dialog_history)
		
		return res, dialog_history