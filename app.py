from flask import Flask
import mainHelpers

app = Flask(__name__)

@app.route('/')
def hello():
    return "<p>hello</p>"

@app.route('/query/<query>')
def deal_with_query(query):
    p, wikiRet, schDf = mainHelpers.initMain()
    resp = mainHelpers.handleQuery(query, p, schDf, wikiRet)
    print('Q: ', query)
    print('A: ', resp)
        
    return resp

# if __name__ == '__main__':
#     app.run(host='192.168.43.3', port=5000)