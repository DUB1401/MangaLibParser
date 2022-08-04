import re

#������������ �������� ����� HTML.
TagsHTML = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')

#������� ���� HTML �� ������.
def RemoveHTML(TextHTML):
  CleanText = re.sub(TagsHTML, '', str(TextHTML))
  return str(CleanText)

#������� �� ������ �������: ����� ������, ���������, ������� �� ������ � �����.
def RemoveSpaceSymbols(Text):
    Text = Text.replace('\n', '')
    Text = Text.replace('\t', '')
    Text = ' '.join(Text.split())
    return Text.strip()

#�������� ������ ����� ������ �� ������� � ��������.
def ReplaceEndlToComma(Text):
    Text = Text.strip()
    Text = Text.replace('\n', ', ')
    return Text

#����������� ����������� ����� � int.
def LiteralToInt(String):
    if String.isdigit():
        return int(String)
    else:
        Number = float(String[:-1]) * 1000
    return int(Number)





















#�������� ������ � ����������� ����������� ����.
def GetChaptersCount(Soup):
    Divs = Soup.find_all('div', {'class': 'media-info-list__value text-capitalize'})
    ChaptersCount = RemoveHTML(Divs[1])
    return ChaptersCount

#�������� ������ �������� ������������ ����.
def GetCurrentChapters(Soup):
    BodyHTML = Browser.execute_script("return document.body.innerHTML;")
    Soup = BeautifulSoup(BodyHTML, "html.parser")
    ChaptersLinks = Soup.find_all('div', {'class': 'media-chapter__name text-truncate'})
    return ChaptersLinks

#������� ���������� ������ � ������.
def RemoveSameStrings(Array):

    return 0

#������� ��������� � ��������� ������ ����.
def SmoothScrollAndGetChapters(ChaptersCount, Soup):
    CurrentChapter = 0
    CodeJS = "window.scrollTo(0, "
    CurrentChapters = GetCurrentChapters(Soup)
    while CurrentChapter < ChaptersCount * 40 + 100:
        #��� ��� ��������� ���� �� ����� ��������� �������.
        if CurrentChapter % 1000 == 0:
            sleep(2);
            NewChapters = GetCurrentChapters(Soup)
            for InObj in NewChapters:
                print(InObj)
            CurrentChapters.extend(NewChapters)
        CurrentChapter += 5
        FullCodeJS = CodeJS + str(CurrentChapter) + ");"
        Browser.execute_script(FullCodeJS)
        PreResult = []
        Result = []
        #���������� � �������.
        for InObj in CurrentChapters:
            PreResult.append(str(InObj))
        #�������� ��������.
        for InObj in PreResult:
            if InObj not in Result:
                Result.append(InObj)
    return Result