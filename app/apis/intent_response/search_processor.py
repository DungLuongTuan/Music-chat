import random

class SearchProcessor(object):
	"""
		there are 2 basic requests this process will handle:
		-	search information by giving properties
		-	search information that has been given from some last request
	"""
	def __init__(self, non_specifics, composer_words, singer_words, title_words, type_words, property_words):
		self.non_specifics = non_specifics
		self.composer_words = composer_words
		self.singer_words = singer_words
		self.title_words = title_words
		self.type_words = type_words
		self.property_words = property_words


	def get_request_information(self, text, songs, names, types, properties, song_collection, dialog_history):
		### detect request object in input sentence
		# declare list of detected informations
		detected_information = []
		if not (songs == None):
			detected_information.append('title')
		if not (types == None):
			detected_information.append('types')
		if not (properties == None):
			detected_information.append('properties')
		# detect request informations
		request_information = []
		for word in self.composer_words:
			if (text.lower().find(word) != -1):
				request_information.append('composers')
				break
		for word in self.singer_words:
			if (text.lower().find(word) != -1):
				request_information.append('singers')
				break
		for word in self.title_words:
			if (text.lower().find(word) != -1):
				request_information.append('title')
				break
		for word in self.type_words:
			if (text.lower().find(word) != -1):
				request_information.append('types')
				break
		for word in self.property_words:
			if (text.lower().find(word) != -1):
				request_information.append('properties')
				break
		# detect request objects
		objects = []
		for info in request_information:
			if not (info in detected_information):
				objects.append(info)
		return objects


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


	def combine(self, inp):
		if (isinstance(inp, list)):
			res = str(inp[0])
			for i in range(1, len(inp)):
				res += ' + ' + str(inp[i])
			return res
		else:
			return str(inp)


	def generate_type_1(self, text, songs, names, types, properties, song_collection, dialog_history):
		### get request objects
		objects = self.get_request_information(text, songs, names, types, properties, song_collection, dialog_history)
		### get input information
		information = self.mongo_form(songs, names, types, properties)
		### renerate response
		response = {'text' : '', 'link' : ''}

		if (information == None) and (len(objects) != 0):
			if (objects[0] == 'title'):
				response['text'] += 'bạn muốn bài hát như thế nào?'
			if (objects[0] == 'singers'):
				response['text'] += 'bạn muốn tìm ca sĩ nào?'
			if (objects[0] == 'composers'):
				response['text'] += 'bạn muốn tìm nhạc sĩ nào?'
		print(information)
		print(objects)
		if (information != None) and (len(objects) != 0):
			### change dialog history
			dialog_history['songs'] = songs
			dialog_history['names'] = names
			dialog_history['types'] = types
			dialog_history['properties'] = properties
			### get response information
			response_information = []
			dialog_history = {'songs' : None, 'names' : None, 'types' : None, 'properties' : None}
			field = {'_id' : 0, 'title' : 0, 'singers': 0, 'composers': 0, 'name' : 0, 'types' : 0, 'properties' : 0, 'time' : 0, 'views' : 0, 'link' : 0}
			for object_ in objects:
				field.pop(object_)
			documents = song_collection.find(information, field)
			if (len(list(documents)) != 0):
				documents = song_collection.find(information, field)
				for document in documents:
					response_information.append(document)
				### generate response
				if not (len(response_information) == 0):
					if (len(objects) == 1):
						if (objects[0] == 'title'):
							response['text'] += 'là bài ' + self.combine(response_information[0]['title'])
							dialog_history['songs'] = [response_information[0]['title']]
						if (objects[0] == 'singers'):
							response['text'] += self.combine(response_information[0]['singers']) + ' hát bài đó'
							dialog_history['names'] = response_information[0]['singers']
						if (objects[0] == 'composers'):
							response['text'] += 'bài hát do ' + self.combine(response_information[0]['composers']) + ' sáng tác'
							dialog_history['names'] = response_information[0]['composers']
						if (objects[0] == 'time'):
							response['text'] += 'bài hát được phát hành vào ' + self.combine(response_information[0]['time'])
					if (len(objects) > 1):
						response['text'] = 'bài hát'
						if ('title' in objects):
							response['text'] += ' ' + self.combine(response_information[0]['title'])
							dialog_history['songs'] = [response_information[0]['title']]
						if ('singers' in objects):
							response['text'] += ' được thể hiện bởi ' + self.combine(response_information[0]['singers'])
							dialog_history['names'] = response_information[0]['singers']
						if ('composers' in objects):
							response['text'] += ' do' + self.combine(response_information[0]['composers']) + ' sáng tác'
							dialog_history['names'] = response_information[0]['composers']
						if ('time' in objects):
							response['text'] += ' được phát hành vào thời gian ' + self.combine(response_information[0]['time'])

		return response, dialog_history


	def generate_type_2(self, text, songs, names, types, properties, song_collection, dialog_history):
		### get request objects
		objects = self.get_request_information(text, songs, names, types, properties, song_collection, dialog_history)
		### get input information
		if (songs == None):
			songs = dialog_history['songs']
		if (names == None):
			names = dialog_history['names']
		if (types == None):
			types = dialog_history['types']
		if (properties == None):
			properties = dialog_history['properties']
		information = self.mongo_form(songs, names, types, properties)
		### renerate response
		response = {'text' : '', 'link' : ''}

		if (information == None) and (len(objects) != 0):
			if (objects[0] == 'title'):
				response['text'] += 'bạn muốn bài hát như thế nào?'
			if (objects[0] == 'singers'):
				response['text'] += 'bạn muốn tìm ca sĩ nào?'
			if (objects[0] == 'composers'):
				response['text'] += 'bạn muốn tìm nhạc sĩ nào?'

		if (information != None) and (len(objects) != 0):
			### get response information
			response_information = []
			dialog_history = {'songs' : None, 'names' : None, 'types' : None, 'properties' : None}
			field = {'_id' : 0, 'title' : 0, 'singers': 0, 'composers': 0, 'name' : 0, 'types' : 0, 'properties' : 0, 'time' : 0, 'views' : 0, 'link' : 0}
			for object_ in objects:
				field.pop(object_)
			documents = song_collection.find(information, field)
			if (len(list(documents)) != 0):
				documents = song_collection.find(information, field)
				for document in documents:
					response_information.append(document)
				### generate response
				if not (len(response_information) == 0):
					if (len(objects) == 1):
						if (objects[0] == 'title'):
							response['text'] += 'là bài ' + self.combine(response_information[0]['title'])
							dialog_history['songs'] = [response_information[0]['title']]
						if (objects[0] == 'singers'):
							response['text'] += self.combine(response_information[0]['singers']) + ' hát bài đó'
							dialog_history['names'] = response_information[0]['singers']
						if (objects[0] == 'composers'):
							response['text'] += 'bài hát do ' + self.combine(response_information[0]['composers']) + ' sáng tác'
							dialog_history['names'] = response_information[0]['composers']
						if (objects[0] == 'time'):
							response['text'] += 'bài hát được phát hành vào ' + self.combine(response_information[0]['time'])
					if (len(objects) > 1):
						response['text'] = 'bài hát'
						if ('title' in objects):
							response['text'] += ' ' + self.combine(response_information[0]['title'])
							dialog_history['songs'] = [response_information[0]['title']]
						if ('singers' in objects):
							response['text'] += ' được thể hiện bởi ' + self.combine(response_information[0]['singers'])
							dialog_history['names'] = response_information[0]['singers']
						if ('composers' in objects):
							response['text'] += ' do ' + self.combine(response_information[0]['composers']) + ' sáng tác'
							dialog_history['names'] = response_information[0]['composers']
						if ('time' in objects):
							response['text'] += ' được phát hành vào thời gian ' + self.combine(response_information[0]['time'])

		return response, dialog_history


	def get_response(self, text, songs, names, types, properties, song_collection, dialog_history):
		response = {'text' : '', 'link' : ''}
		type_ = 1

		for i in range(len(self.non_specifics)):
			if (text.lower().find(self.non_specifics[i]) != -1):
				type_ = 2
				break

		if (type_ == 1):
			response, dialog_history = self.generate_type_1(text, songs, names, types, properties, song_collection, dialog_history)

		if (type_ == 2):
			response, dialog_history = self.generate_type_2(text, songs, names, types, properties, song_collection, dialog_history)

		if (response['text'] == ''):
			response['text'] = 'cái này mình không rõ, hỏi câu khác đi :/'

		return response, dialog_history
