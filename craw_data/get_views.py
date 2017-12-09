from bs4 import BeautifulSoup
import urllib3
import requests
from pymongo import MongoClient
import json
import datetime

def main():
	client = MongoClient()
	db = client['project-nlp']
	song_collection = db.songCollection
	artist_collection = db.artistCollection
	http = urllib3.PoolManager()

	documents = song_collection.find({'views' : None}, no_cursor_timeout = True)
	for document in documents:
		if (document['link'] == None):
			continue
		page = http.request('GET', document['link'])
		soup = BeautifulSoup(page.data, 'html.parser')
		
		print(document['link'])
		time = soup.find('strong', class_ = 'watch-time-text')
		document['time'] = None
		if (time != None):
			time_ = time.get_text()
			time_ = time_.replace(',', '', 1000)
			time_split = time_.split(' ')
			if (len(time_split) == 6):
				day = time_split[2]
				month = time_split[4]
				year = time_split[5]
				document_time = datetime.datetime(int(year), int(month), int(day))
				print(document_time)
				document['time'] = document_time

		views = soup.find('div', class_ = 'watch-view-count')
		if (views != None):
			views_ = views.get_text().split(' ')
			views_ = views_[0].replace('.', '', 1000)
			if (views_.isdigit()):
				print(views_)
				document['views'] = views_

		song_collection.update({'_id':document['_id']}, {"$set": document}, upsert=False)


if __name__ == '__main__':
	main()