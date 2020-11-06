import re
import requests
import imgkit
import time
import sys
import Levenshtein as lev
from fuzzywuzzy import fuzz
from bs4 import BeautifulSoup
import datetime
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
            length = len(ins)
            if ins[0] == '</ins>' and ins[length] == '<ins':
                return '</ins><ins class="diffchange diffchange-inline">'
            elif ins[0] == '</ins>':
                return '</ins>'
            elif ins[length] == '<ins':
                return '<ins class="diffchange diffchange-inline">'
            else:
                return ''

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

    res = []
    for paragraph in paragraphs:
        Ratio = fuzz.ratio(fullText.lower(), paragraph.lower())
        Partial_Ratio = fuzz.partial_ratio(
            fullText.lower(), paragraph.lower())
        Token_Set_Ratio = fuzz.token_set_ratio(fullText, paragraph)
        resObject = {
            'paragraph': paragraph,
            'Ratio': Ratio,
            'Partial_Ratio': Partial_Ratio,
            'Token_Set_Ratio': Token_Set_Ratio
        }
        res.append(resObject)
    res = sorted(res, key=lambda i: i['Token_Set_Ratio'], reverse=True)
    return res[0]


# print(addQueue('https://en.wikipedia.org//w/index.php?title=Coronavirus&diff=977846836&oldid=977765636'))
testFullText = 'to help in the National COVID-19 Treatment.'
testUrl = 'https://en.wikipedia.org/wiki/National_responses_to_the_COVID-19_pandemic'
# testParagraph = 'The M protein is the main structural protein of the envelope that provides the overall shape and is a type III membrane protein. It consists of 218 to 263 amino acid residues and forms a layer of 7.8 nm thickness.[46] It has three domains such as a short N-terminal ectodomain, a triple-spanning transmembrane domain, and a C-terminal endodomain. The C-terminal domain forms a matrix-like lattice that adds to the extra-thickness of the envelope. Different species can have either N- or O-linked glycans in their protein amino-terminal domain. The M protein is crucial in the life cycle of the virus such as during assembly'

# print(checkDeleted(testFullText, testUrl))

# Distance = lev.distance(testParagraph.lower(), testFullText.lower()),
# print(Distance)
# Ratio = lev.ratio(testParagraph.lower(), testFullText.lower())
# print(Ratio)


# print(Ratio)
# print(Partial_Ratio)
# print(Token_Set_Ratio)
# options = {'width': 475, 'disable-smart-width': '', 'quality': 100}
# css = 'styles.css'
# imgkit.from_file('test.html', 'out.jpg', options=options, css=css)
# test = '''<td class="diff-addedline"><div>In the United States, Section 11(c) of the [[Occupational Safety and Health Act (United States)|Occupational Safety and Health Act of 1970]] prohibits employers from retaliating [[Occupational Safety and Health Act (United States)|Occupational Safety and Health Act of0]] against workers for raising concerns about safety and health conditions.  OSHA encourages workers who suffer such retaliation to submit a complaint to OSHA’s Whistleblower Protection Program within the legal time limits.&lt;ref name=":4" /&gt;&lt;ref&gt;{{Cite web|title=The Whistleblower Protection Program|url=https://www.whistleblowers.gov/|last=|first=|date=|website=U.S. Occupational Safety and Health Administration|url-status=live|archive-url=|archive-date=|access-date=2020-05-08}}&lt;/ref&gt;</div></td>'''
# '[[Occupational Safety and Health Act (United States)|Occupational Safety and Health Act of 197Occupational Safety and Health Act of 1970]'
# clean = re.compile('&lt;ref.*?&lt;/ref&gt;')
# test = re.sub(clean, '', test)

# brackets = re.findall(r'\[\[(.*?)\]\]', test)
# print("Brackets", brackets)
# for i in range(len(brackets)):
#     split = brackets[i].split('|')
#     name = split[1] if len(split) > 1 else split[0]

#     search = '[[' + split[0] + \
#         '|' + \
#         split[1] + \
#         ']]' if len(
#         split) > 1 else '[[' + split[0] + ']]'

#     # clean = re.compile(search)
#     print(search, name)

#     test = test.replace(search, name)
#     print("Final", test)

# print(test)
# tester = 'dsfijgndgnsbk;fgnb;gjklsbnbgjkngjkbnsgjk;bnk;jngkv;bngsnbsgn'

# print(len(tester.split(" ")))


# addedLineCleaned = '''<td class="diff-addedline"><div>China's response to the virus, in comparison to the [[2003 SARS outbreak]], has been praised by some foreign leaders<ins class="diffchange diffchange-inline"> and analysts.&lt;ref&gt;{{Cite news|last=[[Donald McNeil Jr.]]|first=|date=2020-03-25|title=The Virus Can Be Stopped, but Only With Harsh Steps, Experts Say|language=en-US|work=The New York Times|url=https://www.nytimes.com/2020/03/22/health/coronavirus-restrictions-us.html|url-status=live|access-date=2020-10-25|issn=0362-4331}}&lt;/ref&gt; UN Secretary General [[António Guterres|Antonio Guterres]] stated on February that it was clear "there is a massive effort that is made by China in order to contain the disease and avoid its propagation" and added the effort was "remarkable".&lt;ref&gt;{{Cite web|date=2020-02-08|title=UN’s Guterres praises China’s ‘remarkable’ coronavirus response|url=https://news.abs-cbn.com/overseas/02/08/20/uns-guterres-praises-chinas-remarkable-coronavirus-response|url-status=live|archive-url=|archive-date=|access-date=2020-10-25|website=[[ABS-CBN]], [[Agence France-Presse]]|language=en}}&lt;/ref&gt;</ins> U.S. President Trump thanked Chinese leader Xi Jinping "on behalf of the American People" on 24 January on Twitter, stating that "China has been working very hard to contain the Coronavirus. The United States greatly appreciates their efforts and transparency."&lt;ref&gt;{{cite web |url= https://www.straitstimes.com/world/united-states/trump-praises-china-efforts-and-transparency-on-wuhan-virus |title=Trump praises China 'efforts and transparency' on Wuhan virus |date=25 January 2020 |work=[[The Straits Times]] |url-status=live |archive-url= https://web.archive.org/web/20200127163253/https://www.straitstimes.com/world/united-states/trump-praises-china-efforts-and-transparency-on-wuhan-virus |archive-date=27 January 2020 |access-date=28 January 2020}}&lt;/ref&gt; Germany's health minister [[Jens Spahn]], in an interview on ''[[Bloomberg Television|Bloomberg TV]]'', said with comparison to the Chinese response to SARS in 2003: "There's a big difference to SARS. We have a much more transparent China. The action of China is much more effective in the first days already." He also praised the international co-operation and communication in dealing with the virus.&lt;ref&gt;{{cite news |url= https://www.dw.com/en/coronavirus-reaches-europe-as-france-confirms-3-cases/a-52145333 |title=Coronavirus reaches Europe as France confirms 3 cases |date=24 January 2020 |work=[[Deutsche Welle]] |access-date=28 January 2020}}&lt;/ref&gt;&lt;ref&gt;{{cite web |url= https://www.bloomberg.com/news/articles/2020-01-24/china-doing-good-job-in-combating-virus-german-minister-says |title=China Doing Good Job in Combating Virus, German Minister Says |work=[[Bloomberg News]] |access-date=28 January 2020 |url-access=subscription}}&lt;/ref&gt; In a letter to Xi, Singaporean president [[Halimah Yacob]] applauded China's "swift, decisive and comprehensive measures" in safeguarding the health of the Chinese people, while prime minister [[Lee Hsien Loong]] remarked of "China's firm and decisive response" in communities affected by the virus.&lt;ref&gt;{{cite web |url= https://www.channelnewsasia.com/news/singapore/covid19-coronavirus-singapore-china-solidarity-12465678 |title=Singapore leaders stand in solidarity with China over COVID-19 outbreak |work=[[Channel NewsAsia]] |access-date=24 February 2020}}&lt;/ref&gt; Similar sentiments were expressed by Russian president [[Vladimir Putin]].&lt;ref&gt;{{cite web |url= https://www.scmp.com/news/china/diplomacy/article/3050782/russia-and-china-pledge-maintain-special-relationship-despite |title=Russia and China pledge to maintain special relationship despite Moscow's slow response to coronavirus |work=[[South China Morning Post]] |access-date=24 February 2020 |date=16 February 2020}}&lt;/ref&gt;</div></td>'''
# clean = re.compile('&lt;ref.*?&lt;/ref&gt;')
# w = re.findall(clean, addedLineCleaned)

# clean = re.compile('&lt;ref.*?/&gt;')
# x = re.findall(clean, addedLineCleaned)

# clean = re.compile('&lt;ref.*?&gt;')
# y = re.findall(clean, addedLineCleaned)

# clean = re.compile('&lt;/ref&gt;')
# z = re.findall(clean, addedLineCleaned)

# refs = w

# for ref in refs:
#     ins = re.findall('(<ins|</ins>)', ref)
#     length = len(ins) - 1
#     if length == - 1:
#         addedLineCleaned = addedLineCleaned.replace(ref, '')
#     elif ins[0] == '</ins>' and ins[length] == '<ins':
#         i = '</ins><ins class="diffchange diffchange-inline">'
#         addedLineCleaned = addedLineCleaned.replace(ref, i)
#     elif ins[0] == '</ins>':
#         i = '</ins>'
#         addedLineCleaned = addedLineCleaned.replace(ref, i)
#     elif ins[length] == '<ins':
#         i = '<ins class="diffchange diffchange-inline">'
#         addedLineCleaned = addedLineCleaned.replace(ref, i)
#     else:
#         addedLineCleaned = addedLineCleaned.replace(ref, '')
# changedText = "{{cite web|}}"
# clean = re.compile('{{(C|c)ite.*?}}')
# changedText = re.sub(clean, 'a', changedText)

# print(changedText)

test = [" 18:35, 8 February 2020", " 18:35, 8 March 1000",
        " 18:35, 8 April 2020", " 18:36, 8 February 2020"]




print(test)
