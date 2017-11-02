# -*- coding: utf-8 -*-
import re
import random

class DialogManager(object):
	"""
		manage conversation and response suitable reply
	"""

	def __init__(self):
		self.load_domain_dictionary()


	def load_domain_dictionary(self):
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


	def combine(self, inp):
		if (isinstance(inp, list)):
			res = str(inp[0])
			for i in range(1, len(inp)):
				res += ' + ' + str(inp[i])
			return res
		else:
			return str(inp)


	def inform_state_tracker(self, text, songs, names, types, properties):
		# declare information dictionary
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
				dict_name['$or'].append({'singer': name})
				dict_name['$or'].append({'composer': name})
			information['$and'].append(dict_name)
		# append types information
		if not (types == None):
			dict_type = {'$or': []}
			for type_ in types:
				dict_type['$or'].append({'type': type_})
			information['$and'].append(dict_type)
		# append properties information
		if not (properties == None):
			dict_property = {'$or': []}
			for property_ in properties:
				dict_property['$or'].append({'property': property_})
			information['$and'].append(dict_property)
		# check text in whatever
		for sen in self.whatever_dictionary:
			if (text.lower().find(sen) != -1):
				information = {'$and': ['whatever']}
		# return
		if (len(information['$and']) == 0):
			return None
		else:
			return information


	def inform_generator(self, information, collection, last_inform):
		response = {'text' : '', 'link' : ''}
		new_inform = last_inform
		if (information == None):
			response['text'] += 'bạn muốn mở bài hát gì?'
		else:
			response_information = []
			if (information['$and'][0] == 'whatever'):
				for document in collection.find().limit(1).skip(random.randint(0, collection.find().count() - 1)):
					response_information.append(document)
				response['text'] += 'bài hát ' + response_information[0]['title'] + ' đã được phát'
				response['link'] += response_information[0]['link']
			else:
				field = {'singer': 0, 'composer': 0, 'description' : 0, 'type' : 0, 'property' : 0, 'time' : 0, 'rate' : 0}
				for document in collection.find(information, field).sort('rate'):
					response_information.append(document)
				response['text'] += 'bài hát ' + response_information[0]['title'] + ' đã được phát'
				response['link'] += response_information[0]['link']
				new_inform = [information]
		return response, new_inform


	def search_state_tracker(self, text, songs, names, types, properties):
		### detect request object in input sentence
		# declare list of detected informations
		detected_information = []
		if not (songs == None):
			detected_information.append('title')
		if not (types == None):
			detected_information.append('type')
		if not (properties == None):
			detected_information.append('property')
		# detect request informations
		request_information = []
		for word in self.composer_words:
			if (text.lower().find(word) != -1):
				request_information.append('composer')
				break
		for word in self.singer_words:
			if (text.lower().find(word) != -1):
				request_information.append('singer')
				break
		for word in self.title_words:
			if (text.lower().find(word) != -1):
				request_information.append('title')
				break
		for word in self.type_words:
			if (text.lower().find(word) != -1):
				request_information.append('type')
				break
		for word in self.property_words:
			if (text.lower().find(word) != -1):
				request_information.append('property')
				break
		# detect request objects
		objects = []
		for info in request_information:
			if not (info in detected_information):
				objects.append(info)

		### change all input information in to mongodb input form
		# declare information dictionary
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
				dict_name['$or'].append({'singer': name})
				dict_name['$or'].append({'composer': name})
			information['$and'].append(dict_name)
		# append types information
		if not (types == None):
			dict_type = {'$or': []}
			for type_ in types:
				dict_type['$or'].append({'type': type_})
			information['$and'].append(dict_type)
		# append properties information
		if not (properties == None):
			dict_property = {'$or': []}
			for property_ in properties:
				dict_property['$or'].append({'property': property_})
			information['$and'].append(dict_property)
		if (len(information['$and']) == 0):
			information = None
		### return
		return objects, information


	def search_generator(self, objects, information, collection):
		response = {'text' : '', 'link' : ''}
		if (information == None):
			if (objects[0] == 'title'):
				response['text'] += 'bạn muốn bài hát như thế nào?'
			if (objects[0] == 'singer'):
				response['text'] += 'bạn muốn tìm ca sĩ nào?'
			if (objects[0] == 'composer'):
				response['text'] += 'bạn muốn tìm nhạc sĩ nào?'
		else:
			### get response information
			response_information = []
			field = {'_id' : 0, 'title' : 0, 'singer': 0, 'composer': 0, 'description' : 0, 'type' : 0, 'property' : 0, 'time' : 0, 'rate' : 0, 'link' : 0}
			for object_ in objects:
				field.pop(object_)
			for document in collection.find(information, field):
				response_information.append(document)
			### generate response
			if not (len(response_information) == 0):
				if (len(objects) == 1):
					if (objects[0] == 'title'):
						response['text'] += 'là bài ' + self.combine(response_information[0][objects[0]])
					if (objects[0] == 'singer'):
						response['text'] += self.combine(response_information[0][objects[0]]) + ' hát bài đó'
					if (objects[0] == 'composer'):
						response['text'] += 'bài hát do ' + self.combine(response_information[0][objects[0]]) + ' sáng tác'
					if (objects[0] == 'time'):
						response['text'] += 'bài hát được phát hành vào ' + self.combine(response_information[0][objects])
				if (len(objects) > 1):
					response['text'] = 'bài hát'
					if ('title' in objects):
						response['text'] += ' ' + self.combine(response_information[0]['title'])
					if ('singer' in objects):
						response['text'] += ' được thể hiện bởi ' + self.combine(response_information[0]['singer'])
					if ('composer' in objects):
						response['text'] += ' do' + self.combine(response_information[0]['composer']) + ' sáng tác'
					if ('time' in objects):
						response['text'] += ' được phát hành vào thời gian ' + self.combine(response_information[0]['time'])
			else:
				response['text'] = 'mình không biết :(('
		### return
		return response


	def show_state_tracker(self, text, songs, names, types, properties):
		### detect request object in input sentence
		# declare list of detected informations
		detected_information = []
		if not (songs == None):
			detected_information.append('title')
		if not (types == None):
			detected_information.append('type')
		if not (properties == None):
			detected_information.append('property')
		# detect request informations
		request_information = []
		for word in self.composer_words:
			if (text.lower().find(word) != -1):
				request_information.append('composer')
				break
		for word in self.singer_words:
			if (text.lower().find(word) != -1):
				request_information.append('singer')
				break
		for word in self.title_words:
			if (text.lower().find(word) != -1):
				request_information.append('title')
				break
		for word in self.type_words:
			if (text.lower().find(word) != -1):
				request_information.append('type')
				break
		for word in self.property_words:
			if (text.lower().find(word) != -1):
				request_information.append('property')
				break
		for word in self.all_words:
			if (text.lower().find(word) != -1):
				request_information = ['title', 'singer', 'composer', 'type', 'time', 'description']
		# detect request objects
		objects = []
		for info in request_information:
			if not (info in detected_information):
				objects.append(info)

		### change all input information in to mongodb input form
		# declare information dictionary
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
				dict_name['$or'].append({'singer': name})
				dict_name['$or'].append({'composer': name})
			information['$and'].append(dict_name)
		# append types information
		if not (types == None):
			dict_type = {'$or': []}
			for type_ in types:
				dict_type['$or'].append({'type': type_})
			information['$and'].append(dict_type)
		# append properties information
		if not (properties == None):
			dict_property = {'$or': []}
			for property_ in properties:
				dict_property['$or'].append({'property': property_})
			information['$and'].append(dict_property)
		if (len(information['$and']) == 0):
			information = None
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
		### return
		return num, prop, objects, information


	def show_generator(self, num, prop, objects, information, collection):
		response = {'text' : '', 'link' : ''}
		if (information != None):
			### show response dictionary
			dictionary = {'title' : 'bài hát: ', 'singer' : 'thể hiện: ', 'composer' : 'sáng tác: ', 'description' : 'mô tả: ', 'type' : 'thể loại: ', 'time' : 'phát hành: '}
			### get response information
			response_information = []
			field = {'_id' : 0, 'title' : 0, 'singer': 0, 'composer': 0, 'description' : 0, 'type' : 0, 'property' : 0, 'time' : 0, 'rate' : 0, 'link' : 0}
			for object_ in objects:
				field.pop(object_)
			for document in collection.find(information, field).sort('rate'):
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
			else:
				response['text'] = 'cái này mình không biết :(('
		### return
		if (response['text'] == ''):
			return 'không tìm thấy thông tin'
		else:
			return response


	def change_generator(self, information, collection, last_inform):
		response = {'text' : '', 'link' : ''}
		new_inform = last_inform
		if (len(last_inform) == 0):
			response['text'] = 'bạn muốn mở bài gì?'
		else:
			response_information = []
			field = {'singer': 0, 'composer': 0, 'description' : 0, 'type' : 0, 'property' : 0, 'time' : 0, 'rate' : 0}
			for document in collection.find(last_inform[-1], field).sort('rate'):
				response_information.append(document)
			if (len(response_information) > len(last_inform)):
				response['text'] = 'bài hát ' + response_information[len(last_inform)]['title'] + ' đã được phát'
				response['link'] = response_information[len(last_inform)]['link']
				new_inform.append(last_inform[-1])
			else:
				response['text'] = 'bạn muốn đổi bài gì?'

		return response, new_inform


	def get_response(self, intent, text, songs, names, types, properties, collection, last_inform):
		response = {'text' : '', 'link' : ''}
		### process inform request
		if (intent == 'inform'):
			information = self.inform_state_tracker(text, songs, names, types, properties)
			response, new_inform = self.inform_generator(information, collection, last_inform)
			if not (new_inform == []):
				last_inform = new_inform
		### process search request
		if (intent == 'search'):
			objects, information = self.search_state_tracker(text, songs, names, types, properties)
			response = self.search_generator(objects, information, collection)
		### process show request
		if (intent == 'show'):
			num, prop, objects, information = self.show_state_tracker(text, songs, names, types, properties)
			response = self.show_generator(num, prop, objects, information, collection)
		### process change request
		if (intent == 'change'):
			information = self.inform_state_tracker(text, songs, names, types, properties)
			response, last_inform = self.change_generator(information, collection, last_inform)
		### return response
		return response, last_inform