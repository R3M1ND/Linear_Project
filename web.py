from flask import Flask, render_template,request,redirect,flash,url_for
from flask.helpers import url_for
from SearchEngine import SearchEngine
import numpy as np
from nltk.corpus import wordnet
import math
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mykey'
se = SearchEngine("zen_record.txt")


def bubbleSort(arr,lstStr):
    n = len(arr)
    for i in range(n-1):
        for j in range(0, n-i-1):
            if arr[j] < arr[j + 1] :
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                lstStr[j], lstStr[j + 1] = lstStr[j + 1], lstStr[j]
    return arr,lstStr
#---------------------------------------------------------------------
@app.route('/')
def Home():
    return render_template('web.html')
@app.route('/my-link/')
def my_link():
    return render_template('rankweb.html')
@app.route('/searchengine',methods = ['POST',"GET"])
def search():
    if request.form['search'] :
        output = request.form.to_dict()
        search = output["search"]
        x = se.search_by_keyword(keyword = search, return_value ='Quote',number_of_result = 10)    
        if x[1][0] == 1 :
            flash("no result for ' {} '".format(search))
        lemmakw = se.parse_words(search)
        matrixA=[]
        print(lemmakw[0],type(lemmakw[0]))
        for i,data in enumerate(x[0]):
            print(i+1,data.replace(search,"'"+search+"'"))
            if lemmakw[0] in data:    
                matrixA.append(data)
            if x[1]!=[]:
                #x[1] is list
                #x[1][0] is word in list 
                if str(x[1][0]) in data:
                    matrixA.append(data)
        print('this x1 0',x[1][0])
        print('this x1 1',x[1][1])
        tempkw = x[1][1]
        print('---------------------------------------------------')
        #find synonyms
        synonyms = []
        #kwSyn == keyword Synonyms
        kwSyn=x[1][1]
        for syn in wordnet.synsets(kwSyn):
            for l in syn.lemmas():
                synonyms.append(l.name())
        print(f"we search synonyms for word : {kwSyn}")
        setSyn = set(synonyms)
        if kwSyn in synonyms:
            setSyn.remove(kwSyn)
        print(setSyn)
        print('synonyms',synonyms)
        print('set :',setSyn)
        lstSyn = list(setSyn)

        #lst synonym len
        wordSyn=[]
        lstlenSyn=[]
        for word in lstSyn:
            matrixB=[]
            x = se.search_by_keyword(keyword=word, return_value ='Quote',number_of_result = 10)
            for i,data in enumerate(x[0]):
                
                if word in data:    
                    matrixB.append(data)
                    if word not in wordSyn:
                        wordSyn.append(word)
                    
                    #print(matrixB)
            lstlenSyn.append(len(matrixB))
        #wordSyn=set(wordSyn)
        #print(wordSyn)
        lstlenSyn = [i for i in lstlenSyn if i != 0]
        #print(lstlenSyn)
        pagerankWord=wordSyn
        pagerankLen=lstlenSyn
        print('pagerankWord :',pagerankWord)
        print('pagerankLen :',pagerankLen)
        # #matrix zone

        # print('Matrix A =',matrixA,'len:',len(matrixA))

        # #Method : multiply matrix A and r
        # a = np.array([[0, 2/3, 1/3],
        #               [1/2, 0, 1/2],
        #               [0, 1/2, 1/2]])
        # b = np.array([[1/3, 1/3, 1/3]])
        # #iter multiply 19 round
        # for i in range(5):
        #     b=np.matmul(b, a)
        #     print(f'round {i}',b)
        # ans=[]
        # for i in range(3):
        #     ans.append(b[0,i])

        # print(ans)

        lstnum,lst=bubbleSort(pagerankLen,pagerankWord)
        print(lstnum,lst)
        #dimension == n
        n=len(lstnum)
        col=0
        lstOrder=[]
        A=np.array([])

        #find diagonal 
        lstDiagonal=[]
        #find diagonal index
        for i in range(1,n+1):
            #Formula : (a1 * (dimension+1))-(dimension)
            indexDiagonal=(i*(n+1))-(n)
            lstDiagonal.append(indexDiagonal)
        print('lst Diagonal',lstDiagonal)
        indexmat =0
        for i in range(n):
            link1=math.floor(lstnum[i]*(2/3))
            link2=lstnum[i]-link1
            #add fraction to link1 and link2
            link1=link1/lstnum[i]
            link2=link2/lstnum[i]
            lstlink=[]
            #if this node is last index
                #link1
            if i+1==n:
                #link1
                lstlink.append(0)
                #link2
                lstlink.append(1)
            #if this node is second last
            elif i+2==n:
                lstlink.append(i+1)
                #link2
                lstlink.append(0)
            #if this node is pass every condition
            else:
                lstlink.append(i+1)
                lstlink.append(i+2)
            print(lstlink)
            for j in range(n):
                #== diagonal
                if j == col:
                    lstOrder.append(0)
                    A=np.append(A,[0])
                elif j == lstlink[0]:
                    A=np.append(A,[link1])
                elif j == lstlink[1]:
                    A=np.append(A,[link2])
                else:
                    A=np.append(A,[0])
                indexmat+=1
            col+=1

        A=np.reshape(A,(n,n),order="f")
        print(A)

        print('len:',len(A),'Matrix A =')
        print(A)
        A=np.transpose(A)
        print("Tranpose A:")
        print(A)
        #Method : multiply matrix A and r

        '''a = np.array([[0, 2/3, 1/3],
                    [1/2, 0, 1/2],
                    [0, 1/2, 1/2]])
        '''
        r=np.array([])
        for i in range(n):
            initialV = 1/n 
            r = np.append(r,[initialV])
        print('initial vector :',r)
        #iter multiply 19 round
        for i in range(20):
            r=np.matmul(r, A)
            print(f'round {i}',r)
        ans=[]
        for i in range(n):
            ans.append(r[i])
        print(ans)

        pagerankLen,pagerankWord=bubbleSort(ans,pagerankWord)
        print(pagerankLen)
        print(pagerankWord)

        #loop Return list
        #we add keyword in first wordPage 
        wordPage=[tempkw]
        for i in pagerankWord:
            wordPage.append(i)
        result=[]
        for word in wordPage:
            x = se.search_by_keyword(keyword=word, return_value ='Quote',number_of_result = 10)
            for i,data in enumerate(x[0]):
                
                if word in data:    
                    #matrixB.append(data)
                    result.append(data)       

    return render_template('rankweb.html',search = search,kw = result[:20] ,len = len ,pagerankWord = pagerankWord,tempkw = tempkw)

if __name__ == '__main__':  
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
    #app.run()
