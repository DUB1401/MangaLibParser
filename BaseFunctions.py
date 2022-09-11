from operator import truediv
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from sys import platform
from time import sleep

import hashlib

import logging
import re
import os

#==========================================================================================#
#=== БАЗОВЫЕ ФУНКЦИИ ===#
#==========================================================================================#

#Перечисление областей тегов HTML.
TagsHTML = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')

#Выключает компьютер: работает на Windows и Linux.
def Shutdown():
	if platform == "linux" or platform == "linux2":
		os.system('sudo shutdown now')
	elif platform == "win32":
		os.system("shutdown /s")

#Удаляет теги HTML из строки.
def RemoveHTML(TextHTML):
  CleanText = re.sub(TagsHTML, '', str(TextHTML))
  return str(CleanText)

#Удаляет из строки символы: новой строки, табуляции, пробелы из начала и конца.
def RemoveSpaceSymbols(Text):
    Text = Text.replace('\n', '')
    Text = Text.replace('\t', '')
    Text = ' '.join(Text.split())
    return Text.strip()

#Заменяет символ новой строки на запятую с пробелом.
def ReplaceEndlToComma(Text):
    Text = Text.strip()
    Text = Text.replace('\n', ', ')
    return Text

#Преобразует литеральное число в int.
def LiteralToInt(String):
    if String.isdigit():
        return int(String)
    else:
        Number = float(String[:-1]) * 1000
    return int(Number)

#Очищает консоль.
def Cls():
    os.system('cls' if os.name == 'nt' else 'clear')

#Выводит прогресс процесса.
def PrintProgress(String, Current, Total):
	Cls()
	print(String, " ", Current, " / ", Total)

#Удаляет аргументы из URL.
def RemoveArgumentsFromURL(URL):
	return str(URL).split('?')[0]

#==========================================================================================#
#=== ПАРСИНГ ГЛАВ ===#
#==========================================================================================#

#Выполнение, если указано настройками, входа на сайт и отключение уведомления о возрастном ограничении.
def SignInAndDisableWarning(Browser, Settings):
	if Settings["sign-in"] == True:
		if Settings["email"] != "" and Settings["password"] != "":
			LogIn(Browser, Settings)
			logging.info("Sign in as \"" + Settings["email"] + "\".")
		else:
			logging.error("Uncorrect user data! Check \"Settings.json\".")

	if Settings["disable-age-limit-warning"] == True:
		DisableAgeLimitWarning(Browser, Settings)
		logging.info("Age limit warning disabled.")

#Возвращает результат проверки: платный ли тайтл.
def IsMangaPaid(Browser, MangaName, Settings):
	#Проверка нахождения на нужной странице.
	URLinfo = Settings["domain"] + MangaName + "?section=info"
	if Browser.current_url != URLinfo:
		Browser.get(URLinfo)

	#Поиск иконки покупки.
	BodyHTML = Browser.execute_script("return document.body.innerHTML;")
	Soup = BeautifulSoup(BodyHTML, "lxml")
	if Soup.find_all('i', {'class': 'fa fa-shopping-cart mr-5'}) == []:
		return False
	else:
		return True

#Получает ID главы на сайте.
def GetChapterID(Browser, ChapterLink, Settings, GoToPage):
	if GoToPage == True:
		Browser.get(Settings["domain"][:-1] + ChapterLink)
	SiteWindowData = Browser.execute_script("return window.__info;")
	return SiteWindowData["current"]["id"]

#Возвращает уникальный BranchID на основе названия манги.
def GetCodeBID(MangaName, StrBID):
		MangaIntName = hashlib.md5(MangaName.encode())
		MangaIntName = MangaIntName.hexdigest()
		return str(int(MangaIntName, 16)) + StrBID

#Вход на сайт.
def LogIn(Browser, Settings):
	Browser.get("https://lib.social/login?from=https%3A%2F%2F" + Settings["domain"].replace("https://", "").replace(".me/", "") + ".me")

	EmailInput = Browser.find_element(By.CSS_SELECTOR , "input[name=\"email\"]")
	PasswordInput = Browser.find_element(By.CSS_SELECTOR , "input[name=\"password\"]")

	EmailInput.send_keys(Settings["email"])
	PasswordInput.send_keys(Settings["password"])

	Browser.find_element(By.CLASS_NAME, "button_primary").click()

#Возвращает контейнер с данными о переводчике для записи в JSON.
def GetPublisherData(Div, Domain):
    Soup = BeautifulSoup(str(Div), "lxml")
    Bufer = {}
    Bufer['id'] = 0
    Bufer['name'] = RemoveSpaceSymbols(RemoveHTML(Soup.find('div', {'class': 'team-list-item__name'})))
    Bufer['img'] = str(Soup.find('div', {'class': 'team-list-item__cover'}))
    Bufer['img'] = Bufer['img'].split('(')[-1].split(')')[0].replace('?', '').replace('"', '')
    if Bufer['img'] != "/uploads/no-image.png":
        Bufer['dir'] = Bufer['img'].split('/')[5]
    else:
        Bufer['dir'] = Soup.find('a')['href'].split('/')[-1]
        Bufer['img'] = Domain[:-1] + Bufer['img']
    Bufer['tagline'] = ''
    Bufer['type'] = 'Переводчик'
    return Bufer

#Отключить уведомление о возрастном ограничении.
def DisableAgeLimitWarning(Browser, Settings):
	if Settings["domain"] == "https://mangalib.me/":
		Browser.get("https://mangalib.me/kimetsu-no-yaiba/v1/c1?page=1")
	elif Settings["domain"] == "https://hentailib.me/": 
		Browser.get("https://hentailib.me/oh-sheet-shadman/v1/c1?page=1")
	elif Settings["domain"] == "https://yaoilib.me/": 
		Browser.get("https://yaoilib.me/you-are-here/v1/c151?page=1")

	Browser.find_elements(By.CLASS_NAME, "control__text")[-1].click()
	Browser.find_element(By.CLASS_NAME, 'reader-caution-continue').click()

#Получает bid веток перевода.
def GetBID(Browser, MangaName, Settings):
	Browser.get(Settings["domain"] + MangaName + "?section=chapters")
	TranslateBranches = Browser.find_elements(By.CLASS_NAME, "team-list-item")
	BIDs = list()
	for InObj in TranslateBranches:
		if InObj.is_displayed() and InObj.is_enabled():
			InObj.click()
			BIDs.append(str(Browser.current_url).split('?')[-1].split('&')[0].split('=')[1])
	return BIDs

#Открывает панель для получения названий глав, ссылок на главы и слайдов
def PrepareToParcingChapter(Browser, MangaName, Settings, BID):
	if BID is None:
		Browser.get(Settings["domain"] + MangaName + "?section=chapters")
	else:
		Browser.get(Settings["domain"] + MangaName + "?bid=" + str(BID) + "&section=chapters")
	#Ожидание полной подгрузки страницы.
	Wait = WebDriverWait(Browser, 500)
	Wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "media-chapter__name")))

	#Получение ссылки на последнюю главу.
	BodyHTML = Browser.execute_script("return document.body.innerHTML;")
	Soup = BeautifulSoup(BodyHTML, "lxml")
	LastChapter = Soup.find_all('div', {'class': 'media-chapter__name text-truncate'})[0]
	Soup = BeautifulSoup(str(LastChapter), "lxml")
	LastChapter = Soup.find('a')

	#Переход к последней главе.
	Browser.get(Settings["domain"][:-1] + LastChapter['href'])
	Browser.find_elements(By.CLASS_NAME, 'reader-header-action__text')[1].click()
	
#Получение списка названий глав.
def GetChaptersNames(Browser):
	BodyHTML = Browser.execute_script("return document.body.innerHTML;")
	Soup = BeautifulSoup(BodyHTML, "lxml")
	ChaptersNames = Soup.find_all('a', {'class': 'menu__item'})
	Bufer = []
	for InObj in ChaptersNames:
		Bufer.append(RemoveSpaceSymbols(RemoveHTML(InObj)))
	ChaptersNames = Bufer
	Bufer = []
	return ChaptersNames

#Получение списка ссылок на главы.
def GetChaptersLinks(Browser):
	BodyHTML = Browser.execute_script("return document.body.innerHTML;")
	Soup = BeautifulSoup(BodyHTML, "lxml")
	SmallSoup = Soup.find_all('div', {'class': 'modal__body'})
	SmallSoup = BeautifulSoup(str(SmallSoup[-1]), "lxml")
	ChaptersLinks = SmallSoup.find_all('a', {'class': 'menu__item'})
	
	Bufer = []
	for InObj in ChaptersLinks:
		Bufer.append(RemoveSpaceSymbols(RemoveHTML(InObj['href'])).split('?')[0])
	ChaptersLinks = Bufer
	Bufer = []
	
	return ChaptersLinks

#Возвращает список URL слайдов (компонент GetMangaSlidesUrlArray).
def GetSlides(Browser, FirstPage, FramesCount, Settings, ChapterLink):
	if Browser.current_url != FirstPage:
		Browser.get(FirstPage)
		logging.warning("Chapter: \"" + ChapterLink + "\". Restoring the chapter...")
	sleep(Settings["slide-interval"])
	#Получение ссылок на кадры главы.
	for i in range(0, int(FramesCount) - 1):
		#Проверка полной загрузки всех <img> на странице.
		while Browser.execute_script('''
        for (var img of document.getElementsByTagName("img")) {
            if (img.complete != true) return false;
        };
        return true;    
		''') == False:
			sleep(1)
		#Нажатие на слайд для перехода к следующему.
		Browser.find_element(By.CLASS_NAME, 'reader-view__container').click()
		#Пауза между перелистыванием для снижения нагрузки на сервер.
		sleep(Settings["slide-interval"])

	BodyHTML = Browser.execute_script("return document.body.innerHTML;")
	Soup = BeautifulSoup(BodyHTML, "lxml")
	SmallSoup = BeautifulSoup(str(Soup.find('div', {'class': 'reader-view__container'})), "html.parser")
	FramesLinksArray = SmallSoup.find_all('img', {"src": True})
	PreFrameLinks = []
	for i in range(len(FramesLinksArray)):
		PreFrameLinks.append(FramesLinksArray[i]['src'])

	return PreFrameLinks

#Получение списка ссылок на слайды манги и преобразование его в нужный формат.
def GetMangaSlidesUrlArray(Browser, ChapterLink, Settings):
	Browser.get(Settings["domain"][:-1] + ChapterLink)
	FirstPage = Browser.current_url
	BodyHTML = Browser.execute_script("return document.body.innerHTML;")
	Soup = BeautifulSoup(BodyHTML, "lxml")
	WebDriverWait(Browser, 60).until(EC.presence_of_element_located, (By.ID , "reader-pages"))
	FramesCount = Soup.find('select', {'id': 'reader-pages'})
	FramesCount = RemoveHTML(FramesCount)
	FramesCount = FramesCount.split()[-1]

	FramesLinks = GetSlides(Browser, FirstPage, FramesCount, Settings, ChapterLink)

	#Проверка ошибки: получен URL не всех слайдов.
	if len(FramesLinks) != int(FramesCount):
		logging.warning("Chapter: \"" + ChapterLink + "\" parced with errors. Not all slides were received: " + str(len(FramesLinks)) + " / " + FramesCount + ".")
		FramesLinks = GetSlides(Browser, FirstPage, FramesCount, Settings, ChapterLink)
		if len(FramesLinks) != int(FramesCount):
			logging.warning("Chapter: \"" + ChapterLink + "\" restoring failed. Not all slides were received: " + str(len(FramesLinks)) + " / " + FramesCount + ".")
	else:
		logging.info("Chapter: \"" + ChapterLink + "\" parced. Slides count: " + str(len(FramesLinks)) + ".")

	FrameHeights = []
	FrameWidths = []
	for i in range(len(FramesLinks)):
		FrameHeights.append(Browser.execute_script('''
			var img = new Image();
			img.src = arguments[0]
			return img.height
		''', FramesLinks[i]))

	for i in range(len(FramesLinks)):
		FrameWidths.append(Browser.execute_script('''
			var img = new Image();
			img.src = arguments[0]
			return img.width
		''', FramesLinks[i]))

	ChapterData = []
	
	for i in range(len(FramesLinks)):
		FrameData = dict()
		FrameData["link"] = FramesLinks[i]
		FrameData["width"] = FrameWidths[i]
		FrameData["height"] = FrameHeights[i]
		ChapterData.append(FrameData)

	return ChapterData

#Получение данных о манге и их сохранение в JSON.
def GetMangaData(Browser, MangaName, Settings):
	Browser.get(Settings["domain"] + MangaName + "?section=info")
	BodyHTML = Browser.execute_script("return document.body.innerHTML;")
	Soup = BeautifulSoup(BodyHTML, "lxml")
	SmallSoup = BeautifulSoup(str(Soup.find('div', {'class': 'media-sidebar__cover paper'})), "html.parser")
	
	SiteWindowData = Browser.execute_script("return window.__DATA__;")

	CoverURL = SmallSoup.find('img')['src']
   
	MangaNameRU = Soup.find('div', {'class': 'media-name__main'}).get_text()
	
	MangaNameEN = Soup.find('div', {'class': 'media-name__alt'})
	if MangaNameEN != None:
		MangaNameEN = MangaNameEN.get_text()
	
	AnotherName = ReplaceEndlToComma(Soup.find_all('div', {'class': 'media-info-list__value'})[-1].get_text())
	
	PreDescription = Soup.find('div', {'class': 'media-description__text'})
	Description = ""
	if PreDescription != None:
		Description = RemoveHTML(PreDescription.get_text()).strip()
	
	PrePublicationYear = Soup.find_all('a', {'class': 'media-info-list__item'})
	PublicationYear = 0
	for InObj in PrePublicationYear:
		if "Год релиза" in str(InObj):
			PublicationYear = int(RemoveHTML(InObj).replace('\n', ' ').split()[2])
	
	Rating = RemoveSpaceSymbols(Soup.find('div', {'class': 'media-rating__value'}).get_text())
	
	Voted = LiteralToInt(RemoveSpaceSymbols(Soup.find('div', {'class': 'media-rating__votes'}).get_text()))
	
	AgeLimit = Soup.find('div', {'class': 'media-info-list__value text-danger'})
	if AgeLimit != None:
		AgeLimit = int(AgeLimit.get_text()[:-1])
	else:
		AgeLimit = 0
   
	PreStatus = Soup.find_all('a', {'class': 'media-info-list__item'})
	Status = "Неизвестен"
	for InObj in PreStatus:
		if "Статус тайтла" in str(InObj):
			Status = RemoveHTML(InObj).replace('\n', ' ').split()[2]

	Type = RemoveHTML(Soup.find('div', {'class': 'media-info-list__value'}).get_text())
	
	MediaInfo = Soup.find_all('a', {'class': 'media-tag-item'})
	Genres = []
	Tags = []
	for InObj in MediaInfo:
		if "genres" in str(InObj):
			Genres.append(RemoveHTML(InObj))
		else:
			Tags.append(RemoveHTML(InObj))
	GenresArray = []
	for InObj in Genres:
		Bufer = {}
		Bufer['id'] = 0
		Bufer['name'] = str(InObj)
		GenresArray.append(Bufer)
	TagsArray = []
	for InObj in Tags:
		Bufer = {}
		Bufer['id'] = 0
		Bufer['name'] = str(InObj)
		TagsArray.append(Bufer)
   
	PrePublishers = Soup.find_all('div', {'class': 'media-section media-section_teams'})
	SmallSoup = BeautifulSoup(str(PrePublishers), "lxml")
	PrePublishers = SmallSoup.find_all('a', {'class': 'team-list-item team-list-item_xs'})
	Publishers = []
	if len(PrePublishers) == 0:
		PrePublishers = []
		Bufer = {}
		Bufer['id'] = 0
		Bufer['name'] = 'Неизвестный переводчик'
		Bufer['img'] = ''
		Bufer['dir'] = ''
		Bufer['tagline'] = ''
		Bufer['type'] = 'Переводчик'
		Publishers.append(Bufer)
	else:
		for InObj in PrePublishers:
			Publishers.append(GetPublisherData(InObj, Settings["domain"]))
	
	Branches = []
	Browser.get(Settings["domain"] + MangaName + "?section=chapters")
	BodyHTML = Browser.execute_script("return document.body.innerHTML;")
	Soup = BeautifulSoup(BodyHTML, "lxml")
	BranchesCount = Soup.find_all('div', {'class': 'team-list-item'})
	BranchIndex = 0
	for InObj in BranchesCount:
		BranchIndex += 1
		InBranch = {}
		InBranch['id'] = ""
		SmallSoup = BeautifulSoup(str(InObj), "lxml")
		InBranch['img'] = SmallSoup.find('div', {'class': 'team-list-item__cover'})['style'].split('(')[-1].split(')')[0]
		InBranch['img'] = Settings["domain"][:-1] + InBranch['img'].replace('"', '')
		PublisherInfo = {}
		PublisherInfo['id'] = 0
		PublisherInfo['name'] = RemoveSpaceSymbols(RemoveHTML(SmallSoup.find('span')))
		PublisherInfo['img'] = InBranch['img']
		PublisherInfo['dir'] = InBranch['img'].split('/')[-3]
		PublisherInfo['tagline'] = ""
		PublisherInfo['type'] = "Переводчик"
		InBranch['publishers'] = []
		InBranch['publishers'].append(PublisherInfo)
		InBranch['subscribed'] = False
		InBranch['total_votes'] = 0
		InBranch['count_chapters'] = 0
		Branches.append(InBranch)
	#Если нет веток перевода, то создать пустой шаблон.
	if len(Branches) == 0:
		InBranch = {}
		InBranch['id'] = GetCodeBID(MangaName, "")
		InBranch['img'] = ""
		InBranch['publishers'] = Publishers
		InBranch['subscribed'] = False
		InBranch['total_votes'] = 0
		InBranch['count_chapters'] = 0
		Branches.append(InBranch)

	IsLicensed = False
	if Soup.find_all('div', {'class': 'paper empty section'}) != []:
		IsLicensed = True
	
	IsVertical = False
	IsVerticalBufer = str(Soup.find('div', {'class': 'media-info-list paper'}))
	if "Вебтун" in IsVerticalBufer:
		IsVertical = True

	IsYaoi = False
	if "яой" in GenresArray:
		IsYaoi = True
	
	JSON = { 
		"id" : int(SiteWindowData["manga"]["id"]), 
		"img" : {
			"high": CoverURL,
			"mid": "",
			"low": ""
		}, 
		"en_name": MangaNameEN,
		"rus_name": MangaNameRU, 
		"another_name": AnotherName,
		"dir": MangaName,
		"description": Description,
		"issue_year": PublicationYear,
		"avg_rating": Rating,
		"admin_rating": "",
		"count_rating": Voted,
		"age_limit": AgeLimit,
		"status": {
			"id": 0,
			"name": Status
		},
		"count_bookmarks": 0,
		"total_votes": 0,
		"total_views": 0,
		"type": {
			"id": 0,
			"name": Type
		},
		"genres": GenresArray,
		"categories": TagsArray,
		"publishers": Publishers,
		"bookmark_type": None,
		"branches": Branches,
		"continue_reading": None,
		"is_licensed": IsLicensed,
		"newlate_id": None,
		"newlate_title": None,
		"related": None,
		"uploaded": 0,
		"can_post_comments": True,
		"adaptation": None,
		"isVertical": IsVertical,
		"isYaoi": IsYaoi,
		"content": {}
	}

	return JSON

#Возвращает структуру контента для помещения в JSON.
def MakeContentData(ChaptersNames, ChaptersLinks, BID, Browser, Settings, ShowProgress):
	ChaptersNames.reverse()
	ChaptersLinks.reverse()
	ContentDataBranch = []
	ChapterData = {
		"id": 0,
		"tome": 0,
		"chapter": "",
		"name": "",
		"score": 0,
		"rated": None,
		"viewed": None,
		"upload_date": "",
		"is_paid": False,
		"is_bought": None,
		"price": None,
		"pub_date": None,
		"publishers": [],
		"index": 1,
		"volume_id": None,
		"slides": []
		}
	IsBID = ""
	if BID == "":
		IsBID = "none"
	else:
		IsBID = BID.split('=')[-1]

	for i in range(0, len(ChaptersNames)):
		ChapterDataBufer = dict(ChapterData)
		ChapterNameData = ChaptersNames[i].split(' ')

		ChapterDataBufer["tome"] = ChapterNameData[1]
		ChapterDataBufer["chapter"] = ChapterNameData[3]
		if len(ChapterNameData) > 4:
			ChapterDataBufer["name"] = RemoveSpaceSymbols(ChaptersNames[i].split('-')[-1])
		else:
			ChapterDataBufer["name"] = ""
		ChapterDataBufer["index"] = i + 1
		PrintProgress(ShowProgress + "Branch ID: " + IsBID + ". Parcing chapters: ", str(i + 1), str(len(ChaptersLinks)))
		ChapterDataBufer["slides"] = GetMangaSlidesUrlArray(Browser, ChaptersLinks[i] + BID, Settings)
		ChapterDataBufer["id"] = GetChapterID(Browser, ChaptersLinks[i] + BID, Settings, False)
		ContentDataBranch.append(ChapterDataBufer)

	return ContentDataBranch

