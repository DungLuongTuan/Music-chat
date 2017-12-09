import re

class ShowProcessor(object):
	def __init__(self, non_specifics, composer_words, singer_words, title_words, type_words, property_words, number_dictionary, negative_dictionary, lyric_words, all_words):
		self.non_specifics = non_specifics
		self.composer_words = composer_words
		self.singer_words = singer_words
		self.title_words = title_words
		self.type_words = type_words
		self.property_words = property_words
		self.number_dictionary = number_dictionary
		self.negative_dictionary = negative_dictionary
		self.lyric_words = lyric_words
		self.all_words = all_words
		

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
		for word in self.lyric_words:
			if (text.lower().find(word) != -1):
				request_information.append('lyric')
				break
		for word in self.all_words:
			if (text.lower().find(word) != -1):
				request_information = ['title', 'singers', 'composers', 'types', 'time']
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


	def generate_type_1(self, text, songs, names, types, properties, song_collection, artist_collection, dialog_history):
		### get request objects
		objects = self.get_request_information(text, songs, names, types, properties, song_collection, dialog_history)
		### get input information
		information = self.mongo_form(songs, names, types, properties)
		### get number of request list
		numbers = re.findall(r'\d+', text)
		num = 1
		for word in self.number_dictionary:
			if (text.lower().find(word) != -1):
				num = -1
		for number in numbers:
			num = max(num, int(number))
		if (num == -1):
			num = 1000000000
		### get property of request sentence
		prop = 1
		for word in self.negative_dictionary:
			if (text.lower().find(word) != -1):
				print('word: ', word)
				prop = -1
		### renerate response
		response = {'text' : '', 'link' : ''}
		### show response dictionary
		dictionary = {'title' : 'bài hát: ', 'singers' : 'thể hiện: ', 'composers' : 'sáng tác: ', 'types' : 'thể loại: ', 'time' : 'phát hành: ', 'lyric' : 'lời bài hát:\n'}
		if (information != None):
			### get response information
			response_information = []
			field = {'_id' : 0, 'title' : 0, 'singers': 0, 'composers': 0, 'name' : 0, 'types' : 0, 'properties' : 0, 'time' : 0, 'views' : 0, 'link' : 0, 'lyric' : 0}
			for object_ in objects:
				field.pop(object_)
			documents = song_collection.find(information, field)
			if (len(list(documents)) != 0):
				documents = song_collection.find(information, field).sort('views')
				for document in documents:
					response_information.append(document)
				### generate response
				if not (len(response_information) == 0):
					if (prop == 1):
						response_information = response_information[::-1]

					number_response = min(num, len(response_information))
					if (number_response == 1):
						for object_ in objects:
							response['text'] += dictionary[object_] + self.combine(response_information[0][object_]) + '\n'
					else:
						for i in range(number_response):
							response['text'] += str(i+1) + '.\n'
							for object_ in objects:
								response['text'] += dictionary[object_] + self.combine(response_information[i][object_]) + '\n'
					response['text'] = response['text'][:-1]

		if (information == None) and ('lyric' in objects) and (dialog_history['songs'] != None):
			response_information = None
			field = {'_id' : 0, 'title' : 0, 'singers': 0, 'composers': 0, 'name' : 0, 'types' : 0, 'properties' : 0, 'time' : 0, 'views' : 0, 'link' : 0}
			documents = song_collection.find({'title' : dialog_history['songs'][0]}, field)
			if (len(list(documents)) != 0):
				documents = song_collection.find({'title' : dialog_history['songs'][0]}, field).sort('views')
				for document in documents:
					response_information = document
					break
				if (response_information != None):
					if (response_information['lyric'] != None):
						response['text'] = dictionary['lyric'] + response_information['lyric']
					else:
						response['text'] = 'mình không biết lời bài hát này'

		return response, dialog_history


	def generate_type_2(self, text, songs, names, types, properties, song_collection, artist_collection, dialog_history):
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
		### get number of request list
		numbers = re.findall(r'\d+', text)
		num = 1
		for word in self.number_dictionary:
			if (text.lower().find(word) != -1):
				num = -1
		for number in numbers:
			num = max(num, int(number))
		if (num == -1):
			num = 1000000000
		### get property of request sentence
		prop = 1
		for word in self.negative_dictionary:
			if (text.lower().find(word) != -1):
				prop = -1
		### renerate response
		response = {'text' : '', 'link' : ''}
		dictionary = {'title' : 'bài hát: ', 'singers' : 'thể hiện: ', 'composers' : 'sáng tác: ', 'types' : 'thể loại: ', 'time' : 'phát hành: ', 'lyric' : 'lời bài hát:\n'}
		if (information != None):
			### get response information
			response_information = []
			field = {'_id' : 0, 'title' : 0, 'singers': 0, 'composers': 0, 'types' : 0, 'properties' : 0, 'time' : 0, 'views' : 0, 'link' : 0, 'lyric' : 0}
			for object_ in objects:
				field.pop(object_)
			documents = song_collection.find(information, field)
			if (len(list(documents)) != 0):
				documents = song_collection.find(information, field).sort('views')
				for document in documents:
					response_information.append(document)
				### generate response
				if not (len(response_information) == 0):
					if (prop == 1):
						response_information = response_information[::-1]

					number_response = min(num, len(response_information))
					if (number_response == 1):
						for object_ in objects:
							response['text'] += dictionary[object_] + self.combine(response_information[0][object_]) + '\n'
					else:
						for i in range(number_response):
							response['text'] += str(i+1) + '.\n'
							for object_ in objects:
								response['text'] += dictionary[object_] + self.combine(response_information[i][object_]) + '\n'
					response['text'] = response['text'][:-1]

		if (information == None) and ('lyric' in objects) and (dialog_history['songs'] != None):
			response_information = None
			field = {'_id' : 0, 'title' : 0, 'singers': 0, 'composers': 0, 'name' : 0, 'types' : 0, 'properties' : 0, 'time' : 0, 'views' : 0, 'link' : 0}
			documents = song_collection.find({'title' : dialog_history['songs'][0]}, field)
			if (len(list(documents)) != 0):
				documents = song_collection.find({'title' : dialog_history['songs'][0]}, field).sort('views')
				for document in documents:
					response_information = document
					break
				if (response_information != None):
					if (response_information['lyric'] != None):
						response['text'] = dictionary['lyric'] + response_information['lyric']
					else:
						response['text'] = 'bài này mình không biết lời :(('

		return response, dialog_history


	def get_response(self, text, songs, names, types, properties, song_collection, artist_collection, dialog_history):
		response = {'text' : '', 'link' : ''}
		type_ = 1

		for i in range(len(self.non_specifics)):
			if (text.lower().find(self.non_specifics[i]) != -1):
				type_ = 2
				break

		if (type_ == 1):
			response, dialog_history = self.generate_type_1(text, songs, names, types, properties, song_collection, artist_collection, dialog_history)

		if (type_ == 2):
			response, dialog_history = self.generate_type_1(text, songs, names, types, properties, song_collection, artist_collection, dialog_history)

		if (response['text'] == ''):
			response['text'] = 'mình không có thông tin mà bạn muốn tìm :('

		return response, dialog_history


