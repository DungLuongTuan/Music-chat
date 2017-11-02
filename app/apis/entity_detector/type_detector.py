
class TypeDetector(object):
	"""

	"""
	def __init__(self):
		pass


	def detect(self, text, collection):
		list_types = []
		standard_types = []
		# get all types in collection
		f = open('./data/dictionary/entity_dictionary/type_dictionary', 'r')
		for row in f:
			row_split = row[:-1].split('\t')
			if (row_split[1] == '_'):
				continue
			list_types.append(row_split[0])
			standard_types.append(row_split[1])
		f.close()
		# longest matching
		types = []
		while 1:
			type_ = ''
			for i in range(len(list_types)):
				if ((text.lower().find(list_types[i]) != -1) and (len(list_types[i]) > len(type_))):
					type_ = list_types[i]
			if (type_ != ''):
				idx = text.lower().find(type_)
				text = text[:idx] + '<type>' + text[idx + len(type_):]
				types.append(standard_types[list_types.index(type_)])
			else:
				break
		# return
		if (len(types) == 0):
			return text, None
		else:
			return text, types