
class SingerComposerDetector(object):
	"""

	"""
	def __init__(self):
		pass


	def detect(self, text, collection):
		list_names = []
		# get all singers and composers in collection
		for document in collection.find({}, {'_id' : 0, 'title' : 0, 'description' : 0, 'type' : 0, 'property' : 0, 'time' : 0, 'rate' : 0, 'link' : 0}):
			list_names += document['singer']
			list_names += document['composer']
		list_names = list(set(list_names))
		# longest matching
		names = []
		while 1:
			name = ''
			for i in range(len(list_names)):
				if ((text.lower().find(list_names[i]) != -1) and (len(list_names[i]) > len(name))):
					name = list_names[i]
			if (name != ''):
				idx = text.lower().find(name)
				text = text[:idx] + '<name>' + text[idx + len(name):]
				names.append(name)
			else:
				break
		# return
		if (len(names) == 0):
			return text, None
		else:
			return text, names