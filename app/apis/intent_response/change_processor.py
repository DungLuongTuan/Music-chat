import random

class ChangeProcessor(object):
	def __init__(self):
		pass

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

		
	def generate_type_1(self, text, songs, names, types, properties, song_collection, dialog_history):
		response = {'text' : '', 'link' : ''}
		if (dialog_history['names'] == None) and (dialog_history['songs'] == None) and (dialog_history['types'] == None) and (dialog_history['properties'] == None):
			response['text'] = 'bạn muốn mở bài gì?'
			return response, dialog_history
			
		if (names == None) and (songs == None) and (types == None) and (properties == None):
			response['text'] = 'bạn muốn mở bài gì?'
			return response, dialog_history

		### get input information
		types = None
		properties = None
		if (songs == None) and (dialog_history['songs'] != None):
			songs = [dialog_history['songs'][random.randint(0, len(dialog_history['songs']) - 1)]]
		if (names == None) and (dialog_history['names'] != None):
			names = [dialog_history['names'][random.randint(0, len(dialog_history['names']) - 1)]]
		information = self.mongo_form(songs, names, types, properties)
		
		if (information != None):
			response_information = None
			field = {'name' : 0, 'time' : 0, 'views' : 0}
			documents = song_collection.find(information, field)
			if (len(list(documents)) != 0):
				documents = song_collection.find(information, field).limit(1).skip(random.randint(0, song_collection.find(information, field).count() - 1))
				for document in documents:
					response_information = document
				if (response_information != None):
					response['text'] = 'bài hát ' + response_information['title'] + ' đã được phát'
					response['link'] = response_information['link']
					dialog_history = {'songs' : [response_information['title']], 'names' : response_information['singers'] + response_information['composers'], 'types' : response_information['types'], 'properties' : response_information['properties']}
			else:
				response['text'] = 'mình không biết bài nào như thế cả :('

		return response, dialog_history

	def get_response(self, text, songs, names, types, properties, song_collection, dialog_history):
		response = {'text' : '', 'link' : ''}
		response, dialog_history = self.generate_type_1(text, songs, names, types, properties, song_collection, dialog_history)

		if (response['text'] == ''):
			response['text'] = 'bạn muốn đổi bài gì?'

		return response, dialog_history