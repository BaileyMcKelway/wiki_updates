import re
import requests
import imgkit
import time
import sys
from bs4 import BeautifulSoup
from datetime import datetime
from fuzzy_matcher import process


def addQueue(prevHref):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }

    req = requests.get(prevHref, headers)

    soup = BeautifulSoup(req.content, 'lxml')

    # find table
    title = soup.find("h1", id="firstHeading").get_text().split(":")[0]
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
        addedLineCleaned = re.sub(clean, '', addedLineCleaned)
        addedLineCleaned = BeautifulSoup(
            addedLineCleaned, 'html.parser')

        highlightedLines = addedLineCleaned.find_all(
            'ins', {"class": "diffchange-inline"})

        maxLength = 0

        if len(highlightedLines) == 0 and deletedLine == None:
            maxLength += len(addedLineCleaned.get_text())
        else:
            for i in range(len(highlightedLines)):
                highlightedLine = highlightedLines[i]
                maxLength += len(highlightedLine.get_text())

        print(maxLength)
        if maxLength <= 30:
            continue
        # CHECK FOR SIZE OF HIGHLIGHTED TEXT

        # CREATE ARRAY FOR  OBJECT
        revision = {
            'revisionId': 'revisionId',
            'title': title,
            'fullText': str(addedLineCleaned.get_text()),
            'changedText': str(addedLine),
            'curLink': 'curHref',
            'prevLink': prevHref
        }
        res.append(revision)
    return res


def checkDeleted(fullText, url):
    titles = ['National_responses_to_the_COVID-19_pandemic',
              'COVID-19_vaccine',
              'Workplace_hazard_controls_for_COVID-19',
              'COVID-19_pandemic_in_the_United_States',
              'COVID-19_pandemic_in_Brazil',
              'COVID-19_pandemic_in_India',
              'COVID-19_pandemic_in_Russia',
              'COVID-19_pandemic_in_South_Africa',
              'COVID-19_pandemic_in_Peru',
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
              'List_of_unproven_methods_against_COVID-19']

    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }
    # CHECK IF REVERT

    mainUrl = url
    article = requests.get(mainUrl, headers)
    urlsoup = BeautifulSoup(article.content, 'lxml')

    paragraphs = urlsoup.find_all('p')
    for i in range(len(paragraphs)):
        paragraphs[i] = paragraphs[i].text

    query = fullText
    fuzzy = process.extract(
        query, paragraphs, limit=3, scorer='ratio')
    print('FUZZY', fuzzy)


# print(addQueue('https://en.wikipedia.org/w/index.php?title=National_responses_to_the_COVID-19_pandemic&diff=985417966&oldid=985052321'))

testFullText = 'At a Sunday mass at [[St. Peter\'s Square]] in Vatican City on 26 January, [[Pope Francis]] praised "the great commitment by the Chinese community that has already been put in place to combat the epidemic" and commenced a closing prayer for "the people who are sick because of the virus that has spread through China". Microsoft co-founder [[Bill Gates]] defended the nation\'s COVID-19 response amidst criticism from the Trump administration, saying "China did a lot of things right at the beginning" and that "they got to zero" with "an effective lockdown". '
testUrl = 'https://en.wikipedia.org/wiki/National_responses_to_the_COVID-19_pandemic'

print(checkDeleted(testFullText, testUrl))
