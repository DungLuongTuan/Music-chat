# -*- coding: utf-8 -*-
class MusicChecker(object):
	"""
		check whether a sentence has 'music''s words
	"""
	def __init__(self):
		self.load_music_words()


	def load_music_words(self):
		### declare list of music words
		self.music_words = []
		### append title's word
		f = open('./data/dictionary/entity_dictionary/title_dictionary', 'r')
		for row in f:
			self.music_words.append(row[:-1])
		f.close()
		### append singer's word
		f = open('./data/dictionary/entity_dictionary/singer_dictionary', 'r')
		for row in f:
			self.music_words.append(row[:-1])
		f.close()
		### append composer's word
		f = open('./data/dictionary/entity_dictionary/composer_dictionary', 'r')
		for row in f:
			self.music_words.append(row[:-1])
		f.close()
		### append type's word
		f = open('./data/dictionary/entity_dictionary/type_dictionary', 'r')
		for row in f:
			row_split = row[:-1].split('\t')
			self.music_words.append(row_split[0])
		f.close()
		### append whatever's sen
		f = open('./data/dictionary/whatever_dictionary', 'r')
		for row in f:
			self.music_words.append(row[:-1])
		f.close()

	def check(self, text):
		ok = False
		for word in self.music_words:
			if (text.lower().find(word) != -1):
				ok = True
		return ok