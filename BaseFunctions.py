from random_user_agent.params import SoftwareName, OperatingSystem
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from random_user_agent.user_agent import UserAgent
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from PIL import ImageFile
from sys import platform
from time import sleep
from PIL import Image

import requests
import hashlib
import logging
import PIL
import re
import os

#==========================================================================================#
# >>>>> КЛАССЫ <<<<< #
#==========================================================================================#

# Вывод в консоль цветного текста.
class ColoredPrinter(object):
	
	# Конструктор.
	def __init__(self):
		# Базовые цвета.
		self.BLACK = "0"
		self.RED = "1"
		self.GREEN = "2"
		self.YELLOW = "3"
		self.BLUE = "4"
		self.PURPLE = "5"
		self.CYAN = "6"
		self.WHITE = "7"
		# Переключатель: возвращать ли стандартные настройки после каждого вывода.
		self.ResetStylesAfterPrint = True
		# Переключатель: переход на новую строку после вывода.
		self.NewLineAfterPrint = False

	# Вывод в консоль.
	def Print(self, Text: str(), TextColor: str(), BackgroundColor: str() = ""):
		# Если передан цвет для фота, то создать соответствующий модификатор.
		if BackgroundColor != "":
			BackgroundColor = "\033[4" + BackgroundColor + "m"
		# Генерация модификатора цвета текста.
		TextColor = "\033[3" + TextColor + "m"
		# Создание результирующей строки со стилями: цветового модификатора, модификатора фона, текста.
		StyledText = TextColor + BackgroundColor + Text
		# Если указано, добавить модификатор сброса стилей после вывода.
		if self.ResetStylesAfterPrint == True:
			StyledText = StyledText + "\033[0m"
		# Вывод в консоль и установка параметра перехода на норвую строку.
		if self.NewLineAfterPrint == True:
			print(StyledText, end = "")
		else:
			print(StyledText)

#==========================================================================================#
# >>>>> БАЗОВЫЕ ФУНКЦИИ <<<<< #
#==========================================================================================#

# Регулярное выражение фильтрации тегов HTML.
TagsHTML = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')

# Выключает ПК: работает на Windows и Linux.
def Shutdown():
	if platform == "linux" or platform == "linux2":
		os.system('sudo shutdown now')
	elif platform == "win32":
		os.system("shutdown /s")

# Удаляет теги HTML из строки.
def RemoveHTML(TextHTML):
  CleanText = re.sub(TagsHTML, '', str(TextHTML))

  return str(CleanText)

# Удаляет из строки символы: новой строки, табуляции, пробелы из начала и конца.
def RemoveSpaceSymbols(Text):
	Text = Text.replace('\n', '')
	Text = Text.replace('\t', '')
	Text = ' '.join(Text.split())

	return Text.strip()

# Заменяет символ новой строки на запятую с пробелом.
def ReplaceEndlToComma(Text):
	Text = Text.strip()
	Text = Text.replace('\n', ', ')

	return Text

# Преобразует литеральное число в int.
# Примечание: используется только для вычисления количества оценок.
def LiteralToInt(String):
	if String.isdigit():
		return int(String)
	else:
		Number = float(String[:-1]) * 1000
	return int(Number)

# Очищает консоль.
def Cls():
	os.system('cls' if os.name == 'nt' else 'clear')

# Выводит прогресс процесса.
def PrintProgress(String, Current, Total):
	Cls()
	print(String, " ", Current, " / ", Total)

# Удаляет запросы из URL.
def RemoveArgumentsFromURL(URL):
	return str(URL).split('?')[0]

# Усекает число до определённого количества знаков после запятой.
def ToFixedFloat(FloatNumber, Digits = 0):
	return float(f"{FloatNumber:.{Digits}f}")

# Проевращает число секунд в строку-дескриптор времени по формату [<x> hours <y> minuts <z> seconds].
def SecondsToTimeString(Seconds):
	# Количество часов.
	Hours = int(Seconds / 3600.0)
	Seconds -= Hours * 3600
	# Количество минут.
	Minutes = int(Seconds / 60.0)
	Seconds -= Minutes * 60
	# Количество секунд.
	Seconds = ToFixedFloat(Seconds, 2)
	# Строка-дескриптор времени.
	TimeString = ""

	# Генерация строки.
	if Hours > 0:
		TimeString += str(Hours) + " hours "
	if Minutes > 0:
		TimeString += str(Minutes) + " minutes "
	if Seconds > 0:
		TimeString += str(Seconds) + " seconds"

	return TimeString

# Возвращает случайное значение заголовка User-Agent.
def GetRandomUserAgent():
	SoftwareNames = [SoftwareName.CHROME.value]
	OperatingSystems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]   
	UserAgentRotator = UserAgent(software_names = SoftwareNames, operating_systems = OperatingSystems, limit = 100)

	return str(UserAgentRotator.get_random_user_agent()).strip('"')

# Удаляет повторы значений из словаря.
def RemoveDuplicatesFromDict(Dictionary: dict()):
	return {v:k for k,v in {Dictionary[k]:k for k in reversed(list(Dictionary))}.items()}

# Инвертирует порядок элементов словаря.
def ReverseDict(Dictionary: dict()):
	# Список ключей.
	Keys = list(Dictionary.keys())
	# Инвертирование списка ключей.
	Keys.reverse()
	# Инвертированный словарь.
	ReversedDict = dict()

	# Запись значений в обратном порядке.
	for InObj in Keys:
		ReversedDict[InObj] = Dictionary[InObj]

	return ReversedDict

#==========================================================================================#
# >>>>> ПАРСИНГ ТАЙТЛА <<<<< #
#==========================================================================================#

# Проверяет ветвь на пустоту.
def CheckBranchOnSiteForEmpty(Browser, Settings, MangaName, True_BranchID):
	# Перейти на страницу ветви перевода.
	if True_BranchID != "":
		Browser.get(Settings["domain"] + MangaName + "?bid=" + True_BranchID + "&section=chapters")
	else:
		Browser.get(Settings["domain"] + MangaName + "?section=chapters")

	# HTML-код страницы после полной загрузки.
	BodyHTML = Browser.execute_script("return document.body.innerHTML;")
	# Парсинг HTML-кода страницы.
	Soup = BeautifulSoup(BodyHTML, "lxml")
	# Поиск блока с уведомлением о пустоте ветви.
	SmallSoup = str(Soup.find("div", {"class": "empty"}))

	# Проверить наличие сообщения о пустоте ветви.
	if "Здесь пока нет глав" in SmallSoup:
		return True
	else:
		return False

# Выполнение, если указано настройками, входа на сайт и отключение уведомления о возрастном ограничении.
def SignInAndDisableWarning(Browser, Settings):
	# Если включён вход на сайт.
	if Settings["sign-in"] == True:
		# Проверка присутствия логина и пароля.
		if Settings["email"] != "" and Settings["password"] != "":
			# Вход на сайт.
			LogIn(Browser, Settings)
			# Запись в лог сообщения об успешном входе.
			logging.info("Sign in as \"" + Settings["email"] + "\".")
		else:
			# Вывод в лог ошибки: некорректные данные пользователя.
			logging.error("Uncorrect user data! Check \"Settings.json\".")

	# Если включено отключение уведомления о возрастном ограничении.
	if Settings["disable-age-limit-warning"] == True:
		# Отключить уведомление.
		DisableAgeLimitWarning(Browser, Settings)
		# Запись в лог сообщения об отключении уведомления.
		logging.info("Age limit warning disabled.")

#Возвращает результат проверки тайтла на платность.
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

# Получает ID главы на сайте. 
# Примечание: вызывать после перехода на страницу главы.
def GetChapterID(Browser):
	# Информация о странице из JS-данных сайта.
	SiteWindowData = Browser.execute_script("return window.__info;")

	return SiteWindowData["current"]["id"]

# Возвращает уникальный BranchID на основе названия манги.
def GetSynt_BranchID(MangaName, True_BranchID):
	# Вычисление MD5 хеш-суммы.
	MangaIntName = hashlib.md5(MangaName.encode())
	# Получение шестнадцатиричного представления хеш-суммы.
	MangaIntName = MangaIntName.hexdigest()
	# Преобразование хеш-суммы в десятичное строковое представление.
	MangaIntName = str(int(MangaIntName, 16))
	
	return str(MangaIntName) + True_BranchID

# Вход на сайт.
def LogIn(Browser, Settings):
	# Переход на главную страницу.
	Browser.get(Settings["domain"][:-1])
	# Ожидание появления кнопки входа.
	WebDriverWait(Browser, 60).until(EC.visibility_of_element_located((By.CLASS_NAME, "header__sign-in")))
	# Клик по кнопке входа.
	Browser.find_element(By.CLASS_NAME, "header__sign-in").click()

	# Поиск поля ввода логина.
	EmailInput = Browser.find_element(By.CSS_SELECTOR , "input[name=\"email\"]")
	# Ввод логина.
	PasswordInput = Browser.find_element(By.CSS_SELECTOR , "input[name=\"password\"]")

	# Поиск поля ввода пароля.
	EmailInput.send_keys(Settings["email"])
	# Ввод пароля.
	PasswordInput.send_keys(Settings["password"])

	# Клик по кнопке входа.
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

# Отключает уведомление о возрастном ограничении.
def DisableAgeLimitWarning(Browser, Settings):
	# Переключение между способами отключения уведомления в зависимости от домена.
	if Settings["domain"] == "https://mangalib.me/":
		Browser.get("https://mangalib.me/kimetsu-no-yaiba/v1/c1?page=1")

	elif Settings["domain"] == "https://hentailib.me/": 
		# Поиск последней добавленной на сайт главы и переход к ней кликом по ссылке.
		Browser.find_elements(By.CLASS_NAME, "updates__chapter")[1].click()

	elif Settings["domain"] == "https://yaoilib.me/": 
		Browser.get("https://yaoilib.me/you-are-here/v1/c151?page=1")
	
	# Поиск и нажатие на кнопку сокрытия уведомления.
	Browser.find_elements(By.CLASS_NAME, "control__text")[-1].click()
	Browser.find_element(By.CLASS_NAME, 'reader-caution-continue').click()

# Получает истинные ID ветвей переводов.
def GetBranchesID(Browser, MangaName, Settings):
	# Переход на страницу с информацией о тайтле.
	Browser.get(Settings["domain"] + MangaName + "?section=chapters")
	# Поиск всех кнопок смены переводчика.
	TranslatorsButtons = Browser.find_elements(By.CLASS_NAME, "team-list-item")
	# Список истинных ID ветвей перевода.
	BranchesID = []

	# Кликать по каждой кнопке и записывать истинный ID из адресной строки браузера. 
	for InObj in TranslatorsButtons:
		# Проверка кнопки на доступность.
		if InObj.is_displayed() and InObj.is_enabled():
			InObj.click()
			BranchesID.append(str(Browser.current_url).split('?')[-1].split('&')[0].split('=')[1])

	return BranchesID

# Открывает навигационную панель для получения названий глав и ссылок на главы.
def PrepareToParcingChapters(Browser, Settings, MangaName, True_BranchID):
	# Проверка на существование истинного ID ветви (в случае, если в тайтле только одна ветвь перевода) и переход к нужной странице.
	if True_BranchID is None:
		Browser.get(Settings["domain"] + MangaName + "?section=chapters")
	else:
		Browser.get(Settings["domain"] + MangaName + "?bid=" + str(True_BranchID) + "&section=chapters")

	# Ожидание загрузки блока с ссылкой на самую свежую главу в ветви перевода.
	WebDriverWait(Browser, 60).until(EC.visibility_of_element_located((By.CLASS_NAME, "media-chapter__name")))

	# HTML-код страницы после полной загрузки.
	BodyHTML = Browser.execute_script("return document.body.innerHTML;")
	# Парсинг HTML-кода страницы.
	Soup = BeautifulSoup(BodyHTML, "lxml")
	# Поиск блока самой свежей главы.
	LastChapter = Soup.find_all("div", {"class": "media-chapter__name text-truncate"})[0]
	# Парсинг блока самой свежей главы.
	Soup = BeautifulSoup(str(LastChapter), "lxml")
	# Поиск ссылки на самую свежую главу.
	LastChapter = Soup.find("a")

	# Переход к самой свежей главе главе.
	Browser.get(Settings["domain"][:-1] + LastChapter["href"])
	# Поиск кнопки для открытия блока с главами.
	ChaptersSpoilerButton = Browser.find_elements(By.CLASS_NAME, "reader-header-action__text")

	# Проверка доступности кнопки и её нажатие.
	if len(ChaptersSpoilerButton) >= 2:
		if ChaptersSpoilerButton[1].is_displayed():
			ChaptersSpoilerButton[1].click()
	
# Получает список названий глав.
# Примечание: предварительно вызвать PrepareToParcingChapters.
def GetChaptersNames(Browser):
	# HTML-код страницы после полной загрузки.
	BodyHTML = Browser.execute_script("return document.body.innerHTML;")
	# Парсинг HTML-кода страницы.
	Soup = BeautifulSoup(BodyHTML, "lxml")
	# Поиск всех блоков с названиями глав.
	ChaptersNames = Soup.find_all("a", {"class": "menu__item"})

	# Для каждого блока главы удалить HTML-теги и пробелы.
	for i in range(0, len(ChaptersNames)):
		ChaptersNames[i] = RemoveSpaceSymbols(RemoveHTML(ChaptersNames[i]))

	return ChaptersNames

# Получает список ссылок на главы. 
# Примечание: предварительно вызвать PrepareToParcingChapters.
def GetChaptersLinks(Browser):
	# HTML-код страницы после полной загрузки.
	BodyHTML = Browser.execute_script("return document.body.innerHTML;")
	# Парсинг HTML-кода страницы.
	Soup = BeautifulSoup(BodyHTML, "lxml")
	# Поиск модальных блоков, среди которого есть блок с главами.
	SmallSoup = Soup.find_all("div", {"class": "modal__body"})
	# Парсинг блока с главами.
	SmallSoup = BeautifulSoup(str(SmallSoup[-1]), "lxml")
	# Поиск HTML-ссылок на главы внутри блока.
	ChaptersLinks = SmallSoup.find_all("a", {"class": "menu__item"})

	# Для кажой ссылки оставить только источник.
	for i in range(0, len(ChaptersLinks)):
		ChaptersLinks[i] = RemoveSpaceSymbols(RemoveHTML(ChaptersLinks[i]["href"])).split('?')[0]
	
	return ChaptersLinks

# Получает список слайдов главы из JS-данных страницы и определяет их размеры в пикселях.
def GetMangaSlidesUrlList(Browser, Settings, ChapterLink, Logging = True):
	# Переход на страницу главы.
	Browser.get(Settings["domain"][:-1] + ChapterLink)
	# Ожидание загрузки JS данных о главе.
	WebDriverWait(Browser, 60).until(EC.presence_of_element_located, (By.ID , "pg"))
	# Получение JS инофрмации о странице.
	SiteWindowInfo = Browser.execute_script("return window.__info;")
	# Получение JS данных о главе.
	SiteWindowPg = Browser.execute_script("return window.__pg;")
	# Получение ссылки на сервер-хранилище.
	StorageLink = SiteWindowInfo["servers"][Settings["server"]]
	# Получение алиаса главы на сервере-хранилище.
	ChapterSlug = SiteWindowInfo["img"]["url"]
	# Разрешить чтение усечённых файлов.
	ImageFile.LOAD_TRUNCATED_IMAGES = True
	# Формирование заголовков запроса.
	RequestHeaders = {}
	RequestHeaders["referer"] = Settings["domain"]
	RequestHeaders["user-agent"] = GetRandomUserAgent()
	# Запись в лог используемого для главы User-Agent.
	logging.debug("User-Agent for request: " + RequestHeaders["user-agent"])
	# Список URL слайдов.
	SlidesLinks = []

	#Формирование для каждого слайда полной ссылки на сервер-хранилище.
	for i in range(0, len(SiteWindowPg)):
		SlidesLinks.append(StorageLink + "/" + ChapterSlug + SiteWindowPg[i]["u"])

	# Ширина слайдов.
	SlidesSizesW = []
	# Высота слайдов.
	SlidesSizesH = []
	# Количество неполученных слайдов.
	SlidesErrors = 0

	# Подгрузка слайдов и определение их размеров, если указано в настройках.
	if Settings["getting-slide-sizes"] == True:
		for i in range(0, len(SlidesLinks)):
			# Ширина текущего слайда.
			SlideW = None
			# Высота текущего слайда.
			SlideH = None
			# Проверка успешности запроса на получение слайда.
			Request = requests.get(SlidesLinks[i], headers = RequestHeaders, stream = True)
			# Обработка статуса запроса.
			if Request.status_code == 200: 

				# Попытка обработать слайд для получения размеров.
				try:
					# Открытие слайда из потока запроса.
					with Image.open(Request.raw) as Slide:
						# Запись размеров слайда.
						SlideW = Slide.width
						SlideH = Slide.height

				except PIL.UnidentifiedImageError:
					# Запись в лог ошибки распознания слайда.
					if Logging == True:
						logging.warning("Chapter: \"" + ChapterLink + "\" parcing. Unable to recognize image \"" + SlidesLinks[i] + "\".")

				except OSError:
					# Запись в лог ошибки: усечённый файл.
					if Logging == True:
						logging.warning("Chapter: \"" + ChapterLink + "\" parcing. Truncated image \"" + SlidesLinks[i] + "\".")

			else:
				# Инкремент количества неполученных слайдов.
				SlidesErrors += 1
				# Запись в лог ошибки получения слайда с сервера.
				logging.warning("Chapter: \"" + ChapterLink + "\" parcing. Failed to request \"" + SlidesLinks[i] + "\".")

			# Помещение размеров слайда в контейнеры.
			SlidesSizesW.append(SlideW)
			SlidesSizesH.append(SlideH)

			# Интервал запроса слайдов.
			sleep(Settings["delay"])

	else:
		# Заполнение размеров слайдов неопределёнными значениями.
		for i in range(0, len(SlidesLinks)):
			SlidesSizesW.append(None)
			SlidesSizesH.append(None)

		# Интервал перехода между главами.
		sleep(Settings["delay"])

	# Структура главы.
	ChapterData = []
	
	# Формирование структуры главы для записи в JSON.
	for i in range(len(SlidesLinks)):
		FrameData = dict()
		FrameData["link"] = SlidesLinks[i]
		FrameData["width"] = SlidesSizesW[i]
		FrameData["height"] = SlidesSizesH[i]
		ChapterData.append(FrameData)

	# Запись в лог результата выполнения и обработка неполного получения данных о слайдах.
	if SlidesErrors == 0 and Logging == True:
		logging.info("Chapter: \"" + ChapterLink + "\" parced. Slides count: " + str(len(ChapterData)) + ".")
	elif Logging == True:
		logging.warning("Chapter: \"" + ChapterLink + "\" parced with errors. Not all slides were received correctly : " + str(len(ChapterData) - SlidesErrors) + " / " + str(len(ChapterData)) + ".")

	return ChapterData

# Получение статуса тайтла.
def GetMangaData_Status(Browser, Settings, MangaName):
	# Переход на страницу с описанием тайтла, если таковой ещё не выполнен.
	if RemoveArgumentsFromURL(Browser.current_url) != Settings["domain"] + MangaName or "?section=info" not in Browser.current_url:
		Browser.get(Settings["domain"] + MangaName + "?section=info")
	# HTML-код страницы после полной загрузки.
	BodyHTML = Browser.execute_script("return document.body.innerHTML;")
	# Парсинг HTML-кода страницы.
	Soup = BeautifulSoup(BodyHTML, "lxml")
	# Поиск блоков с данными о тайтле.
	DescriptionBlocks = Soup.find_all("a", {"class": "media-info-list__item"})
	# Статус произведения.
	Status = "Неизвестен"
	# Структура статуса для помещения в JSON.
	StatusStruct = {}

	# В каждом блоке данных о тайтле искать статус.
	for InObj in DescriptionBlocks:
		if "Статус перевода" in str(InObj):
			Status = RemoveHTML(InObj).replace('\n', ' ').split()[2]

	# Запись статуса.
	StatusStruct["id"] = 0
	StatusStruct["name"] = Status

	return StatusStruct

# Получение серий тайтла.
def GetMangaData_Series(Browser, Settings, MangaName):
	# Переход на страницу с описанием тайтла, если таковой ещё не выполнен.
	if RemoveArgumentsFromURL(Browser.current_url) != Settings["domain"] + MangaName or "?section=info" not in Browser.current_url:
		Browser.get(Settings["domain"] + MangaName + "?section=info")
	# HTML-код страницы после полной загрузки.
	BodyHTML = Browser.execute_script("return document.body.innerHTML;")
	# Парсинг HTML-кода страницы.
	Soup = BeautifulSoup(BodyHTML, "lxml")
	# Поиск блоков с данными о тайтле.
	DescriptionBlocks = Soup.find_all("div", {"class": "media-info-list__item"})
	# Ссылки на серии.
	SeriesLinks = []
	# Названия серий.
	SeriesNames = []
	# Алиасы серий.
	SeriesSlugs = []
	# Структура контейнера ссылок для помещения в JSON.
	SeriesContainer = []

	# В каждом блоке данных о тайтле искать серии.
	for InObj in DescriptionBlocks:
		if "Серия" in str(InObj):
			# Парсинг блока с сериями.
			SmallSoup = BeautifulSoup(str(InObj), "lxml")
			# Поиск всех ссылок.
			SeriesLinks = SmallSoup.find_all("a")

	# Для каждой ссылки сформировать найти название и алиас.
	for InObj in SeriesLinks:
		SeriesNames.append(RemoveHTML(InObj))
		SeriesSlugs.append(InObj["href"].split('/')[-1])

	# Заполнение контейнера.
	for i in range(0, len(SeriesLinks)):
		BuferStruct = {}
		BuferStruct["name"] = SeriesNames[i]
		BuferStruct["slug"] = SeriesSlugs[i]

		SeriesContainer.append(BuferStruct)

	return SeriesContainer

# Получение данных о манге и их сохранение в JSON.
def GetMangaData(Browser, Settings, MangaName):
	# Переход на страницу тайтла с информацией.
	Browser.get(Settings["domain"] + MangaName + "?section=info")
	# HTML-код страницы после полной загрузки.
	BodyHTML = Browser.execute_script("return document.body.innerHTML;")
	# Парсинг HTML-кода страницы.
	Soup = BeautifulSoup(BodyHTML, "lxml")
	# Получение JS инофрмации о тайтле.
	SiteWindowData = Browser.execute_script("return window.__DATA__;")

	# ---> Перечень стандартных значений.
	# ================================================== #
	# URL обложки.
	CoverURL = ""
	# Русское название тайтла.
	TitleName_RU = ""
	# Английское название тайтла (ромадзи, транслитерация).
	TitleName_EN = ""
	# Альтернативные названия (через ", ").
	AlternativeNames = ""
	# Описание тайтла.
	Description = ""
	# Год релиза тайтла.
	PublicationYear = None
	# Рейтинг.
	Rating = "0"
	# Количество проголосовавших.
	VotedCount = 0
	# Возрастное ограничение.
	AgeLimit = 0
	# Статус перевода.
	Status = "Неизвестен"
	# Тип тайтла.
	Type = ""
	# ================================================== #

	# Поиск блока обложки.
	CoverBlock = Soup.find("div", {"class": "media-sidebar__cover paper"})
	# Парсинг блока обложки.
	SmallSoup = BeautifulSoup(str(CoverBlock), "lxml")
	# Получение URL обложки.
	CoverURL = SmallSoup.find("img")["src"]
   
	# Получение русского названия тайтла.
	TitleName_RU = Soup.find("div", {"class": "media-name__main"}).get_text()
	
	# Поиск блока английского названия тайтла.
	TitleNameBlock_EN = Soup.find("div", {"class": "media-name__alt"})
	# Если такой блок найден, то получить название.
	if TitleNameBlock_EN != None:
		TitleName_EN = TitleNameBlock_EN.get_text()

	# ---> Получение данных из медиа-информационных блоков.
	# ================================================== #
	# Поиск медиа-информационных блоков.
	MediaInfoItems = Soup.find_all(["div", "a"], {"class": "media-info-list__item"})

	# Проверка каждого блока.
	for Item in MediaInfoItems:

		# Обработка: тип тайтла.
		if "Тип" in str(Item):
			Type = RemoveHTML(Item).replace("\n", " ").split()[-1]

		# Обработка: год релиза.
		if "Год релиза" in str(Item):
			PublicationYear = int(RemoveHTML(Item).replace("\n", " ").split()[-1])

		# Обработка: статус перевода.
		if "Статус перевода" in str(Item):
			Status = RemoveHTML(Item).replace("\n", " ").split()[-1]

		# Обработка: возрастное ограничение.
		if "Возрастной рейтинг" in str(Item):
			AgeLimit = int(RemoveHTML(Item).replace("\n", " ").split()[-1].replace("+", ""))

		# Обработка: альтернативные названия.
		if "Альтернативные названия" in str(Item):
			# Удаление из блока альтернативных названий ненужных строк.
			AlternativeNames = RemoveHTML(str(Item).replace("Альтернативные названия", "").replace("показать все", ""))
			# Форматирование альтернативных названий разделителем.
			AlternativeNames = AlternativeNames.replace("\n\n\n", "").replace("\n", ", ")

	# ================================================== #

	# Поиск блока описания тайтла.
	TitleDescriptionBlock = Soup.find("div", {"class": "media-description__text"})
	# Если такой блок найден, то получить описание.
	if TitleDescriptionBlock != None:
		Description = RemoveHTML(TitleDescriptionBlock.get_text()).strip("\n \t")
	
	# Получение блока рейтинга.
	RatingBlock = Soup.find("div", {"class": "media-rating__value"})
	# Получение рейтинга.
	Rating = RatingBlock.get_text()
	
	# Поиск блока количества голосов.
	VotedBlock = Soup.find("div", {"class": "media-rating__votes"})
	# Получение приближённого количества голосов.
	VotedCount = LiteralToInt(VotedBlock.get_text())
	
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

	Series = GetMangaData_Series(Browser, Settings, MangaName)
   
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
		InBranch['id'] = GetSynt_BranchID(MangaName, "")
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
	for InObj in GenresArray:
		IsYaoiTemplate = {}
		IsYaoiTemplate['id'] = 0
		IsYaoiTemplate['name'] = "яой"
		if IsYaoiTemplate in GenresArray:
			IsYaoi = True
	
	# Структура файла JSON, описывающего тайтл.
	JSON = { 
		"id" : int(SiteWindowData["manga"]["id"]), 
		"img" : {
			"high": CoverURL,
			"mid": "",
			"low": ""
		}, 
		"en_name": TitleName_EN,
		"rus_name": TitleName_RU, 
		"another_name": AlternativeNames,
		"dir": MangaName,
		"description": Description,
		"issue_year": PublicationYear,
		"avg_rating": Rating,
		"admin_rating": "",
		"count_rating": VotedCount,
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
		"series": Series,
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

# Формирует структуру контента для помещения в JSON.
def MakeContentData(Browser, Settings, ShowProgress, ChaptersNames, ChaptersLinks, True_BranchID):
	# Реверс порядка названий глав и ссылок на главы.
	ChaptersNames.reverse()
	ChaptersLinks.reverse()
	# Контейнер ветви контента.
	ContentDataBranch = []
	# Строка запроса нужной ветви перевода.
	QueryBranch = ""
	# Структура главы.
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
		"index": 0,
		"volume_id": None,
		"slides": []
		}

	# Если не передан истинный BranchID, то заполнить его сообщением, иначе сформировать строку запроса.
	if True_BranchID == "":
		True_BranchID = "none"
	else:
		QueryBranch = "?bid=" + True_BranchID

	# Для каждой главы сформировать структуру, заполнить её данными и поместить в контейнер.
	for i in range(0, len(ChaptersNames)):
		# Буфернная структура главы.
		ChapterDataBufer = dict(ChapterData)
		# Полное название главы с сайта, разбитое по пробелам.
		ChapterNameData = ChaptersNames[i].split(' ')

		# Вывести прогресс процесса.
		PrintProgress(ShowProgress + "Branch ID: " + True_BranchID + ". Parcing chapters: ", str(i + 1), str(len(ChaptersLinks)))

		# Получение информации о слайдах.
		ChapterDataBufer["slides"] = GetMangaSlidesUrlList(Browser, Settings, ChaptersLinks[i] + QueryBranch)
		
		# Номер тома (целочисленный тип данных).
		ChapterDataBufer["tome"] = int(ChapterNameData[1])
		# Номер главы (строковый тип данных).
		ChapterDataBufer["chapter"] = ChapterNameData[3]
		# Название главы: если есть, то записать его, иначе оставить поле пустым.
		if len(ChapterNameData) > 4:
			ChapterDataBufer["name"] = RemoveSpaceSymbols(ChaptersNames[i].replace(ChaptersNames[i].split('-')[0], ""))
		else:
			ChapterDataBufer["name"] = ""
		# Индекс главы.
		ChapterDataBufer["index"] = i + 1
		# ID главы на сайте.
		ChapterDataBufer["id"] = GetChapterID(Browser)

		# Помещение буферной структуры в контейнер.
		ContentDataBranch.append(ChapterDataBufer)

	return ContentDataBranch

#==========================================================================================#
# >>>>> ОБНОВЛЕНИЕ ТАЙТЛА <<<<< #
#==========================================================================================#

# Получение из JSON тайтла списка синтетических ID ветвей.
def GetBranchesIdFromJSON(TitleJSON):
	# Список синтетических ID ветвей переводов.
	ListID = []

	# Для каждой ветви записать её синтетический ID.
	for i in range(0, len(TitleJSON["branches"])):
		ListID.append(TitleJSON["branches"][i]["id"])

	return ListID

# Построение списка ссылок на главы на основе ветви перевода из JSON.
def BuildLinksFromJSON(TitleJSON, Synt_BranchID, MangaName, Settings):
	# Список ссылок на главы.
	ChaptersLinks = []
	# Данные из ветви перевода внутри JSON.
	ChaptersFromJSON = TitleJSON["content"][Synt_BranchID]

	# Для каждой главы построить ссылку.
	for InObj in ChaptersFromJSON:
		ChaptersLinks.append(Settings["domain"] + MangaName + "/v" + str(InObj["tome"]) + "/c" + InObj["chapter"])

	return ChaptersLinks

# Возвращает номера тома и главы, разделённые пробелом, основываясь на URL.
def GetVolumeAndChapterFromURL(ChapterURL):
	# Номер тома.
	Volume = ChapterURL.split('?')[0].split('/')	
	# Номер главы.
	Chapter = ChapterURL.split('?')[0].split('/')

	# Проверка на корректность URL и получение номера тома.
	if len(Volume) > 3:
		Volume = Volume[-2].replace('v', '')
	else:
		Volume = ""

	# Проверка на корректность URL и получение номера главы.
	if len(Chapter) > 3:
		Chapter = Chapter[-1].replace('c', '')
	else:
		Chapter = ""

	return Volume + " " + Chapter

# Парсинг одной главы.
def ParceChapter(Browser, Settings, ChapterFullLink, True_BranchID):
	# Удаление аргументов из URL.
	ChapterFullLink = RemoveArgumentsFromURL(ChapterFullLink)
	# Переход на страницу главы.
	Browser.get(ChapterFullLink)
	# Информация о странице из JS-данных сайта.
	SiteWindowInfo = Browser.execute_script("return window.__info;")
	# Информация о всех главах из JS-данных сайта.
	SiteWindowChaptersData = Browser.execute_script("return window.__DATA__;")
	SiteWindowChaptersData = SiteWindowChaptersData["chapters"]
	SiteWindowChaptersData.reverse()
	# Структура главы для помещения в JSON.
	ChapterStruct = {
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
		"index": 0,
		"volume_id": None,
		"slides": []
	}

	# Если есть истинный ID ветви перевода, то для удобства добавить к нему определение.
	if True_BranchID != "":
		True_BranchID = "?bid=" + True_BranchID

	# Получение ID.
	ChapterStruct["id"] = SiteWindowInfo["current"]["id"]
	# Получение номера тома.
	ChapterStruct["tome"] = SiteWindowInfo["current"]["volume"]
	# Получение номера главы.
	ChapterStruct["chapter"] = SiteWindowInfo["current"]["number"]
	# Получение названия.
	ChapterStruct["name"] = SiteWindowChaptersData[SiteWindowInfo["current"]["index"] - 1]["chapter_name"]

	# Получение информации о слайдах.
	ChapterStruct["slides"] = GetMangaSlidesUrlList(Browser, Settings, ChapterFullLink.replace(Settings["domain"][:-1], "") + True_BranchID)

	return ChapterStruct
	
# Преобразует синтетический BranchID в истинный.
def SyntToTrueBranchID(Synt_BranchID, MangaName):
	# Десятичное представление MD5 хеш-суммы алиаса манги.
	PartMD5 = GetSynt_BranchID(MangaName, "")
	# Удаление из синтетического BranchID генерируемой части.
	True_BranchID = Synt_BranchID.replace(PartMD5, "")

	return True_BranchID

# Преобразует истинный BranchID в синтетический.
def TrueToSyntBranchID(True_BranchID, MangaName):
	# Десятичное представление MD5 хеш-суммы алиаса манги.
	PartMD5 = GetSynt_BranchID(MangaName, "")
	# Синтетический BranchID.
	Synt_BranchID = PartMD5 + True_BranchID

	return Synt_BranchID

# Получает структуру описания ветвей переводов для помещения в JSON.
def GetBranchesDescriptionStruct(Browser, Settings, MangaName, True_BranchesID):
	# Переход на страницу с главами тайтла.
	Browser.get(Settings["domain"] + MangaName + "?section=chapters")
	# Получение HTML-кода страницы.
	BodyHTML = Browser.execute_script("return document.body.innerHTML;")
	# Парсинг исходного кода страницы.
	Soup = BeautifulSoup(BodyHTML, "lxml")
	# Блоки с ветвями.
	BranchesHTML = Soup.find_all("div", {"class": "team-list-item"})
	# Структура ветвей переводов.
	BranchesStruct = []
	# Индекс ветви.
	BranchIndex = 0
	
	# Для каждого блока ветви сформировать структуру.
	for i in range(0, len(BranchesHTML)):
		# Инкремент индекса ветви.
		BranchIndex += 1
		# Буферное значение для формирования структуры.
		BuferBranch = {}
		# Парсинг блока ветви.
		SmallSoup = BeautifulSoup(str(BranchesHTML[i]), "lxml")
		# Информация о переводчике.
		PublisherInfo = {}

		# Присвоение синтетического BranchID.
		BuferBranch["id"] = TrueToSyntBranchID(True_BranchesID[i], MangaName)
		# Аватар переводчика.
		BuferBranch["img"] = Settings["domain"][:-1] + SmallSoup.find('div', {"class": "team-list-item__cover"})["style"].split('(')[-1].split(')')[0].replace('"', '')
		# Создание контейнера для переводчиков.
		BuferBranch["publishers"] = []
		# Есть ли подписка (не определяется).
		BuferBranch["subscribed"] = False
		# Количество голосов (не определяется).
		BuferBranch["total_votes"] = 0
		# Количество глав (не определяется).
		BuferBranch["count_chapters"] = 0

		# ID переводчика (не определяется).
		PublisherInfo["id"] = 0
		# Название переводчика.
		PublisherInfo["name"] = RemoveSpaceSymbols(RemoveHTML(SmallSoup.find("span")))
		# Копирование ссылки на аватар переводчика.
		PublisherInfo["img"] = BuferBranch["img"]
		# Директория переводчика на сервере.
		PublisherInfo["dir"] = BuferBranch["img"].split('/')[-3]
		# Слоган переводчика (не определяется.)
		PublisherInfo["tagline"] = ""
		# Тип.
		PublisherInfo["type"] = "Переводчик"
		# Добавление переводчика.
		BuferBranch["publishers"].append(PublisherInfo)

		# Помещение буферной структуры в основной контейнер.
		BranchesStruct.append(BuferBranch)

	return BranchesStruct

#==========================================================================================#
# >>>>> ИСПРАВЛЕНИЕ ТАЙТЛА <<<<< #
#==========================================================================================#

# Возвращает количество слайдов без определённго разрешения.
def CheckChapterForNoneSlideSizes(Chapter):
	# Список слайдов.
	Slides = Chapter["slides"]
	# Количество слайдов без размеров.
	NoneSizesSlidesCount = 0

	# Для каждого слайда проверить наличие размеров.
	for i in range(0, len(Slides)):
		if Slides[i]["width"] == None or Slides[i]["height"] == None:
			NoneSizesSlidesCount += 1

	return NoneSizesSlidesCount

# Получение списка серверов с контентом.
def GetContentServersList(Browser, Settings):
	# Переход на главную страницу.
	Browser.get(Settings["domain"][:-1])
	# Ожидание появления ссылок на обновлённые главы.
	WebDriverWait(Browser, 60).until(EC.visibility_of_element_located((By.CLASS_NAME, "updates__chapter")))
	# Поиск последней добавленной на сайт главы и переход к ней кликом по ссылке.
	Browser.find_elements(By.CLASS_NAME, "updates__chapter")[0].click()
	# Получение JS инофрмации о странице.
	SiteWindowInfo = Browser.execute_script("return window.__info;")
	# Список словарей.
	ServersList = RemoveDuplicatesFromDict(ReverseDict(SiteWindowInfo["servers"]))

	return ServersList

# Строит алиас главы из описания.
# Примечание: передать структуру главы из описания в JSON тайтла.
def BuildChapterSlug(MangaName, Chapter):
	return "/" + MangaName + "/v" + str(Chapter["tome"]) + "/c" + Chapter["chapter"]

# Попытка дополнить информацию о слайдах.
def AmendChapterSlides(Browser, Settings, Servers, TitleJSON, Chapter):
	# Инвертированные названия серверов для порядка от нового к старому.
	ServersNames = list(Servers.keys())
	# Попытаться поставить в списке на исправление первым сервер, указанный в настройках.
	if Settings["server"] in ServersNames:
		ServersNames.remove(Settings["server"])
		ServersNames.insert(0, Settings["server"])
	# Ссылка на главу.
	ChapterLink = BuildChapterSlug(TitleJSON["dir"], Chapter)
	# Временное хранилище главы.
	ChapterBufer = dict(Chapter)
	# Копирование структуры настроек.
	FakeSettings = Settings
	# Количество слайдов без определённого разрешения в главе.
	NoneSizesSlidesCount = CheckChapterForNoneSlideSizes(Chapter)

	# Получать слайды с сервера, пока не исчезнет ошибка.
	for i in range(0, len(ServersNames)):
		# Вывод сообщения в консоль о дополнении конкретного тайтла.
		print("Trying to amend \"" + ChapterLink +  "\" with server: " + ServersNames[i])
		# Запись нового сервера в имитацию настроек.
		FakeSettings["server"] = ServersNames[i]
		# Запись переключателя, включающего получение слайдов манги.
		FakeSettings["getting-slide-sizes"] = True
		# Запись в лог сообщения о нахождении неполного описания главы.
		logging.info("Amending: \"" + ChapterLink + "\" with server \"" + ServersNames[i] + "\". Trying...")
		# Получение информации о слайдах главы с заданного сервера.
		ChapterBufer["slides"] = GetMangaSlidesUrlList(Browser, FakeSettings, ChapterLink, Logging = False)
		# Количество слайдов без определённого разрешения в главе, полученной с сервера исправления.
		AmendedNoneSizesSlidesCount = CheckChapterForNoneSlideSizes(ChapterBufer)

		# Если описание слайдов в порядке, то сохранить и вернуть его.
		if AmendedNoneSizesSlidesCount == 0:
			# Запись в лог сообщения о дополнении главы размерами слайдов.
			logging.info("Amending: \"" + ChapterLink + "\" successfully amended with server \"" + ServersNames[i] + "\".")
			# Вывод сообщения в консоль о дополнении конкретного тайтла.
			print("Chapter \"" + ChapterLink +  "\" amended successfully!")

			return ChapterBufer

		# Иначе сохранить вариант с меньшим количеством ошибок.
		elif AmendedNoneSizesSlidesCount < NoneSizesSlidesCount:
			Chapter = ChapterBufer


	# Запись в лог сообщения о невозможности дополнить главу размерами слайдов.
	logging.warning("Amending: \"" + ChapterLink + "\". Failed to amend chapter.")
	# Вывод сообщения в консоль о неудачном дополнении конкретного тайтла.
	print("Chapter \"" + ChapterLink +  "\" couldn't amended.")

	return Chapter