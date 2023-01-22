# MangaLib Parser
**MangaLib Parser** – это кроссплатформенный скрипт для получения данных с семейства сайтов [MangaLib](https://mangalib.me/), [YaoiLib](https://yaoilib.me/) и [HentaiLib](https://hentailib.me/) в формате JSON. Он позволяет записать всю информацию о конкретной манге, а также её главах и содержании глав. Файлы на выходе совместимы с парсером API сайта [ReManga](https://remanga.org/).
## Порядок установки и использования
1. Установить Python версии не старше 3.9. При установке рекомендуется добавить в PATH.
2. Скачать [Google Chrome](https://www.google.by/intl/ru/chrome/) и установить в директорию по умолчанию.
3. В среду исполнения установить следующие пакеты вручную или при помощи файла _requirements.txt_: random_user_agent, webdriver-manager, BeautifulSoup4, Selenium, Pillow, lxml.
```
pip install random_user_agent
pip install webdriver-manager
pip install BeautifulSoup4
pip install Selenium
pip install Pillow
pip install lxml
```
4. Настроить скрипт путём редактирования *Settings.json*.
5. Открыть директорию со скриптом в консоли. Можно использовать метод `cd` и прописать путь к папке, либо открыть терминал из проводника.
6. Ввести нужную команду и дождаться завершения. Не сворачивайте браузер, так как это может привести к исключениям области видимости.

**Важно:** В зависимости от ОС может потребоваться полное написание названия главного файла. Например, на Windows 11 достаточно `mlp`, в то время как на Windows 10 необходимо использовать `mlp.py`.
# Консольные команды
```
mlp scan [SOURCE]
```
Получение списка алиасов тайтлов со страницы каталога сайта и его сохранение в рабочую директорию как _#Manifest.json_. В качестве источника принимает URL-адрес страницы каталога на сайте (поддерживает запросы сортировки), либо флаг _**-target**_. В последнем случае URL будет взят из _#Settings.json_.
____
```
mlp parce [MANGA_SLUG] [FLAGS]
```
Парсинг тайтла, алиас которого передаётся вторым аргументом.

**Пример:** mlp parce dr-stone

Если вместо алиаса передать аргумент _**-all**_, то скрипт по очереди будет обрабатывать все тайтлы из *#Manifest.json*. 

**Список специфических флагов:**
* _**-f**_ – включает перезапись уже существующих файлов;
* _**-am**_ – запускает `mlp amend [MANGA_SLUG]`, в которую передаёт список полученных тайтлов.
____
```
mlp update [MANGA_SLUG]
```
Обновление тайтла, алиас которого передаётся вторым аргументом, путём добавления в него отсутствующих глав и ветвей переводов.

**Пример:** mlp update dr-stone

Если вместо алиаса передать аргумент _**-all**_, то скрипт по очереди будет обрабатывать все тайтлы из рабочей директории.

**Список специфических флагов:**
* _**-am**_ – запускает `mlp amend [MANGA_SLUG]`, в которую передаёт список обновлённых тайтлов.
____
```
mlp amend [MANGA_SLUG]
```
Дополнение JSON тайтла размерами слайдов в пикселях методом запросов с альтернативных серверов, если таковые отсутствуют у некоторых или всех глав.

**Пример:** mlp amend dr-stone

Если вместо алиаса передать аргумент _**-all**_, то скрипт по очереди будет обрабатывать все тайтлы из рабочей директории.
____
```
mlp ubid [MANGA_SLUG]
```
Выводит уникальный ID манги на основе десятиричного представления MD5 хеш-суммы алиаса. Для тайтлов с несколькими ветвями перевода данное значение может отличаться, потому что в таких случаях к ID ветви добавляется значение _bid_ перевода.

**Пример:** В результате выполнения функции было выведено значение 12345. В файле JSON ветви перевода будут обозначены 12345**678** и 12345**679**, где последняя часть является значением _bid_ из адресной строки главы (https://mangalib.me/manganame/v1/c1?bid=678).
____
```
mlp getsl [CHAPTER_URL]
```
Получает данные о слайдах конкретной главы из переданного URL (можно использовать как полный URL, так и значение из логов). Для этой команды функционируют настройки "_disable-age-limit-warning_" и "_sign-in_". Информация сохраняется в файл _#Slides.json_.

**Примечание:** Полезно, когда в логах вы видите ошибку о неполном парсинге главы. Просто скопируйте URL из лога, подставьте в команду, и на выходе получите полные данные о слайдах для восстановления JSON.
____
```
mlp chtest
```
Запускает тест [Chrome Headless Detection](https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html) и выводит его результаты в консоль.
____
```
mlp -s
```
Флаг _**-s**_ выключает компьютер после завершения работы скрипта. Его можно добавить к любой другой команде.

# Settings.json
```
"domain" : "mangalib"
```
Устанавливает целевой домен, с которого будет происходить парсинг. Поддерживаются значения: _mangalib_, _yaoilib_, _hentailib_.
____
```
"directory" : ""
```
Задаёт рабочую директорию. Сюда будут сохраняться файлы манги, манифест, определения слайдов и отсюда же будут браться список тайтлов для обновления. По умолчанию каталог задаётся в зависимости от домена: _"manga"_, _"hentai"_ или _"yaoi"_.
____
```
"scan-target" : ""
```
Задаёт страницу каталога манги, откуда будет собран манифест. Указать URL страницы с аргументами сортировки. 

**Пример:** "https://mangalib.me/manga-list?page=2&status[]=2". В манифест будут записаны данные о манге со статусом «Завершено», вторая страница каталога.
____
```
"sign-in" : false
```
Указывает, проводить ли вход в аккаунт. Необходимо для парсинга 18+ тайтлов.
> **Warning**
> Для корректной работы в аккаунте должен быть подтверждён возраст. Если вы этого не сделали, зайдите в главу любого 18+ тайтла и введите дату рождения в появившемся окне.
____
```
"user-id" : null
```
Задаёт ID пользователя, необходимый для доступа к главам 18+. В случае, если не установлен вручную, будет определён автоматически.

Получить можно из адресной строки на страничке любой манги: "...&ui=XXXX".
____
```
"email": "",
"password": ""
```
Задаёт логин и пароль для входа. Если аккаунт зарегестрирован через кнопки социальных сетей, электронную почту к нему можно указать в настройках сайта.
____
```
"delay": 5
```
Устанавливает интервал в секундах между загрузкой глав, а также между получением слайдов для уменьшения нагрузки на сервера. Помогает избежать блокировки по IP за быстрые автоматические запросы. 

Рекомендуемое значение: не менее 5 секунд.
____
```
"getting-slide-sizes": false
```
Переключатель, отвечающий за получение размеров слайдов. Без загрузки каждого слайда и его проверки скорость парсинга возрастает в десятки раз, однако определение размеров слайдов становится невозможным, а скрипт перестаёт проверять содержимое слайдов на целостность. Не учитывается при работе `mlp amend`.
____
```
"server": "fourth"
```
Устанавливает сервер, для которого будут формироваться ссылки. Работает только для нового режима получения слайдов. Список доступных серверов можно узнать на целевом сайте в JS-переменной `window.__info`. Рекомендуется сервер _fourth_ как наиболее стабильный и часто используемый.

Поддерживаются: _main_, _secondary_, _compress_, _fourth_.
____
```
"logs-cleanup": true
```
При включении будут сохраняться только те логи, которые относятся к командам `mlp parce`, `mlp update` и `mlp amend`.

*Evolv Group. Copyright © 2018-2023.*
