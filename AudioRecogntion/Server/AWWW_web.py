# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 17:18:16 2016
@author: winpython
"""

import os
from flask import Flask, request, send_file, send_from_directory, session
from werkzeug import secure_filename
# belows include self-define libs and func
#from AWWW_wav_to_spectro import wav2sep
from AWWW_wav_to_STT import input_filename
from AWWW_jiebaCut import func_cut
from AWWW_chatbot_response import Chat_with_Bot
#from AWWW_pic_pred import pred
#from file_del import pred_del
from flask import jsonify


# aboves include self-define libs and func
import numpy as np
import json

#ans_test = pred_test()

#from chatbot import chatbot
#AkishinoProjectBot = chatbot.Chatbot()
#AkishinoProjectBot.main(['--modelTag', 'taiwa20170709', '--test', 'daemon'])


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = set(['wave', 'wav'])




def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@app.route("/", methods=['get', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
         
        if file and allowed_file(file.filename):
#            print(file)
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # return redirect(url_for('uploaded_file',filename = filename))

            """wav2sep(filename)
            ans = pred()

            # below decode json from nvidia digits output
            jsondec = json.loads(ans.decode('utf8'))
            jsondec = jsondec['predictions']
            jsondec = str(jsondec).replace("[", "")
            jsondec = str(jsondec).replace("]", "")
            jsondec = "{" + jsondec + "}"
            jsondec = jsondec.replace("',", "':")
            jsondec = jsondec.replace("'", '"')
            jsondec = json.loads(jsondec)  
            respred = ((jsondec['happy'], jsondec['sad'], jsondec['calm'], jsondec['fearful'], jsondec['angry']))

            maxpred = (max(jsondec['happy'], jsondec['sad'], jsondec['calm'], jsondec['fearful'], jsondec['angry']))

            if maxpred == jsondec['happy']:
                print("開心 : " + str(jsondec['happy']))
            elif maxpred == jsondec['sad']:
                print("傷心 : " + str(jsondec['sad']))
            elif maxpred == jsondec['calm']:
                print("平靜 : " + str(jsondec['calm']))
            elif maxpred == jsondec['fearful']:
                print("害怕 : " + str(jsondec['fearful']))                
            elif maxpred == jsondec['angry']:
                print("生氣 : " + str(jsondec['angry']))
            else:
                print("無法辨識")"""



            from chatbot import chatbot
            AkishinoProjectBot = chatbot.Chatbot()
            
            """if maxpred == (jsondec['happy']):
                AkishinoProjectBot.main(['--modelTag', 'positive_negative_correct', '--test', 'daemon'])
            elif maxpred == jsondec['sad']:
                AkishinoProjectBot.main(['--modelTag', 'positive_negative_correct', '--test', 'daemon'])
            elif maxpred == jsondec['calm']:
                AkishinoProjectBot.main(['--modelTag', 'positive_negative_correct', '--test', 'daemon'])
            elif maxpred == jsondec['fearful']:
                AkishinoProjectBot.main(['--modelTag', 'positive_negative_correct', '--test', 'daemon'])
            elif maxpred == jsondec['angry']:
                AkishinoProjectBot.main(['--modelTag', 'positive_negative_correct', '--test', 'daemon'])
            else:
                print("無法辨識")"""
            AkishinoProjectBot.main(['--modelTag', 'model-AIA', '--test', 'daemon'])
            asking = str(input_filename(filename))
            print("asking = " + asking)
            if  asking == "None":
                #responsing = Chat_with_Bot(asking, AkishinoProjectBot)
                asking = "無法辨識"
                print("chatbot_responsing asking = " + asking)
            else:   
                asking = func_cut(input_filename(filename))
                responsing = Chat_with_Bot(asking, AkishinoProjectBot)
                print("chatbot_responsing asking_res = " + responsing)                
                if responsing == "":
                   responsing = "無法回應"
                   print("responsing = " + responsing)
            #asking = str(input_filename(filename))
            print("asking = " + asking)

            #ans_del = pred_del(filename)
               
                
			
            json_res = [{
                '1_ask': asking,
                '2_response': responsing
            }]   
            #print("maxpred = " + str(maxpred[0]))
	        #shutdown web server   
            shutdown()

            #print(ans.decode('utf8').replace("\n"," "))
            #return str(maxpred[0])
            #reload = restart()

            return jsonify(json_res)
            #return (ans.decode('utf8') + "|" +"ask = "+ asking_res + "," + "response = "+ responsing)
            
            return ("ask = "+ asking + "," + "response = "+ responsing)

    return'''
    <doctype html>
    <title>test upload</title>
    <h1>Upload NoTag</h1>
    <form action="" method="post" enctype=multipart/form-data>
        <p><input type=file name=file>
           <input type=submit name=upload></p>
    </form>
    '''


def shutdown():
    shutdown_server()
    print("Server shutting down...")
    return 'Server shutting down...'



@app.route("/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)



if __name__ == "__main__" :
    app.run(host='0.0.0.0',port=5050)
