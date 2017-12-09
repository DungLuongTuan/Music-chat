
class SingerComposerDetector(object):
	"""

	"""
	def __init__(self, collection):
		self.collection = collection
		self.get_names()


	def get_names(self):
		self.list_names = []
		# get all singers and composers in collection
		documents = self.collection.find({}, {'_id' : 0, 'title' : 0, 'types' : 0, 'properties' : 0, 'time' : 0, 'views' : 0, 'link' : 0, 'lyric' : 0, 'name' : 0}, no_cursor_timeout = True)
		for document in documents:
			self.list_names += document['singers']
			self.list_names += document['composers']
		self.list_names = list(set(self.list_names))


	def detect(self, text):
		# longest matching
		names = []
		words = text.split(' ')

		# detect all candidates
		candidates = []
		for i in range(len(words)):
			for j in range(len(words) - 1, -1, -1):
				cand = ' '.join(words[i:j+1])
				for k in range(len(self.list_names)):
					if (cand.lower() == self.list_names[k].lower()):
						candidates.append((self.list_names[k], i, j))
						break
		# overlap process
		if (len(candidates) != 0):
			cand = candidates[0]
			end = cand[2]
			for i in range(1, len(candidates)):
				if (candidates[i][1] > end):
					names.append(cand)
					cand = candidates[i]
					end = cand[2]
				else:
					if ((cand[2] - cand[1]) < (candidates[i][2] - candidates[i][1])):
						cand = candidates[i]
					end = max(candidates[i][2], cand[2])
			names.append(cand)
		# change text
		if (len(names) != 0):
			text_ = ' '.join(words[0:names[0][1]]) + ' ' + '<name>'
			for i in range(1, len(names)):
				text_ += ' ' + ' '.join(words[names[i-1][2] + 1 : names[i][1]]) + ' ' + '<name>'
			text_ += ' ' + ' '.join(words[names[len(names)-1][2] + 1:len(words)])
			text = text_
			names = [t[0] for t in names]
		# return
		if (len(names) == 0):
			return text, None
		return text, names
