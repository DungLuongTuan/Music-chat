
class SongDetectorLM(object):
	"""

	"""
	def __init__(self, collection):
		self.collection = collection
		self.get_titles()


	def get_titles(self):
		# get all title in collection
		self.list_title = set()
		documents = self.collection.find({}, {'_id' : 0, 'name' : 0, 'singers' : 0, 'composers' : 0, 'types' : 0, 'properties' : 0, 'time' : 0, 'views' : 0, 'link' : 0}, no_cursor_timeout = True)
		for song in documents:
			self.list_title.add(song['title'])
		self.list_title = list(self.list_title)
		documents.close()


	def detect(self, text):
		### longest matching
		# longest matching
		titles = []
		words = text.split(' ')

		candidates = []
		# detect all candidates
		for i in range(len(words)):
			# rules of detecting title of song
			ok = False
			if (i - 1 >= 0) and (words[i-1].lower() in ['bài', 'và', ',']):
				ok = True
			if (i - 2 >= 0) and (' '.join(words[i-2:i]).lower() in ['bài hát', 'ca khúc']):
				ok = True
			if (i - 3 >= 0) and (' '.join(words[i-3:i]).lower() in ['mở cho mình']):
				ok = True
			if (ok == False):
				continue
			# longest matching title
			for j in range(len(words) - 1, -1, -1):
				cand = ' '.join(words[i:j+1])
				for k in range(len(self.list_title)):
					if (cand.lower() == self.list_title[k].lower()):
						candidates.append((self.list_title[k], i, j))
						break
		# overlap process
		if (len(candidates) != 0):
			cand = candidates[0]
			end = cand[2]
			for i in range(1, len(candidates)):
				if (candidates[i][1] > end):
					titles.append(cand)
					cand = candidates[i]
					end = cand[2]
				else:
					if ((cand[2] - cand[1]) < (candidates[i][2] - candidates[i][1])):
						cand = candidates[i]
					end = max(candidates[i][2], cand[2])
			titles.append(cand)
		# change text
		if (len(titles) != 0):
			text_ = ' '.join(words[0:titles[0][1]]) + ' ' + '<title>'
			for i in range(1, len(titles)):
				text_ += ' ' + ' '.join(words[titles[i-1][2] + 1 : titles[i][1]]) + ' ' + '<title>'
			text_ += ' ' + ' '.join(words[titles[len(titles)-1][2] + 1:len(words)])
			text = text_
			titles = [t[0] for t in titles]
		# return
		if (len(titles) == 0):
			return text, None
		return text, titles




		