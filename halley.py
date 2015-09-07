from daemon import Daemon
import http.client, urllib, hmac, hashlib, re, serial, time

class Halley(Daemon):
  """Monitors serial port (23b Open Access Board) for authorizations and triggers"""
  
  version = '0.0.1a'
  serial_path = '/dev/ttyUSB0'
  timeout = 5
  baudrate = 9600
  
  
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
      pass

  def send_output(self, output):
    print("Sending output")
    resp = self.notify('output', {'output': output})
    print(resp.read())
    return resp.status == 200

  def run(self):
    self.bootup()
    
    ser = serial.Serial(Halley.serial_path, Halley.baudrate, timeout=Halley.timeout)
    output = None
    
    while True:
      line = ser.readline()
      if output == None
        output = line
      else
        output += line
      
      # A line length of 0 means we reached the timeout, so send output if there is any buffered
      if output != None and len(len) == 0 and len(output) > 0
        if self.send_output(output)
          output = None
      
    
    
