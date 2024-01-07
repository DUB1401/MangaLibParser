# MangaLib Parser
**MangaLib Parser** – это кроссплатформенный скрипт для получения данных с семейства сайтов [MangaLib](https://mangalib.me/), [HentaiLib](https://hentailib.me/) и [YaoiLib](https://yaoilib.me/) в JSON. Он позволяет записать всю информацию о конкретной манге, а также её главах и содержании глав в формате [DMP-V1](Examples/DMP-V1.md).

## Порядок установки и использования
1. Загрузить последний релиз. Распаковать.
2. Установить Python версии не старше 3.10. Рекомендуется добавить в PATH.
3. В среду исполнения установить следующие пакеты: [BeautifulSoup4](https://launchpad.net/beautifulsoup), [dublib](https://github.com/DUB1401/dublib).
```
pip install BeautifulSoup4
pip install dublib==0.2.0
```
Либо установить сразу все пакеты при помощи следующей команды, выполненной из директории скрипта.
```
pip install -r requirements.txt
```
4. Настроить скрипт путём редактирования _Settings.json_ и _Proxies.json_.
5. Открыть директорию со скриптом в терминале. Можно использовать метод `cd` и прописать путь к папке, либо запустить терминал из проводника.
6. Указать для выполнения главный файл скрипта `mlp.py`, передать ему команду вместе с параметрами, нажать кнопку ввода и дождаться завершения работы.

# Консольные команды
```
getcov [MANGA_SLUG*] [FLAGS]
```
Загружает обложки конкретного тайтла, алиас которого передан в качестве аргумента.

**Список специфических флагов:**
* _**-f**_ – включает перезапись уже загруженных обложек.
___

```
parse [TARGET*] [MODE] [DOMAIN] [FLAGS] [KEYS]
```
Проводит парсинг тайтла с указанным алиасом в JSON формат и загружает его обложки. В случае, если файл тайтла уже существует, дополнит его новыми данными. 

**Описание позиций:**
* **TARGET** – задаёт цель для парсинга. Обязательная позиция.
	* Аргумент – алиас тайтла для парсинга.
	* Флаги:
		* _**-collection**_ – указывает, что список тайтлов для парсинга необходимо взять из файла _Collection.txt_;
		* _**-local**_ – указывает для парсинга все локальные файлы.
* **MODE** – указывает, какие данные необходимо парсить.
	* Флаги:
		* _**-onlydesc**_ – будет произведено обновление только описательных данных тайтла, не затрагивающее ветви перевода и главы.
* **DOMAIN** – указывает, на каком дополнительном домене искать тайтл.
	* Флаги:
		* _**-h**_ – поиск будет произведён на [HentaiLib](https://hentailib.me/);
		* _**-y**_ – поиск будет произведён на [YaoiLib](https://yaoilib.me/).
		
**Список специфических флагов:**
* _**-f**_ – включает перезапись уже загруженных обложек и существующих JSON файлов.

**Список специфических ключей:**
* _**--from**_ – указывает алиас тайтла, с момента обнаружения которого в коллекции тайтлов необходимо начать парсинг.
___
```
repair [FILENAME*] [CHAPTER_ID*]
```
Обновляет и перезаписывает сведения о слайдах конкретной главы в локальном файле.

**Описание позиций:**
* **FILENAME** – имя локального файла, в котором необходимо исправить слайды. Обязательная позиция.
	* Аргумент – имя файла (с расширением или без него).
* **CHAPTER_ID** – ID главы в локальном файле, слайды которой необходимо заново получить с сервера. Обязательная позиция.
	* Ключи:
		* _**--chapter**_ – указывает ID главы.
___
```
update [MODE] [DOMAIN] [FLAGS] [KEYS]
```
Проводит парсинг тайтлов, в которые за интервал времени, указанный в _Settings.json_, были добавлены новые главы.

**Описание позиций:**
* **MODE** – указывает, какие данные необходимо обновлять. Может принимать следующие значения:
	* Флаги:
		* _**-onlydesc**_ – будет произведено обновление только описательных данных тайтла, не затрагивающее ветви перевода и главы.
* **DOMAIN** – указывает, на каком дополнительном домене искать тайтл.
	* Флаги:
		* _**-h**_ – поиск будет произведён на [HentaiLib](https://hentailib.me/);
		* _**-y**_ – поиск будет произведён на [YaoiLib](https://yaoilib.me/).

**Список специфических флагов:**
* _**-f**_ – включает перезапись уже загруженных обложек и существующих JSON файлов.

**Список специфических ключей:**
* _**--from**_ – указывает алиас тайтла, с момента обнаружения которого в списке обновляемых тайтлов необходимо начать обработку обновлений.

## Неспецифические флаги
Данный тип флагов работает при добавлении к любой команде и выполняет отдельную от оной функцию.
* _**-s**_ – выключает компьютер после завершения работы скрипта.

# Settings.json
```JSON
"login": ""
```
Здесь необходимо указать электронную почту или логин аккаунта для авторизации.
___
```JSON
"password": ""
```
Здесь необходимо указать пароль аккаунта для авторизации.
___
```JSON
"user-id": 0
```
Здесь необходимо указать ID аккаунта, взять который можно из адресной строки браузера после авторизации. Будет указан на главной странице в параметре запроса _updates-home-{ID}_.
___
```JSON
"use-id-instead-slug": false
```
При включении данного параметра файлы JSON и директория обложки тайтла будут названы по ID произведения, а не по алиасу. При этом уже существующие данные обновляются в автоматическом режиме.
___
```JSON
"check-updates-period": 24
```
Указывает, обновления за какой период времени до запуска скрипта (в часах) нужно получить.
___
```JSON
"titles-directory": ""
```
Указывает, куда сохранять JSON-файлы тайтлов. При пустом значении будет создана папка Titles в исполняемой директории скрипта. Рекомендуется оформлять в соответствии с принципами путей в Linux, описанными [здесь](http://cs.mipt.ru/advanced_python/lessons/lab02.html#cd).
___
```JSON
"covers-directory": ""
```
Указывает, куда сохранять обложки тайтлов. При пустом значении будет создана папка _Covers_ в исполняемой директории скрипта. Рекомендуется оформлять в соответствии с принципами путей в Linux, описанными [здесь](http://cs.mipt.ru/advanced_python/lessons/lab02.html#cd).
___
```JSON
"proxy": {
	"enable": false,
	"host": "",
	"port": "",
	"login": null,
	"password": null
}
```
Указывает HTTPS-прокси для выполнения запросов. Помогает обойти региональные ограничения доступа к сайту.
___
```JSON
"delay": 1
```
Устанавливает интервал в секундах между последовательными запросами к серверу.

_Copyright © DUB1401. 2022-2024._
