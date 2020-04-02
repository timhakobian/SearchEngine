import re
from bs4 import BeautifulSoup
import os
import json
import glob
from collections import defaultdict
from nltk.stem import PorterStemmer
import math
import time
import threading

def extractText(html_content):
    soup = BeautifulSoup(html_content, "xml")
    for script in soup(["script", "style"]):
        script.extract()
    text = soup.get_text()
    return text


def tokenize(text):
    tokens = defaultdict(int)
    ps = PorterStemmer()
    words = re.split('[^a-zA-Z0-9]',text)
    for word in words:
        if word != '':
          	tokens[ps.stem(word.lower())] += 1
    return tokens


def buildIndex():
    total = 0
    count = 0
    n = 1
    index = defaultdict(list)
    urlDict = {}
    urlFile = open("url.json", "w")
    for file in glob.glob("ANALYST/*/*"):
        count += 1
        if count % 1000 == 0:
            for token, docs in index.items():
                if not os.path.isfile("tests" + str(n) + "/test" + token[0] + ".json"):
                    if not os.path.isdir("tests" + str(n)):
                        os.mkdir("tests" + str(n))
                    x = open("tests"  + str(n) + "/test" + token[0] + ".json", "w")
                    tempDict = dict()
                    tempDict[token] = docs
                    json.dump(tempDict, x)
                    x.close()
                else:
                    x = open("tests" + str(n) + "/test" + token[0] + ".json", "r+")
                    tempDict = dict()
                    tempDict[token] = docs
                    j = json.load(x)
                    j.update(tempDict)
                    x.close()
                    x = open("tests" + str(n) + "/test" + token[0] + ".json", "w")
                    json.dump(j, x)
                    x.close()
            index.clear()
            n += 1
        f = open(file, "r")
        data = json.load(f)
        text = extractText(data["content"])
        urlDict[total + 1] = data["url"]
        tokens = tokenize(text)
        for k, v in tokens.items():
            index[k].append([total + 1, v])
        total += 1
        f.close()
    json.dump(urlDict, urlFile)
    urlFile.close()
    return total


def parseTxt(file_name):
    f = open(file_name)
    dictionary = defaultdict(list)
    for line in f:
        line = line.strip()
        line = eval(line)
        dictionary[line[0]] = line[1]
    f.close()
    return dictionary


def search(string, numUrls):
    query = string.split(" ")
    mainDict = defaultdict(list)
    ps = PorterStemmer()

    def loop1():
        for word in query:
            word = word.lower()
            word.strip(" \n")
            if word in {"and", "of", "at", "in", "on", "for", "the", "what", "is", "are", "am" "not", "or", "how", "why", "when", "who", "a", "an"}:
                continue
            testNum = 1
            while(os.path.isdir("tests" + str(testNum)) and testNum < 28):
                f = open("tests" + str(testNum) + "/test"+word[0]+".json", "r")
                tokenDict = json.load(f)
                word = ps.stem(word)
                if word in tokenDict:
                    mainDict[word].extend(tokenDict[word])
                testNum += 1
    def loop2():
        for word in query:
            if word in {"and", "of", "at", "in", "on", "for", "the", "what", "is", "are", "am" "not", "or", "how", "why", "when", "who", "a", "an"}:
                continue
            testNum = 28
            while(os.path.isdir("tests" + str(testNum)) and testNum <= 55):
                f = open("tests" + str(testNum) + "/test"+word[0]+".json", "r")
                tokenDict = json.load(f)
                word = word.lower()
                word.strip(" \n")
                word = ps.stem(word)
                if word in tokenDict:
                    mainDict[word].extend(tokenDict[word])
                testNum += 1

    thread1 = threading.Thread(target = loop1)
    thread1.start()
    thread2 = threading.Thread(target = loop2)
    thread2.start()
    thread1.join()
    thread2.join()

		#calculate the tf-idf score
    for word, docandFreq in mainDict.items():
        temp = 0
        for doc in docandFreq:
            tf = doc[1]
            mainDict[word][temp][1] = (1 + math.log(tf, 10)) * math.log(numUrls/len(mainDict[word]),10)
            temp += 1
		#add together the tf-idf score for each word in the query
    docsList = []
    wordDict = defaultdict(int)

    for i in mainDict.values():
        for x in i:
            wordDict[x[0]] += x[1]

		#sort by the highest tf-idf score for the postings, get the document number and append to docs list
    for doc, count in sorted(wordDict.items(), key = lambda x: -x[1]):
        if count >= len(query):
            docsList.append(doc)

    Urls = open("url.json", "r")
    url_dict = json.load(Urls)

    print("RESULTS:")
    y = 0
    for x in docsList:
        if str(x) in url_dict.keys() and y < 10:
            print(url_dict[str(x)].strip())
            y += 1

    Urls.close()

i = 2

if i == 1:
    merge()
if i == 2:
    buildIndex()
if i == 3:
    while True:
        x = input("What would you like to search? ")
        if x == "quit":
            break
        search(x, 55393)
