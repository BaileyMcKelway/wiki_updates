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


def checkDeleted(fullText, url, paragraph):
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

    paragraphs = [paragraph]
    # for i in range(len(paragraphs)):
    #     paragraphs[i] = paragraphs[i].text

    query = fullText
    fuzzy = process.extract(
        query, paragraphs, limit=3, scorer='ratio')
    print('FUZZY', fuzzy)


# print(addQueue('https://en.wikipedia.org//w/index.php?title=Coronavirus&diff=977846836&oldid=977765636'))

testFullText = 'The M protein is the main structural protein of the envelope and is a type III membrane protein. It consists of 218 to 263 amino acid residues and form a layer of 7.8 nm thick.'
testUrl = 'https://en.wikipedia.org/wiki/Coronavirus'
testParagraph = 'The M protein is the main structural protein of the envelope that provides the overall shape and is a type III membrane protein. It consists of 218 to 263 amino acid residues and forms a layer of 7.8 nm thickness.[46] It has three domains such as a short N-terminal ectodomain, a triple-spanning transmembrane domain, and a C-terminal endodomain. The C-terminal domain forms a matrix-like lattice that adds to the extra-thickness of the envelope. Different species can have either N- or O-linked glycans in their protein amino-terminal domain. The M protein is crucial in the life cycle of the virus such as during assembly'

print(checkDeleted(testFullText, testUrl, testParagraph))
