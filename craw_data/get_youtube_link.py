from bs4 import BeautifulSoup
import urllib3
import requests
from pymongo import MongoClient
import json

def main():
	client = MongoClient()
	db = client['project-nlp']
	song_collection = db.songCollection
	artist_collection = db.artistCollection
	http = urllib3.PoolManager()

	documents = song_collection.find({'link' : None}, no_cursor_timeout = True)
	for document in documents:
		if ((document['name'] != None) and (document['singers'] != None)):
			query = document['name'] + ' official mv ' + ', '.join(document['singers'])
			res = http.request('GET', 'https://www.googleapis.com/youtube/v3/search', fields = {"regionCode" : "vn", "part" : "snippet", "type" : "video", "key" : "AIzaSyCvyjvMcn351CQoq2RcFpym6jg-o0aygsE", "q" : query})
			data = json.loads(res.data.decode('utf-8'))
			if ('items' not in data.keys()) or (len(data['items']) == 0):
				continue
			link = "https://www.youtube.com/watch?v=" + data['items'][0]['id']['videoId']
			print(document['name'], ' ', document['singers'], ' ', link)
			document['link'] = link
			song_collection.update({'_id':document['_id']}, {"$set": document}, upsert=False)

if __name__ == '__main__':
	main()