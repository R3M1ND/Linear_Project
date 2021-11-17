from os import error, replace
from flask import Flask, render_template,request,redirect,flash,url_for
from flask.helpers import url_for
from SearchEngine import SearchEngine
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mykey'
se = SearchEngine("zen_record.txt")


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
        x = se.search_by_keyword(keyword = search, return_value ='Quote',number_of_result = 20)    
        if x[1] != [] :
            flash("no result for '{}'".format(search))

    return render_template('rankweb.html',search = search,kw = x , enumerate = enumerate , len = len)

if __name__ == '__main__':  
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
    #app.run()
