import re
import requests
import imgkit
import tweepy
import time
import sys
from bs4 import BeautifulSoup
from datetime import datetime
from fuzzy_matcher import process
from datetime import datetime
from fuzzywuzzy import fuzz

key = 'NSkKvBJI7UHeUdWAlvsYknQEm'
secret = 'oBD3k0uczP5nkTcVnNkmKkuF0tel4vtAzYEHQHSj7gHRdmP1kG'

token = '1321211489278173186-9GrEzJ3CT1XKEhS1wEav2FiFBAVCKj'
tokenSecret = '2cqLHWi9vE6hDeLOKobZFDD3h5NnUIR24biOCTxDVbLAu'

auth = tweepy.OAuthHandler(key, secret)
auth.set_access_token(token, tokenSecret)


class WikiUpdate:

    def __init__(self):
        self.headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
        }

        self.titles = ['National_responses_to_the_COVID-19_pandemic',
                       'COVID-19_vaccine',
                       'Workplace_hazard_controls_for_COVID-19',
                       'COVID-19_pandemic_in_the_United_States',
                       'COVID-19_pandemic_in_Brazil',
                       'COVID-19_pandemic_in_India',
                       'COVID-19_pandemic_in_Russia',
                       'COVID-19_pandemic_in_South_Africa',
                       'COVID-19_pandemic_in_Mexico',
                       'COVID-19_pandemic_in_Chile',
                       'COVID-19_pandemic_in_the_United_Kingdom',
                       'COVID-19_pandemic_in_Iran',
                       'Severe_acute_respiratory_syndrome_coronavirus_2',
                       'Coronavirus',
                       'COVID-19_pandemic',
                       'Coronavirus_disease_2019',
                       'Coronavirus_disease',
                       'COVID-19_recession',
                       'Misinformation_related_to_the_COVID-19_pandemic',
                       'COVID-19_drug_development',
                       'Impact_of_the_COVID-19_pandemic_on_science_and_technology',
                       'Impact_of_the_COVID-19_pandemic_on_the_environment',
                       'Impact_of_the_COVID-19_pandemic_on_politics',
                       'Financial_market_impact_of_the_COVID-19_pandemic',
                       'Impact_of_the_COVID-19_pandemic_on_social_media',
                       'Mental_health_during_the_COVID-19_pandemic',
                       'Human_rights_issues_related_to_the_COVID-19_pandemic']

        self.mostRecent = {}
        self.queue = []
        self.api = tweepy.API(auth)

    def mainFunc(self):
        while True:
            # Main Data Structure for every revision
            revisionAll = {}

            # Loop Titles
            for title in self.titles:
                print('TITLE', title)
                url = 'https://en.wikipedia.org/w/index.php?title=' + title + '&action=history'

                # Query for new revision
                req = requests.get(url, self.headers)
                soup = BeautifulSoup(req.content, 'lxml')
                history = soup.find(id='pagehistory')

                # Finds all revisions on history page for specific article
                allRevisions = history.find_all('li')
                allRevisionsLength = len(allRevisions)

                mostRecentTime = None
                if title not in self.mostRecent:
                    mostRecentTime = allRevisions[allRevisionsLength - 1].find(
                        class_="mw-changeslist-date").get_text()
                else:
                    mostRecentTime = self.mostRecent[title]

                # Loops through every revision
                startChecking = False
                i = allRevisionsLength - 1
                while i >= 0:
                    currDate = allRevisions[i].find(
                        class_="mw-changeslist-date").get_text()
                    if mostRecentTime == currDate:
                        startChecking = True

                    if startChecking == True:
                        revisions = self.addQueue(allRevisions[i])
                        if revisions != None:
                            if title in revisionAll:
                                revisionAll[title] = revisionAll[title] + \
                                    revisions
                            else:
                                revisionAll[title] = revisions

                    i -= 1

                # Stores most recent revision and resets variables
                self.mostRecent[title] = allRevisions[0].find(
                    class_="mw-changeslist-date").get_text()
                allRevisions = []
                startChecking = False

            self.queue.append(revisionAll)

            if len(self.queue) >= 5:
                self.checkDeleted()

            # time.sleep(3600)

    def addQueue(self, curr):
        if self.checkSize(curr) == True:
            prevLink = curr.span.find('a', text='prev', href=True)
            currLink = curr.span.find('a', text='cur', href=True)

            if prevLink == None or currLink == None:
                return

            prevHref = 'https://en.wikipedia.org/' + prevLink['href']
            curHref = 'https://en.wikipedia.org/' + currLink['href']

            req = requests.get(prevHref, self.headers)
            soup = BeautifulSoup(req.content, 'lxml')

            # find table
            revisionId = curr['data-mw-revid']
            title = soup.find("h1", id="firstHeading").get_text().split(":")[0]
            date = soup.find(id="mw-diff-ntitle1").strong.a.get_text()
            table = soup.find('table')
            tableRows = table.find_all('tr')

            res = []
            # loop   through table rows
            for tableRow in tableRows:
                addedLine = tableRow.find(class_='diff-addedline')
                deletedLine = tableRow.find(class_='diff-deletedline')

                if addedLine != None and addedLine.find('div') == None:
                    addedLine = None

                if addedLine == None:
                    continue

                addedLineCleaned = str(addedLine)
                clean = re.compile('&lt;ref.*?&lt;/ref&gt;')
                w = re.findall(clean, addedLineCleaned)

                clean = re.compile('&lt;ref.*?/&gt;')
                x = re.findall(clean, addedLineCleaned)

                clean = re.compile('&lt;ref.*?&gt;')
                y = re.findall(clean, addedLineCleaned)

                clean = re.compile('&lt;/ref&gt;')
                z = re.findall(clean, addedLineCleaned)

                refs = w + x + y + z

                for ref in refs:
                    ins = re.findall('(<ins|</ins>)', ref)
                    length = len(ins) - 1
                    if length == - 1:
                        addedLineCleaned = addedLineCleaned.replace(ref, '')
                    elif ins[0] == '</ins>' and ins[length] == '<ins':
                        i = '</ins><ins class="diffchange diffchange-inline">'
                        addedLineCleaned = addedLineCleaned.replace(ref, i)
                    elif ins[0] == '</ins>':
                        i = '</ins>'
                        addedLineCleaned = addedLineCleaned.replace(ref, i)
                    elif ins[length] == '<ins':
                        i = '<ins class="diffchange diffchange-inline">'
                        addedLineCleaned = addedLineCleaned.replace(ref, i)
                    else:
                        addedLineCleaned = addedLineCleaned.replace(ref, '')

                if(addedLineCleaned.find('*') != -1):
                    continue

                if(addedLineCleaned.find('[[File') != -1):
                    continue

                if(len(addedLineCleaned.split(" ")) == 1):
                    continue

                addedLineCleaned = BeautifulSoup(
                    addedLineCleaned, 'html.parser')

                highlightedLines = addedLineCleaned.find_all(
                    'ins', {"class": "diffchange-inline"})

                # Determines if edit is substantial
                maxLength = 0
                if len(highlightedLines) == 0 and deletedLine == None:
                    maxLength += len(addedLineCleaned.get_text())
                else:
                    for i in range(len(highlightedLines)):
                        highlightedLine = highlightedLines[i]
                        maxLength += len(highlightedLine.get_text())

                if maxLength <= 40:
                    continue

                revision = {
                    'revisionId': revisionId,
                    'date': date,
                    'title': title,
                    'fullText': str(addedLineCleaned),
                    'changedText': str(addedLine),
                    'curLink': curHref,
                    'prevLink': prevHref
                }
                res.append(revision)
            return res

    def checkDeleted(self):
        checkRevisions = self.queue.pop(0)
        final = []
        i = 0
        for title in self.titles:
            mainUrl = 'https://en.wikipedia.org/wiki/' + title
            article = requests.get(mainUrl, self.headers)
            urlsoup = BeautifulSoup(article.content, 'lxml')

            paragraphs = urlsoup.find_all(['p', 'h1', 'h2', 'h3'])
            for i in range(len(paragraphs)):
                text = paragraphs[i].text
                element = paragraphs[i]
                paragraphs[i] = {'text': text, 'element': element}

            if title in checkRevisions:
                checkCurrentTitle = checkRevisions[title]
                for revision in checkCurrentTitle:
                    query = revision['fullText']
                    fuzzyMatches = []
                    for i in range(len(paragraphs)):
                        paragraph = paragraphs[i]
                        Token_Set_Ratio = fuzz.token_set_ratio(
                            query, paragraph['text'])
                        fuzzyRes = {
                            'paragraph': paragraph['text'],
                            'Token_Set_Ratio': Token_Set_Ratio,
                            'index': i
                        }
                        fuzzyMatches.append(fuzzyRes)

                    fuzzyMatches = sorted(
                        fuzzyMatches, key=lambda i: i['Token_Set_Ratio'], reverse=True)

                    if(fuzzyMatches[0]['Token_Set_Ratio'] >= 85):
                        options = {'width': 525,
                                   'disable-smart-width': '', 'quality': 100}
                        css = 'styles.css'

                        changedText = revision['fullText']

                        if(changedText.find('|{{') != -1):
                            continue

                        clean = re.compile('{{(c|C)ite.*?}}')
                        changedText = re.sub(clean, '', changedText)

                        brackets = re.findall(r'\[\[(.*?)\]\]', changedText)
                        for i in range(len(brackets)):
                            split = brackets[i].split('|')
                            name = split[1] if len(split) > 1 else split[0]

                            search = '[[' + split[0] + \
                                '|' + \
                                split[1] + \
                                ']]' if len(
                                split) > 1 else '[[' + split[0] + ']]'

                            changedText = changedText.replace(search, name)
                        if len(changedText) < 90:
                            continue

                        fileName = revision['revisionId'] + str(i) + ".jpg"
                        date = revision['date']
                        dateStrip = date.split('of')[1]
                        i += 1
                        # FIND TITLE
                        title = re.sub('_', ' ', title)
                        subTitle = self.findTitle(fuzzyMatches[0], paragraphs)
                        mainTitles = '''<div id="header"><p>Article: {}</p><p>Title: {}</p><p>{}</p></div>'''.format(
                            title, subTitle, date)
                        html = '''<html lang="en">
                                    <head>
                                        <meta content="text/html; charset=utf-8" http-equiv="Content-type">
                                        <meta content="jpg" name="imgkit-format">   
                                        <meta charset="UTF-8">
                                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                                    </head>
                                    <body>
                                        {}
                                        <div class="diff-addedline">
                                        {}
                                        </div>
                                    </body>
                                </html>'''.format(mainTitles, changedText)
                        res = {'html': html, 'date': dateStrip}

                        final.append(res)

        final.sort(key=lambda each_dict: datetime.strptime(
            each_dict['date'], ' %H:%M, %d %B %Y'))
        for tweet in final:
            html = tweet['html']
            imgkit.from_string(html, 'out.jpg', options=options, css=css)
            self.api.update_with_media('./out.jpg')

    def checkSize(self, curr):
        diffBytes = curr.find_all(
            ['span', 'strong'], class_='mw-diff-bytes', dir='ltr')[0]

        if diffBytes:
            size = diffBytes.get_text()
            size = re.sub('[+-,]', '', size)
            return int(size) >= 300
        else:
            return

    def findTitle(self, match, paragraphs):
        i = match['index']
        while(i >= 0):
            currTag = paragraphs[i]['element'].name
            if(currTag == 'h1' or currTag == 'h2' or currTag == 'h3'):
                if paragraphs[i]['element'].span != None:
                    return paragraphs[i]['element'].span.get_text()
                else:
                    return paragraphs[i]['element'].get_text()
            i -= 1

        return


Scraper = WikiUpdate()

Scraper.mainFunc()
