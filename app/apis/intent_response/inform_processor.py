import random

class InformProcessor(object):
	"""
		there are 3 basic requests this process will handle
		-	request by properties
		-	request a song which properties have been mentioned in dialog
		-	request a 'whatever' song
	"""
	def __init__(self, whatever_dictionary, non_specifics):
		self.whatever_dictionary = whatever_dictionary
		self.non_specifics = non_specifics


	def mongo_form(self, songs, names, types, properties):
		information = {'$and': []}
		# append title information
		if not (songs == None):
			dict_title = {'$or': []}
			for song in songs:
				dict_title['$or'].append({'title': song})
			information['$and'].append(dict_title)
		# append names information
		if not (names == None):
			dict_name = {'$or': []}
			for name in names:
				dict_name['$or'].append({'singers': name})
				dict_name['$or'].append({'composers': name})
			information['$and'].append(dict_name)
		# append types information
		if not (types == None):
			dict_type = {'$or': []}
			for type_ in types:
				dict_type['$or'].append({'types': type_})
			information['$and'].append(dict_type)
		# append properties information
		if not (properties == None):
			dict_property = {'$or': []}
			for property_ in properties:
				dict_property['$or'].append({'properties': property_})
			information['$and'].append(dict_property)
		if (len(information['$and']) == 0):
			return None
		return information


	def generate_type_1(self, songs, names, types, properties, song_collection, dialog_history):
		# declare information dictionary
		information = self.mongo_form(songs, names, types, properties)
		# generate response
		response = {'text' : '', 'link' : ''}
		if (information == None):
			response['text'] += 'bạn muốn mở bài hát gì?'
		else:
			response_information = None
			field = {'name' : 0, 'time' : 0, 'views' : 0}
			documents = song_collection.find(information, field)
			if (len(list(documents)) != 0):
				documents = song_collection.find(information, field).limit(1).skip(random.randint(0, song_collection.find(information, field).count() - 1))
				for document in documents:
					response_information = document
				if (response_information != None):
					response['text'] += 'bài hát ' + response_information['title'] + ' đã được phát'
					response['link'] += response_information['link']
					dialog_history = {'songs' : [response_information['title']], 'names' : response_information['singers'] + response_information['composers'], 'types' : response_information['types'], 'properties' : response_information['properties']}
			else:
				response['text'] = 'mình không biết bài nào như thế cả :('

		return response, dialog_history


	def generate_type_2(self, songs, names, types, properties, song_collection, dialog_history):
		# declare information dictionary
		if (songs == None):
			songs = dialog_history['songs']
		if (names == None):
			names = dialog_history['names']
		if (types == None):
			types = dialog_history['types']
		if (properties == None):
			properties = dialog_history['properties']
		information = self.mongo_form(songs, names, types, properties)
		# generate response
		response = {'text' : '', 'link' : ''}
		if (information == None):
			response['text'] += 'bạn muốn mở bài gì cơ?'
		else:
			response_information = None
			field = {'name' : 0, 'time' : 0, 'views' : 0}
			documents = song_collection.find(information, field)
			if (len(list(documents)) != 0):
				documents = song_collection.find(information, field).limit(1).skip(random.randint(0, song_collection.find(information, field).count() - 1))
				for document in documents:
					response_information = document
				if (response_information != None):
					response['text'] += 'bài hát ' + response_information['title'] + ' đã được phát'
					response['link'] += response_information['link']
					dialog_history = {'songs' : [response_information['title']], 'names' : response_information['singers'] + response_information['composers'], 'types' : response_information['types'], 'properties' : response_information['properties']}
			else:
				response['text'] = 'mình không biết bài nào như thế cả :('
				
		return response, dialog_history


	def generate_type_3(self, songs, names, types, properties, song_collection, dialog_history):
		response = {'text' : '', 'link' : ''}
		response_information = None
		for document in song_collection.find().limit(1).skip(random.randint(0, song_collection.find().count() - 1)):
			response_information = document
		if (response_information != None):
			response['text'] += 'bài hát ' + response_information['title'] + ' đã được phát'
			response['link'] += response_information['link']
			dialog_history = {'songs' : [response_information['title']], 'names' : response_information['singers'], 'types' : response_information['types'], 'properties' : response_information['properties']}
		return response, dialog_history


	def get_response(self, text, songs, names, types, properties, song_collection, dialog_history):
		""" 
			check what type of request
			-	type 2 depend on appearence of noun phrase: bài đó, bài đấy, bài vừa rồi,
			bài hát trên, ...
			-	type 3 depend on ...
			-	type 1: others
		"""

		response = {'text' : '', 'link' : ''}

		type_ = 1
		for i in range(len(self.non_specifics)):
			if (text.lower().find(self.non_specifics[i]) != -1):
				type_ = 2
				
		for sen in self.whatever_dictionary:
			if (text.lower().find(sen) != -1):
				type_ = 3
		if (type_ == 1):
			response, dialog_history = self.generate_type_1(songs, names, types, properties, song_collection, dialog_history)
		if (type_ == 2):
			response, dialog_history = self.generate_type_2(songs, names, types, properties, song_collection, dialog_history)
		if (type_ == 3):
			response, dialog_history = self.generate_type_3(songs, names, types, properties, song_collection, dialog_history)
		if (response['text'] == ''):
			response['text'] == 'mình không biết bài hát nào như thế cả :(('

		return response, dialog_history


