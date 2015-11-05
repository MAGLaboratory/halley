from daemon import Daemon
import http.client, urllib, hmac, hashlib, re, serial, time, subprocess, json

class Halley(Daemon):
  """Monitors serial port (23b Open Access Board) for authorizations and triggers"""
  
  version = '0.0.2'
  serial_path = '/dev/ttyUSB0'
  timeout = 5
  baudrate = 9600
  host = 'www.maglaboratory.org'
  use_ssl = True
  secret_path = '/home/halley/.open-sesame'
  
  
  def get_secret(self):
    if len(self.secret) <= 0:
      file = open(Halley.secret_path, 'rb')
      self.secret = file.read()
      file.close
    
    return self.secret
  
  def notify_hash(self, body):
    hasher = hmac.new(self.get_secret(), body, hashlib.sha256)
    hasher.update(self.session)
    return hasher.hexdigest()
  
  def notify(self, path, params):
    # TODO: Check https certificate
    params['time'] = time.time()
    body = urllib.parse.urlencode(params).encode('utf-8')

    headers = {"Content-Type": "application/x-www-form-urlencoded",
      "Accept": "text/plain",
      "X-Haldor": Halley.version,
      "X-Session": self.session,
      "X-Checksum": self.notify_hash(body)
      }
    conn = None
    if Halley.use_ssl:
      conn = http.client.HTTPSConnection(Halley.host)
    else:
      conn = http.client.HTTPConnection(Halley.host)

    conn.request("POST", "/halley/{0}".format(path), body, headers)
    print("Notified {0}".format(path))
    return conn.getresponse()
    

  def bootup(self):
    print("Bootup.")
    self.secret = ""
    self.session = "".encode('utf-8')
    self.notify_bootup()
    

  def notify_bootup(self):
    df = ""
  
    print("Bootup:")
    
    try:
      df = subprocess.check_output("df")
    except:
      print("\tcan't call df")
    
    try:
      resp = self.notify('bootup', {'df': df})
      self.session = resp.read()
      print("Bootup Complete: {0}".format(self.session))
    except:
      # TODO: Error handling
      print("Bootup ERROR")

  def send_output(self, output):
    print("Sending output")
    resp = self.notify('output', {'output': output})
    restxt = resp.read()
    if(restxt.startswith('{') and restxt.endswith('}')):
      self.syncAction(restxt)
    return resp.status == 200

  def syncAction(self, restxt):
    try:
      actions = json.loads(restxt)
      if(actions['keyholders']):
        self.sync_keyholders(actions['keyholders'])
    except:
      print('Sync failed')
    

  def sync_keyholders(self, keyholders):
    # TODO

  def run(self):
    self.bootup()
    
    ser = serial.Serial(Halley.serial_path, Halley.baudrate, timeout=Halley.timeout)
    output = None
    
    while True:
      line = ser.readline()
      if(None == output):
        output = line
      else:
        output += line
      
      # A line length of 0 means we reached the timeout, so send output if there is any buffered
      if(output != None and ((len(line) == 0 and len(output) > 0) or (len(output) > 10000))):
        if(self.send_output(output)):
          output = None
      
    
    
