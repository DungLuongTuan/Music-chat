from bs4 import BeautifulSoup
import urllib3
import requests
from pymongo import MongoClient

def main():
	client = MongoClient()
	db = client['project-nlp']
	song_collection = db.songCollection
	artist_collection = db.artistCollection
	http = urllib3.PoolManager()
	for i in range(11, 100):
		print(i)
		page = http.request('GET', 'https://mp3.zing.vn/the-loai-nghe-si/Viet-Nam/IWZ9Z08I.html?&page=' + str(i))
		soup = BeautifulSoup(page.data, 'html.parser')
		for content in soup.find_all('div', class_ = 'item'):
			split_content = str(content).split('\n')
			### get songs url
			extension = split_content[1].split(' ')[2][6:-1]
			singer_url = 'https://mp3.zing.vn' + extension
			### get singer name
			singer_name = split_content[5].split('"')[9]
			### get song info
			for j in range(1, 100):
				list_song_page = http.request('GET', singer_url + '/bai-hat?&page=' + str(j))
				list_song_soup = BeautifulSoup(list_song_page.data, 'html.parser')

				track_list = list_song_soup.find_all('a', class_ = '_trackLink')
				if (track_list == None):
					continue
				for k in range(3, len(track_list)):
					song_url = 'https://mp3.zing.vn' + str(track_list[k]).split('"')[3]
					song_page = http.request('GET', song_url)
					song_soup = BeautifulSoup(song_page.data, 'html.parser')
					# declare
					composers = None
					singers = None
					song = None
					lyric = None
					youtube_link = None
					views = None
					# composer
					composers_raw = song_soup.find('div', id = 'composer-container')
					if (composers_raw != None):
						composers = str(composers_raw.select('h2')[0].get_text())
					song_and_singers_raw = song_soup.find('h1', class_ = 'txt-primary')
					if (song_and_singers_raw != None):
						song_and_singers_raw = str(song_and_singers_raw.get_text()).replace('\n', '', 1000)
						song_and_singers_raw = song_and_singers_raw.replace('  ', '', 1000).split('-')
						# song name
						song = song_and_singers_raw[0]
						# singers name
						singers = song_and_singers_raw[1]
					# lyric
					lyric_raw = song_soup.find('p', class_ = 'fn-wlyrics fn-content')
					if (lyric_raw != None):
						lyric = str(lyric_raw.get_text())

					# if ((song != None) and (singers != None)):
					# 	# get link youtube
					# 	youtube_link_list = 'https://www.youtube.com/results?search_query=' + song + ' official mv ' + singers
					# 	youtube_link_list = '+'.join((youtube_link_list.replace('  ', ' ', 1000)).split(' '))
					# 	youtube_list_page = requests.get(youtube_link_list)
					# 	youtube_list_soup = BeautifulSoup(youtube_list_page.content, 'html.parser')
					# 	youtube_link_raw = youtube_list_soup.find('div', class_ = 'yt-lockup-content')
					# 	if (youtube_link_raw != None):
					# 		youtube_link = 'https://www.youtube.com' + str(youtube_link_raw.select('a')[0]).split('"')[9]
					# 	# get views
					# 	views_raw = youtube_list_soup.find('div', class_ = 'yt-lockup-content')
					# 	if (views_raw != None):
					# 		for li in views_raw.select('li'):
					# 			if (li.get_text().find('lượt xem') != -1):
					# 				views = str(li.get_text())

					song_document = {'name' : song,
									'singers' : singers,
									'composers' : composers,
									'link' : youtube_link,
									'views' : views,
									'lyric' : lyric}
					song_collection.insert_one(song_document)

			### get singer's story
			story_page = http.request('GET', singer_url + '/tieu-su')
			story_soup = BeautifulSoup(story_page.data, 'html.parser')
			story = story_soup.find('div', class_ = 'entry')
			if (story != None):
				story = str(story.get_text()).replace('  ', '', 1000)
				story = story.replace('\n\n', '\n', 1000)

			artist_document = {'name' : singer_name,
								'story' : story}
			artist_collection.insert_one(artist_document)


if __name__ == '__main__':
	main()