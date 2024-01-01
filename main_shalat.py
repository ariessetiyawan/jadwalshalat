import logging
from datetime import datetime
from datetime import timedelta, date
import time
import sys,os,io,glob

#pyinstaller -F -y -w api_ddk.py --key=bismill4h -i check.ico
filename= (sys.argv[0])
head =os.path.split(filename)
if os.path.isdir(head[0]):
    fllog=os.path.join(head[0],"main_shalat.log")
else:
    fllog=os.path.join(os.path.abspath(os.getcwd()),"main_shalat.log")
try:
    logging.basicConfig(filemode='w',level=logging.ERROR,filename=fllog, format='%(asctime)s - %(message)s',datefmt='%m/%d/%Y %I:%M:%S %p')
except Exception as e: 
    logging.error(e,exc_info=True)
    #os.chdir('/tmp')
    fllog=('./main_shalat.log')
    logging.basicConfig(filemode='w',level=logging.ERROR,filename=fllog, format='%(asctime)s - %(message)s',datefmt='%m/%d/%Y %I:%M:%S %p')
    pass

try:
	from jadwalshalat import *
	from flask import Flask, redirect, url_for, request,jsonify,make_response,render_template,send_from_directory
	from flask_cors import CORS, cross_origin
	from flask_socketio import SocketIO, emit
except Exception as e: 
	logging.error(e,exc_info=True)
	sys.exit()
	

jadwal = Sholat()
api_v2_cors_config = {
  "origins": ["*"],
  "methods": ["OPTIONS", "GET", "POST"],
  "allow_headers": ["Authorization", "Content-Type"]
}    
app = Flask(__name__)
dir_path = os.path.dirname(os.path.realpath(__file__))	
app = Flask(__name__,root_path=dir_path,static_url_path = "/data", static_folder = "/data/downloads",template_folder="templates",)
app.config['SECRET_KEY'] = 'ariessetiyawan!'
CORS(app, resources={"/*": api_v2_cors_config})
socketio = SocketIO(app)

@app.route('/')
@cross_origin()
def index():
    return render_template('index.html')
	
@app.route('/jadwalshalat/<kabko>/<tgl>')
@cross_origin()
def do_jadwalshalat(kabko,tgl):
	kotas = jadwal.cari_kabupaten(kabko)
	tgl=tgl.split('-')
	data={}
	for key in kotas:
		data=jadwal.sehari(key,tgl[0],tgl[1],tgl[2])
		if len(kotas)>1:
			break
	return data

@socketio.event
def my_event(message):
    emit('my response', {'data': 'got it!'})

if __name__ == '__main__':
     socketio.run(app, host="0.0.0.0",port=8003,debug=True)
