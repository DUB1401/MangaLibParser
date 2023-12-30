from dublib.Methods import Cls, CheckPythonMinimalVersion, MakeRootDirectories, ReadJSON, Shutdown
from dublib.Terminalyzer import ArgumentType, Command, Terminalyzer
from Source.Functions import Authorizate, SecondsToTimeString
from dublib.WebRequestor import WebRequestor, RequestsConfig
from Source.TitleParser import TitleParser

import datetime
import logging
import time
import sys
import os

#==========================================================================================#
# >>>>> ИНИЦИАЛИЗАЦИЯ СКРИПТА <<<<< #
#==========================================================================================#

# Проверка поддержки используемой версии Python.
CheckPythonMinimalVersion(3, 10)
# Создание папок в корневой директории.
MakeRootDirectories(["Covers", "Logs", "Titles"])

#==========================================================================================#
# >>>>> НАСТРОЙКА ЛОГГИРОВАНИЯ <<<<< #
#==========================================================================================#

# Получение текущей даты.
CurrentDate = datetime.datetime.now()
# Время запуска скрипта.
StartTime = time.time()
# Формирование пути к файлу лога.
LogFilename = "Logs/" + str(CurrentDate)[:-7] + ".log"
LogFilename = LogFilename.replace(":", "-")
# Установка конфигнурации.
logging.basicConfig(filename = LogFilename, encoding = "utf-8", level = logging.INFO, format = "%(asctime)s %(levelname)s: %(message)s", datefmt = "%Y-%m-%d %H:%M:%S")
# Отключение части сообщений логов библиотеки requests.
logging.getLogger("requests").setLevel(logging.CRITICAL)
# Отключение части сообщений логов библиотеки urllib3.
logging.getLogger("urllib3").setLevel(logging.CRITICAL)

#==========================================================================================#
# >>>>> ЧТЕНИЕ НАСТРОЕК <<<<< #
#==========================================================================================#

# Запись в лог сообщения: заголовок подготовки скрипта к работе.
logging.info("====== Preparing to starting ======")
# Запись в лог используемой версии Python.
logging.info("Starting with Python " + str(sys.version_info.major) + "." + str(sys.version_info.minor) + "." + str(sys.version_info.micro) + " on " + str(sys.platform) + ".")
# Запись команды, использовавшейся для запуска скрипта.
logging.info("Launch command: \"" + " ".join(sys.argv[1:len(sys.argv)]) + "\".")
# Очистка консоли.
Cls()
# Чтение настроек.
Settings = ReadJSON("Settings.json")

# Если путь к директории обложек не указан, задать стандартный.
if Settings["covers-directory"] == "":
	Settings["covers-directory"] = "Covers/"
	
# Если путь к директории обложек не заканчивается слэшем, то добавить его.
elif Settings["covers-directory"][-1] != '/':
	Settings["covers-directory"] += "/"

# Если путь к директории тайтлов не указан, задать стандартный.
if Settings["titles-directory"] == "":
	Settings["titles-directory"] = "Titles/"
	
# Если путь к директории тайтлов не заканчивается слэшем, то добавить его.
elif Settings["titles-directory"][-1] != '/':
	Settings["titles-directory"] += "/"

# Запись в лог сообщения: статус режима использования ID вместо алиаса.
logging.info("Using ID instead slug: " + ("ON." if Settings["use-id-instead-slug"] == True else "OFF."))

#==========================================================================================#
# >>>>> НАСТРОЙКА ОБРАБОТЧИКА КОМАНД <<<<< #
#==========================================================================================#

# Список описаний обрабатываемых команд.
CommandsList = list()

# Создание команды: getcov.
COM_getcov = Command("getcov")
COM_getcov.addArgument(ArgumentType.All, Important = True)
COM_getcov.addFlagPosition(["f"])
COM_getcov.addFlagPosition(["s"])
CommandsList.append(COM_getcov)

# Создание команды: parse.
COM_parse = Command("parse")
COM_parse.addArgument(ArgumentType.All, Important = True, LayoutIndex = 1)
COM_parse.addFlagPosition(["collection"], Important = True, LayoutIndex = 1)
COM_parse.addFlagPosition(["f"])
COM_parse.addFlagPosition(["s"])
COM_parse.addKeyPosition(["from"], ArgumentType.All)
CommandsList.append(COM_parse)

# Инициализация обработчика консольных аргументов.
CAC = Terminalyzer()
# Получение информации о проверке команд.
CommandDataStruct = CAC.checkCommands(CommandsList)

# Если не удалось определить команду.
if CommandDataStruct == None:
	# Запись в лог критической ошибки: неверная команда.
	logging.critical("Unknown command.")
	# Завершение работы скрипта с кодом ошибки.
	exit(1)
	
#==========================================================================================#
# >>>>> ОБРАБОТКА СПЕЦИАЛЬНЫХ ФЛАГОВ <<<<< #
#==========================================================================================#

# Активна ли опция выключения компьютера по завершении работы парсера.
IsShutdowAfterEnd = False
# Сообщение для внутренних функций: выключение ПК.
InFuncMessage_Shutdown = ""
# Активен ли режим перезаписи при парсинге.
IsForceModeActivated = False
# Сообщение для внутренних функций: режим перезаписи.
InFuncMessage_ForceMode = ""

# Обработка флага: режим перезаписи.
if "f" in CommandDataStruct.Flags and CommandDataStruct.Name not in []:
	# Включение режима перезаписи.
	IsForceModeActivated = True
	# Запись в лог сообщения: включён режим перезаписи.
	logging.info("Force mode: ON.")
	# Установка сообщения для внутренних функций.
	InFuncMessage_ForceMode = "Force mode: ON\n"

else:
	# Запись в лог сообщения об отключённом режиме перезаписи.
	logging.info("Force mode: OFF.")
	# Установка сообщения для внутренних функций.
	InFuncMessage_ForceMode = "Force mode: OFF\n"

# Обработка флага: выключение ПК после завершения работы скрипта.
if "s" in CommandDataStruct.Flags:
	# Включение режима.
	IsShutdowAfterEnd = True
	# Запись в лог сообщения о том, что ПК будет выключен после завершения работы.
	logging.info("Computer will be turned off after the script is finished!")
	# Установка сообщения для внутренних функций.
	InFuncMessage_Shutdown = "Computer will be turned off after the script is finished!\n"

#==========================================================================================#
# >>>>> ИНИЦИАЛИЗАЦИЯ МЕНЕДЖЕРА ЗАПРОСОВ <<<<< #
#==========================================================================================#

# Экземпляр навигатора.
Requestor = WebRequestor(Logging = True)
# Настройка конфигурации.
Config = RequestsConfig()
# Установка конфигурации.
Requestor.initialize()
# Авторизация.
Authorizate(Settings, Requestor)

#==========================================================================================#
# >>>>> ОБРАБОТКА КОММАНД <<<<< #
#==========================================================================================#

# Обработка команды: getcov.
if "getcov" == CommandDataStruct.Name:
	# Запись в лог сообщения: заголовок парсинга.
	logging.info("====== Parsing ======")
	# Парсинг тайтла (без глав).
	LocalTitle = TitleParser(Settings, Requestor, CommandDataStruct.Arguments[0], ForceMode = IsForceModeActivated, Message = InFuncMessage_Shutdown + InFuncMessage_ForceMode, Amending = False)
	# Сохранение локальных файлов тайтла.
	LocalTitle.downloadCover()

# Обработка команды: parse.
if "parse" == CommandDataStruct.Name:
	# Запись в лог сообщения: заголовок парсинга.
	logging.info("====== Parsing ======")
	# Список тайтлов для парсинга.
	TitlesList = list()
	# Индекс стартового алиаса.
	StartSlugIndex = 0
	
	# Если активирован флаг парсинга коллекций.
	if "collection" in CommandDataStruct.Flags:
		
		# Если существует файл коллекции.
		if os.path.exists("Collection.txt"):
			
			# Чтение содржимого файла.
			with open("Collection.txt", "r") as FileReader:
				# Буфер чтения.
				Bufer = FileReader.read().split("\n")
				
				# Поместить алиасы в список на парсинг, если строка не пуста.
				for Slug in Bufer:
					if Slug.strip() != "":
						TitlesList.append(Slug.strip())

			# Запись в лог сообщения: количество тайтлов в коллекции.
			logging.info("Titles count in collection: " + str(len(TitlesList)) + ".")
				
		else:
			# Запись в лог критической ошибки: отсутствует файл коллекций.
			logging.critical("Unable to find collection file.")
			# Выброс исключения.
			raise FileNotFoundError("Collection.txt")

	else:
		# Добавление аргумента в очередь парсинга.
		TitlesList.append(CommandDataStruct.Arguments[0])

	# Если указан алиас, с которого необходимо начать.
	if "from" in CommandDataStruct.Keys:
		
		# Если алиас присутствует в списке.
		if CommandDataStruct.Values["from"] in TitlesList:
			# Запись в лог сообщения: парсинг коллекции начнётся с алиаса.
			logging.info("Parcing will be started from \"" + CommandDataStruct.Values["from"] + "\".")
			# Задать стартовый индекс, равный индексу алиаса в коллекции.
			StartSlugIndex = TitlesList.index(CommandDataStruct.Values["from"])
			
		else:
			# Запись в лог предупреждения: стартовый алиас не найден.
			logging.warning("Unable to find start slug in \"Collection.txt\". All titles skipped.")
			# Задать стартовый индекс, равный количеству алиасов.
			StartSlugIndex = len(TitlesList)
			
	# Спарсить каждый тайтл из списка.
	for Index in range(StartSlugIndex, len(TitlesList)):
		# Часть сообщения о прогрессе.
		InFuncMessage_Progress = "Parcing titles: " + str(Index + 1) + " / " + str(len(TitlesList)) + "\n"
		# Генерация сообщения.
		ExternalMessage = InFuncMessage_Shutdown + InFuncMessage_ForceMode + InFuncMessage_Progress if len(TitlesList) > 1 else InFuncMessage_Shutdown + InFuncMessage_ForceMode
		# Парсинг тайтла.
		LocalTitle = TitleParser(Settings, Requestor, TitlesList[Index], ForceMode = IsForceModeActivated, Message = ExternalMessage)
		# Загружает обложку тайтла.
		LocalTitle.downloadCover()
		# Сохранение локальных файлов тайтла.
		LocalTitle.save()

#==========================================================================================#
# >>>>> ЗАВЕРШЕНИЕ РАБОТЫ СКРИПТА <<<<< #
#==========================================================================================#

# Закрытие запросчика.
Requestor.close()
# Запись в лог сообщения: заголовок завершения работы скрипта.
logging.info("====== Exiting ======")
# Очистка консоли.
Cls()
# Время завершения работы скрипта.
EndTime = time.time()
# Запись времени завершения работы скрипта.
logging.info("Script finished. Execution time: " + SecondsToTimeString(EndTime - StartTime) + ".")

# Выключение ПК, если установлен соответствующий флаг.
if IsShutdowAfterEnd == True:
	# Запись в лог сообщения о немедленном выключении ПК.
	logging.info("Turning off the computer.")
	# Выключение ПК.
	Shutdown()

# Выключение логгирования.
logging.shutdown()