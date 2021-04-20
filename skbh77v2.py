import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import os
import math
import openpyxl
import xlsxwriter as xls
import numpy as np
import time
import seaborn
import pandas as pd
keywords = ["targeted threat","Advanced Persistent Threat","phishing","DoS attack","malware","computer virus","spyware","malicious bot","ransomware","encryption"]

##Problem 1
def getKeywords():
    keywords = []
    keywordsBook = openpyxl.load_workbook(filename = "keywords.xlsx")
    sheet=keywordsBook.active
    yPos = 2
    newKeyword = sheet['A2'].value
    while(newKeyword != None):
        keywords.append(newKeyword)
        yPos+=1
        newKeyword = sheet['A'+str(yPos)].value
    return keywords

def problem1():
    keywords = getKeywords()
    print(keywords)
    bbcArticles = bbc(keywords)
    nyArticles = nyTimes(keywords)
    print(len(bbcArticles),len(nyArticles))
    articles = [bbcArticles,nyArticles]

    downloadedArticles = []
    for siteNum in range(0,len(articles)):
        siteArticles = []
        for keywordNum in range(0,len(articles[siteNum])):
            keywordData = []
            for articleNum in range(0,len(articles[siteNum][keywordNum])): 
                articleData = []
                url =  articles[siteNum][keywordNum][articleNum]
                try:
                    req = urllib.request.Request(url)
                    resp = urllib.request.urlopen(req)
                    data = resp.read()
                    keywordData.append(data)
                except:
                    pass
            siteArticles.append(keywordData)
        downloadedArticles.append(siteArticles)
    return downloadedArticles,keywords

def bbc(keywords):
    url = "https://www.bbc.co.uk/search"
    articles = []
    for keyword in keywords:
        print(keyword)
        keywordArticles = []
        page = 0
        moreResults = True
        while len(keywordArticles) < 100 and moreResults:
            moreResults = False
            page += 1
            values = {'q':keyword,'page':str(page)}
            #print(values)
            data = urllib.parse.urlencode(values)
            req = urllib.request.Request(url+'?'+data)
            resp = urllib.request.urlopen(req)
            respData = resp.read()
            string = "Search results for "+keyword+"</h2>"
            test = string.encode('utf_8')
            soup = BeautifulSoup(respData,features="html.parser")
            main = soup.find(id= 'main-content')
            links = main.find_all('a')
            #print(links)
            for link in links:
                result = link.get('href')
                
                if "/search" not in result:
                    #print("Result",result)
                    if  len(keywordArticles) >= 100:
                        moreResults = False
                        break
                    elif "news" in result or "sport" in result:
                    #elif "programme" not in result and "/sound" not in result and "/search"  not in result and "/iplayer" not in result and "/guide" not in result and "/blogs" not in result /learning_english ,/education:
                        print(result)
                        keywordArticles.append(result)
                        moreResults = True
        articles.append(keywordArticles)
    for i in range(0,len(articles)):
        print(keywords[i],len(articles[i]))
    return articles

def nyTimes(keywords):
    articles = []
    for keyword in keywords:
        url = "https://www.nytimes.com/search"
        keywordArticles = []
       
        #sortValues = ["newest","oldest","best"]
        sortValues = ["best","newest"]
        #print(values)
        #url = urllib.parse.quote(url,safe = ":=?/")
        for value in sortValues:
            values = {'query':keyword,"types":"article","startDate":"20000101","sort":value}
            data = urllib.parse.urlencode(values)
            req = urllib.request.Request(url+"?"+data)
            #print(url+"?"+data)
            resp = urllib.request.urlopen(req)
            respData = resp.read()
            #print(respData)
            
            soup = BeautifulSoup(respData,features="html.parser")
            divs = soup.find_all('div', attrs={'class': 'css-e1lvw9'})
            #links = soup.find_all('a')
            #print(links)
            for div in divs:
                links = div.find_all('a')
                for link in links:
                    result = link.get('href')
                    if "https" not in result:
                        result = "https://www.nytimes.com"+result
                    if result not in keywordArticles:
                        keywordArticles.append(result)
                        #print(result)
                    #print(result)
        articles.append(keywordArticles)
    for i in range(0,len(articles)):
        print(keywords[i],len(articles[i]))
    return articles


#Problem 2                
def problem2(articles,keywords):
    sites = ["bbc","nytimes"]
    for siteNum in range(0,len(articles)):
        #print(articles[i])
        siteName = sites[siteNum]
        directory = os.path.join(os.getcwd(),siteName)
        if os.path.exists(directory)==False:
                os.mkdir(site)
        for keyword in keywords:
            path = os.path.join(directory,keyword)
            if os.path.exists(path)==False:
                os.mkdir(path)
                
        for keywordNum in range(0,len(articles[siteNum])):
            #print(articles[i][j])
            
            keywordData = []
            articleNumber = 0
            keywordPath  = os.path.join(directory,keywords[keywordNum])
            print(keywordPath)
            for articleNum in range(0,len(articles[siteNum][keywordNum])):
                
                fileName = keywords[keywordNum]+str(articleNum)+".txt"
                print(fileName)
                filePath = os.path.join(keywordPath,fileName)
                file = open(filePath, "w",encoding='utf-8')
                #file.write(fileName+"\n")
                soup = BeautifulSoup(articles[siteNum][keywordNum][articleNum],features="html.parser")
                paragraphs = soup.find_all('p')
                #print("Paras",len(paragraphs))
                #divs = soup.findAll('div',attrs={"class":"ssrcss-3z08n3-RichTextContainer e5tfeyi2"})
                blacklist = ["Advertisement","Supported by","© 2021 BBC. The BBC is not responsible for the content of external sites.","S ILIN ","E ILIN"]
                textElements = [item for item in soup.findAll(text=True)if item.parent.name == 'p' and item not in blacklist]
                for element in textElements: 
                    #Removes unneccesary whitespace       - NYTF4          
                    toWrite = " ".join(str(element).split())+" "
                    file.write(toWrite)
                file.close()
    
#problem2([[["1","2"],["3","4"]],[["5","6"],["7","8"]]],keywords)


def problem3(keywords):
    sites = ["bbc","nytimes"]
    
    keywordVectors = []
    keywordDocuments = []
    for keyword in keywords:
        keywordVector = {}
        keywordData  = ""
        for site in sites:
            num = 1
            #fileName = os.path.join(os.getcwd(),keyword)
            fileName =  os.path.join(os.getcwd(),site,keyword,keyword+str(num)+".txt")
            while(os.path.isfile(fileName)):
                article = open(fileName,"r",encoding='utf-8')
                data = article.read()
                keywordData += data
                num += 1
                fileName = os.path.join(os.getcwd(),site,keyword,keyword+str(num)+".txt")
       # keywordVector = getVector(data)
        #keywordVectors.append(keywordVector)
        words = keywordData.split(" ")
        keywordDocuments.append(keywordData)
    
    start = time.time()
    vector = getVector(keywordDocuments,words)

   # vector = {'Details': [1, 0, 0, 0, 1, 1, 3, 0, 1, 1], 'of': [2113, 1774, 2286, 2361, 2232, 2087, 2412, 1342, 2113, 2494], 'more': [132, 168, 217, 147, 197, 153, 132, 129, 253, 197], 'than': [86, 136, 146, 113, 114, 106, 91, 98, 135, 101], '530': [0, 0, 2, 1, 0, 0, 0, 0, 2, 1], 'million': [30, 26, 48, 39, 57, 44, 42, 32, 48, 51], 'people': [188, 48, 247, 225, 141, 110, 160, 79, 137, 185], 'were': [207, 165, 280, 233, 206, 204, 195, 102, 261, 201], 'leaked': [5, 1, 3, 8, 4, 1, 7, 2, 4, 12], 'in': [5866, 4427, 7390, 6711, 6115, 5472, 6657, 3534, 6298, 6817], 'a': [26847, 20032, 31396, 29750, 28067, 24902, 28979, 15150, 29958, 30587], 'database': [0, 1, 23, 3, 5, 7, 4, 4, 10, 6], 'online,': [2, 0, 9, 2, 7, 3, 4, 1, 7, 3], 'largely': [2, 14, 2, 7, 2, 1, 2, 1, 5, 8], 'consisting': [0, 0, 0, 0, 0, 0, 0, 0, 0, 2], 'mobile': [12, 16, 17, 8, 72, 27, 28, 2, 16, 27], 'numbers.': [0, 0, 6, 0, 4, 3, 2, 3, 4, 3], 'People': [74, 23, 91, 76, 102, 67, 92, 5, 99, 90], 'can': [243, 263, 265, 379, 298, 214, 346, 169, 262, 362], 'use': [333, 267, 520, 336, 656, 530, 685, 284, 452, 721], 'the': [4526, 3734, 5074, 5161, 4820, 4203, 5162, 2340, 4801, 5421], 'online': [43, 5, 123, 41, 80, 40, 92, 39, 85, 93], 'tool': [3, 7, 20, 14, 71, 7, 75, 28, 24, 40], 'to': [2838, 2074, 3579, 3246, 3183, 2623, 3141, 1672, 2944, 3683], 'check': [5, 4, 34, 4, 30, 18, 14, 2, 8, 14], 'if': [311, 268, 388, 357, 308, 384, 326, 149, 324, 443], 'their': [224, 172, 372, 231, 337, 251, 392, 153, 386, 346], 'numbers': [5, 4, 39, 7, 21, 15, 16, 14, 24, 33], 'or': [3155, 2389, 3561, 3480, 3220, 3107, 3180, 1946, 3306, 3767], 'emails': [7, 5, 131, 5, 15, 2, 39, 3, 43, 17], 'compromised.': [0, 1, 7, 2, 5, 1, 3, 0, 11, 7], 'Facebook': [14, 10, 31, 15, 6, 1, 32, 50, 4, 133], 'says': [78, 14, 107, 90, 92, 71, 134, 24, 54, 100], 'data': [7, 46, 114, 32, 108, 72, 132, 49, 258, 272], 'is': [2584, 1804, 2925, 2939, 2366, 2182, 2825, 1122, 2281, 2719], 'from': [330, 199, 387, 371, 310, 236, 329, 178, 343, 329], 'an': [4592, 3642, 5514, 5369, 4718, 4486, 4950, 2517, 5434, 5344], '“old”': [0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 'breach': [4, 13, 29, 6, 10, 4, 22, 2, 20, 17], '2019': [4, 1, 17, 5, 3, 3, 7, 0, 14, 9], 'but': [213, 159, 219, 230, 182, 182, 184, 90, 197, 214], 'privacy': [1, 1, 9, 1, 16, 7, 89, 0, 3, 98], 'watchdogs': [1, 0, 0, 0, 1, 0, 0, 0, 1, 3], 'are': [523, 411, 788, 690, 1353, 729, 1364, 499, 1455, 810], 'now': [138, 185, 218, 205, 238, 174, 230, 114, 216, 222], 'investigating.': [0, 0, 2, 0, 1, 0, 1, 0, 6, 1], 'said': [586, 270, 548, 494, 525, 502, 437, 311, 661, 544], 'it': [2562, 2253, 3016, 2848, 3161, 2346, 2967, 1518, 3047, 3371], 'had': [266, 159, 396, 257, 279, 210, 226, 131, 345, 208], '"found': [0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 'and': [1777, 1416, 2432, 2416, 1901, 1788, 2019, 960, 2009, 2209], 'fixed"': [0, 0, 0, 0, 0, 0, 0, 0, 1, 1], 'year-and-a-half': [0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 'ago.': [4, 4, 5, 5, 4, 2, 5, 7, 6, 7], 'But': [91, 113, 103, 159, 105, 74, 134, 54, 101, 186], 'information': [18, 35, 178, 42, 95, 78, 121, 142, 93, 134], 'has': [325, 266, 270, 400, 325, 258, 395, 141, 325, 404], 'been': [342, 179, 410, 357, 435, 364, 419, 101, 524, 414], 'published': [14, 7, 10, 14, 12, 6, 15, 10, 8, 18], 'for': [790, 652, 1131, 1023, 919, 793, 951, 628, 865, 1321], 'free': [41, 20, 29, 25, 58, 18, 70, 1, 32, 40], 'hacking': [4, 31, 19, 12, 30, 11, 28, 9, 23, 11], 'forum,': [0, 0, 0, 0, 2, 0, 1, 0, 0, 1], 'making': [19, 15, 27, 20, 33, 13, 29, 22, 27, 41], 'widely': [3, 11, 1, 7, 6, 9, 9, 7, 12, 21], 'available.': [2, 0, 0, 1, 0, 3, 2, 0, 0, 6], 'The': [644, 435, 751, 686, 665, 626, 712, 306, 696, 744], 'covers': [1, 0, 7, 3, 3, 1, 1, 2, 3, 2], '533': [0, 0, 2, 1, 0, 0, 0, 0, 0, 1], '106': [0, 0, 0, 0, 1, 0, 0, 0, 0, 1], 'countries,': [7, 1, 2, 2, 6, 5, 6, 8, 12, 3], 'according': [21, 14, 25, 19, 41, 28, 34, 32, 29, 24], 'researchers': [2, 23, 10, 5, 52, 10, 23, 49, 31, 24], 'analysing': [0, 0, 0, 0, 0, 2, 2, 0, 1, 2], 'data.': [1, 4, 13, 4, 9, 10, 19, 4, 21, 26], 'That': [26, 38, 29, 36, 23, 22, 28, 44, 43, 55], 'includes': [10, 6, 10, 4, 12, 2, 12, 1, 12, 10], '11': [44, 13, 43, 43, 19, 36, 20, 9, 12, 29], 'users': [10, 6, 92, 16, 134, 62, 143, 43, 58, 128], 'UK,': [10, 3, 4, 1, 9, 7, 6, 0, 9, 9], '30': [48, 19, 124, 46, 19, 24, 19, 41, 51, 29], 'Americans': [24, 20, 8, 7, 2, 7, 2, 7, 0, 9], '7': [103, 52, 299, 133, 73, 96, 54, 36, 78, 86], 'Australians.': [0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 'Not': [23, 6, 8, 11, 8, 12, 6, 4, 15, 14], 'every': [35, 44, 70, 61, 57, 57, 63, 18, 39, 70], 'piece': [13, 3, 17, 2, 19, 14, 10, 3, 12, 14], 'available': [9, 8, 6, 13, 29, 23, 27, 6, 30, 31], 'each': [94, 78, 111, 71, 55, 70, 70, 31, 55, 67], 'user': [10, 12, 123, 18, 191, 85, 202, 52, 74, 161], '500': [6, 5, 16, 10, 6, 10, 20, 6, 15, 16], 'phone': [19, 16, 67, 26, 160, 78, 191, 28, 27, 94], 'compared': [5, 1, 6, 6, 4, 4, 1, 3, 2, 4], 'with': [424, 326, 468, 533, 362, 326, 485, 233, 399, 475], '“only': [0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 'few': [22, 35, 41, 23, 35, 25, 26, 14, 40, 15], 'email': [15, 8, 309, 16, 46, 21, 55, 7, 128, 61], 'addresses”,': [0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 'Troy': [0, 0, 0, 1, 0, 1, 0, 0, 1, 1], 'Hunt,': [0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 'security': [63, 96, 166, 60, 312, 104, 180, 134, 343, 264], 'expert': [12, 17, 36, 33, 70, 56, 42, 39, 101, 64]}
    
    print("Vector Done",time.time()-start)
    start = time.time()
    tf = termFrequency(vector,keywordDocuments)
    print("Term Freq Done",time.time()-start)
    start= time.time()
    idf = inverseDocumentFrequency(words,keywordDocuments)
    print("IDF Done",time.time()-start)

    tfidf = tf
    for word in tf.keys():
        for i in range(0,len(tf[word])):
            tfidf[word][i] *= idf[word]
            
    print(tfidf)
    start = time.time()
    similarities = getSim(tfidf,keywords)
    print("Sims done",time.time()-start)

    #print(similarities)

    workbook = xls.Workbook('distance.xlsx')
    worksheet = workbook.add_worksheet()
    worksheet.write(0,0,"Keywords")
    xPos = 0
    for i in range(0,len(keywords)):
        worksheet.write(0,i+1,keywords[i])
        worksheet.write(i+1,0,keywords[i])
        worksheet.write(i+1, i+1, 0)
    startingX = 0
    xPos = 0
    yPos = 0
    for i in range(0,len(similarities)):
        yPos += 1
        startingX += 1
        xPos = startingX
        for j in range(0,len(similarities[i])):
            xPos +=  1
            #print(similarities[i][j])
            worksheet.write(yPos, xPos, similarities[i][j])
            worksheet.write(xPos, yPos, similarities[i][j])     
    workbook.close()


def getVector(inputData,words):
    vector = {}
    for word in words:
        wordCount  = []
        for keywordData in inputData:
            wordCount.append(keywordData.count(word))
        vector[word] = wordCount
    return vector
        

def getSim(tfidf,keywords):
    similarities = []
    for i in range(0,len(keywords)-1):
        keywordSim = []
        for j in range(i+1,len(keywords)):
            top = 0
            xTotal = 0
            yTotal = 0
            for word in tfidf:
                aValue = tfidf[word][i]
                bValue = tfidf[word][j]
                top += aValue * bValue
                xTotal += aValue **2
                yTotal += bValue **2
            xTotal = math.sqrt(xTotal)
            yTotal = math.sqrt(yTotal)
            similarity = 1-( top/(xTotal*yTotal))
            keywordSim.append(similarity)
        similarities.append(keywordSim)
    return similarities
    
        
def pearsonSimilarity(tf,keywords):
    tfList = list(tf.values())
    similarities = []
    for i in range(0,len(keywords)-1):
        keywordSim = []
        for j in range(i+1,len(keywords)):
            xMean = np.mean(np.array(tfList)[:,i])
            yMean = np.mean(np.array(tfList)[:,j])
            numer = np.sum((np.array(tfList)[:,i]-xMean)*(np.array(tfList)[:,j]-yMean))
            xBottom = np.array(tfList)[:,i]-xMean
            yBottom= np.array(tfList)[:,j]-yMean
            #print("X",x)
            denom = np.sqrt( (np.sum(xBottom**2) ) ) *  np.sqrt(np.sum(yBottom**2) )
            keywordSim.append((numer/denom))
        similarities.append(keywordSim)
    return similarities


def termFrequency(vector,inputData):
    lengths = [len(document.split(" ")) for document in inputData]
    for word in vector:
        for i in range(0,len(vector[word])):
           vector[word][i] = math.log(1+vector[word][i])
    return vector


def inverseDocumentFrequency(dictionary, documents):
    idf = {}
    for word in dictionary:
        idf[word] = 0
        for document in documents:
            if word in document:
                idf[word] += 1
        idf[word] = math.log(len(documents)/idf[word])
    return idf

def problem4():
    data = pd.read_excel('distance.xlsx',header = 0,index_col=0)
    cols = list(data.values)
    values = []
    for col in cols:
        values.extend(col)
    seaborn.set_theme()
    seaborn.color_palette("crest", as_cmap=True)

   # heatmap1  = seaborn.heatmap(data,vmin = min(values),vmax = max(values),annot=True,cmap = 'viridis');
   # heatmap1 =heatmap1.get_figure()
    #heatmap1.show()
    createOther(data)

def createOther(data):
    seaborn.set_theme()
    seaborn.color_palette("crest", as_cmap=True)
    heatmap2  = seaborn.heatmap(data,vmin = 0,vmax =1,annot=True,cmap = 'viridis');
    heatmap2 =heatmap2.get_figure()
    heatmap2.show()

    

#articleData,keywords = problem1()
#print("done")
#problem2(articleData, keywords)
#print("done2"
problem3(keywords)   
problem4()
##articleData,keywords = problem1()
##print("done1")
##problem2(articleData, keywords)
