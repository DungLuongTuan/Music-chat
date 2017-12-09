from pymongo import MongoClient

def normalize(text):
	text = text.replace('  ', ' ', 1000)
	while (text[0] == ' '):
		text = text[1:]
	while (text[-1] == ' '):
		text = text[:-1]
	return text

def main():
	client = MongoClient()
	db = client['project-nlp']
	song_collection = db.songCollection
	documents = song_collection.find({'composers' : None}, no_cursor_timeout = True)
	cnt = 0
	for document in documents:
		document['composers'] = ['không xác định']
		song_collection.update({'_id':document['_id']}, {"$set": document}, upsert=False)
	documents.close()

if __name__ == '__main__':
	main()