from flask import Flask, Response

app = Flask(__name__)

count = 0
@app.route('/no_retries', methods=['POST','GET'])
def good_api():
    return Response(status=200)

@app.route('/2_retries', methods=['POST', 'GET'])
def two_retry():
    global count
    print(count)
    if(count<2):
        count += 1
        return Response(status=403)
    return Response(status=200)

@app.route('/reset', methods = ['GET'])
def reset():
    global count
    count = 0
    return str(count)

@app.route('/null', methods = ['POST'])
def null():
    return Response(None)

if __name__=='__main__':
    app.run(debug=True)