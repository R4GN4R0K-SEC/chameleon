__G__ = "(G)bd249ce4"

from http.server import HTTPServer, SimpleHTTPRequestHandler
from random import choice
from cgi import FieldStorage
from multiprocessing import Process
from time import sleep
from requests import get,post
from psutil import process_iter
from signal import SIGTERM 
from time import sleep
from logging import DEBUG, Handler, WARNING, getLogger,basicConfig

class QHTTPServer():
	def __init__(self,ip=None,port=None,username=None,password=None,mocking=False,logs=None):
		self.ip= ip or '0.0.0.0'
		self.port = port or 80
		self.username = username or "test"
		self.password = password or "test"
		self.mocking = mocking or None
		self.random_servers = ['Apache','nginx','Microsoft-IIS/7.5','Microsoft-HTTPAPI/2.0','Apache/2.2.15','SmartXFilter','Microsoft-IIS/8.5','Apache/2.4.6','Apache-Coyote/1.1','Microsoft-IIS/7.0','Apache/2.4.18','AkamaiGHost','Apache/2.2.25','Microsoft-IIS/10.0','Apache/2.2.3','nginx/1.12.1','Apache/2.4.29','cloudflare','Apache/2.2.22']
		self.setup_logger(logs)

	def setup_logger(self,logs):
		self.logs = getLogger("chameleonlogger")
		self.logs.setLevel(DEBUG)
		if logs:
			from custom_logging import CustomHandler
			self.logs.addHandler(CustomHandler(logs))
		else:
			basicConfig()

	def AddUserAndPassAndMock(self):
		_q_s = self

		class CustomSimpleHTTPRequestHandler(SimpleHTTPRequestHandler):
			if isinstance(_q_s.mocking, bool):
				if _q_s.mocking == True:
					SimpleHTTPRequestHandler.server_version = choice(_q_s.random_servers)
					SimpleHTTPRequestHandler.sys_version = ""
			elif isinstance(_q_s.mocking, str):
				SimpleHTTPRequestHandler.server_version = _q_s.mocking
				SimpleHTTPRequestHandler.sys_version = ""

			def do_GET(self):
				_q_s.logs.info(["servers",{'server':'http_server','action':'get','ip':self.client_address[0],'port':self.client_address[1]}])
				if _q_s.username != '' and _q_s.password != '':
					self.path = '/modules/templates/login.html'
				else:
					self.path = '/modules/templates/home.html'				
				return SimpleHTTPRequestHandler.do_GET(self)

			def do_POST(self):
				_q_s.logs.info(["servers",{'server':'http_server','action':'post','ip':self.client_address[0],'port':self.client_address[1]}])
				if _q_s.username != '' and _q_s.password != '':
					form = FieldStorage(fp=self.rfile,headers=self.headers,environ={'REQUEST_METHOD':'POST','CONTENT_TYPE':self.headers['Content-Type'],})
					if 'username' in form and 'password' in form:
						if form['username'].value == _q_s.username and form['password'].value == _q_s.password:
							_q_s.logs.info(["servers",{'server':'http_server','action':'login','status':'success','ip':self.client_address[0],'port':self.client_address[1],'username':_q_s.username,'password':_q_s.password}])
						else:
							_q_s.logs.info(["servers",{'server':'http_server','action':'login','status':'failed','ip':self.client_address[0],'port':self.client_address[1],'username':form['username'].value,'password':form['password'].value}])
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				self.wfile.write(b'<html><body></body></html>')

			def send_error(self, code, message=None):
				_q_s.logs.error(["errors",{'server':'http_server','action':'error','ip':self.client_address[0],'port':self.client_address[1]}])
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				self.wfile.write(b'<html><body></body></html>')


			def handle(self):
				try:
					SimpleHTTPRequestHandler.handle(self)
				except Exception as e:
					_q_s.logs.error(["errors",{'server':'http_server','error':'handle',"type":"error -> "+repr(e)}])

		return CustomSimpleHTTPRequestHandler

	def http_server_main(self):
		server = HTTPServer((self.ip, self.port), self.AddUserAndPassAndMock())
		server.serve_forever()

	def run_server(self,process=False):
		self.close_port()
		if process:
			self.http_server = Process(name='QHTTPServer', target=self.http_server_main)
			self.http_server.start()
		else:
			self.http_server_main()

	def kill_server(self,process=False):
		self.close_port()
		if process:
			self.http_server.terminate()
			self.http_server.join()

	def test_server(self,ip,port,username,password):
		try:
			sleep(2)
			_ip = ip or self.ip
			_port = port or self.port
			_username = username or self.username
			_password = password or self.password
			get('http://{}:{}'.format(_ip,_port))
			post('http://{}:{}'.format(_ip,_port),data={'username': (None, _username),'password': (None, _password)})
		except:
			pass

	def close_port(self):
		for process in process_iter():
			try:
				for conn in process.connections(kind='inet'):
					if self.port == conn.laddr.port:
						process.send_signal(SIGTERM)
						process.kill()
			except:
				pass

if __name__ == "__main__":
	from server_options import server_arguments
	parsed = server_arguments()

	if parsed.docker or parsed.aws or parsed.custom:
		qhttpserver = QHTTPServer(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password,mocking=parsed.mocking,logs=parsed.logs)
		qhttpserver.run_server()

	if parsed.test:
		qhttpserver = QHTTPServer(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password,mocking=parsed.mocking,logs=parsed.logs)
		qhttpserver.test_server(ip=parsed.ip,port=parsed.port,username=parsed.username,password=parsed.password)
