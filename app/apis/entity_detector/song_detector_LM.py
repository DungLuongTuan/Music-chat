
class SongDetectorLM(object):
	"""

	"""
	def __init__(self):
		pass

	def detect(self, text, collection):
		### longest matching
		# get all title in collection
		list_title = set()
		for song in collection.find({}, {'_id' : 0, 'singer' : 0, 'composer' : 0, 'description' : 0, 'type' : 0, 'property' : 0, 'time' : 0, 'rate' : 0, 'link' : 0}):
			list_title.add(song['title'])
		list_title = list(list_title)
		# longest matching
		titles = []
		while 1:
			title = ''
			for i in range(len(list_title)):
				if ((text.lower().find(list_title[i]) != -1) and (len(list_title[i]) > len(title))):
					title = list_title[i]
			if (title != ''):
				idx = text.lower().find(title)
				text = text[:idx] + '<title>' + text[idx + len(title):]
				titles.append(title)
			else:
				break
		# return
		if (len(titles) == 0):
			return text, None
		else:
			return text, titles
		### NER