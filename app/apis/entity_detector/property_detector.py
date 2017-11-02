
class PropertyDetector(object):
	"""

	"""
	def __init__(self):
		pass


	def detect(self, text, collection):
		list_properties = []
		standard_properties = []
		# get all properties in collection
		f = open('./data/dictionary/entity_dictionary/property_dictionary', 'r')
		for row in f:
			row_split = row[:-1].split('\t')
			list_properties.append(row_split[0])
			standard_properties.append(row_split[1])
		f.close()
		# longest matching
		properties = []
		while 1:
			property_ = ''
			for i in range(len(list_properties)):
				if ((text.lower().find(list_properties[i]) != -1) and (len(list_properties[i]) > len(property_))):
					property_ = list_properties[i]
			if (property_ != ''):
				idx = text.lower().find(property_)
				text = text[:idx] + '<property>' + text[idx + len(property_):]
				properties.append(standard_properties[list_properties.index(property_)])
			else:
				break
		# return
		if (len(properties) == 0):
			return text, None
		else:
			return text, properties