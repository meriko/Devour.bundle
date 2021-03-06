TITLE = 'Devour'
DEVOUR_URL = 'http://devour.com/'

###################################################################################################
def Start():

	ObjectContainer.title1 = TITLE
	HTTP.CacheTime = 300
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:18.0) Gecko/20100101 Firefox/18.0'

###################################################################################################
@handler('/video/devour', TITLE)
def MainMenu():

	oc = ObjectContainer()

	oc.add(DirectoryObject(key=Callback(LatestList, page=1), title="Latest Videos"))
	oc.add(SearchDirectoryObject(identifier="com.plexapp.plugins.devour", title="Search for Videos", prompt="Search Devour for...", term="Videos"))

	return oc

###################################################################################################
@route('/video/devour/latest/{page}', page=int, allow_sync=True)
def LatestList(page):

	oc = ObjectContainer(title2="Latest Videos")
	result = {}

	@parallelize
	def GetVideos():

		url = DEVOUR_URL
		if page > 1:
			url = '%s%d/' % (url, page)

		html = HTML.ElementFromURL(url)
		videos = html.xpath("//*[contains(@class, 'article-list')]//*[contains(@class, 'article')]")

		for num in range(len(videos)):
			video = videos[num]

			@task
			def GetVideo(num=num, result=result, video=video):
				try:
					devour_url = video.xpath('./a')[0].get('href')
					devour_html = HTML.ElementFromURL(devour_url, cacheTime=CACHE_1WEEK)
					url = devour_html.xpath("//*[contains(@class, 'video-wrapper')]//iframe/@src")[0]
					video = URLService.MetadataObjectForURL(url)

					if video is not None:
						# Use the Devour-provided title, description vs. the ones assocaited with the underlying clips.
						try:
							video.title = devour_html.xpath('//div[@id="left"]/h1//text()')[0]
							description = devour_html.xpath('//div[@id="left"]/p//text()')
							video.summary = ''.join(description).strip()
						except:
							pass

						result[num] = video
				except:
					pass

	keys = result.keys()
	keys.sort()

	for key in keys:
		oc.add(result[key])

	oc.add(NextPageObject(key=Callback(LatestList, page=page+1), title="More Videos..."))

	return oc
