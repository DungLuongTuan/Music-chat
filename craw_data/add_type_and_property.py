from pymongo import MongoClient
import datetime

def main():
	client = MongoClient()
	db = client['project-nlp']
	song_collection = db.songCollection
	# documents = song_collection.find({'time' : {'$gte' : datetime.datetime(2017, 1, 1)}, 'types' : None, 'singers' : 'Soobin Hoàng Sơn'}, no_cursor_timeout = True)
	documents = song_collection.find({'types' : None, 'singers' : 'Sơn Tùng MTP'}, no_cursor_timeout = True)
	for document in documents:
		print(document['title'])
		print(document['singers'])
		print(document['composers'])
		print(document['link'])
		types = input('types=')
		properties = input('properties=')
		if (len(types) != 0):
			document['types'] = types.split(',')
		else:
			document['types'] = []
		if (len(properties) != 0):
			document['properties'] = properties.split(',')
		else:
			document['properties'] = []
		song_collection.update({'_id':document['_id']}, {"$set": document}, upsert=False)
	documents.close()

if __name__ == '__main__':
	main()