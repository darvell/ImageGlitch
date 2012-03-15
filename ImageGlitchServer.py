import os
from flask import Flask, request, redirect, url_for,send_from_directory,render_template
from werkzeug import secure_filename
import datamosh
import urllib
import random

UPLOAD_FOLDER = datamosh.CurrentDirectory()
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.debug = True

def allowed_file(filename):
  return '.' in filename and \
       filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/uploads/<filename>')
def uploaded_file(filename):
  return send_from_directory(app.config['UPLOAD_FOLDER'],filename)


@app.route('/', methods=['GET', 'POST'])
def upload_file():
  if request.method == 'POST':
    # Not actually possible at the moment...
    if 'files' in request.files.keys():
      file = request.files['file']
    else:
      file = False
    chance = random.randint(50,90)
    length = random.randint(1,20)
    seed = random.randint(0,420)
    huff = False
    if request.form.get('chance'):
      chance = int(request.form.get('chance'))
    if request.form.get('seed'):
      seed = int(request.form.get('seed'))
    if request.form.get('datalength'):
      length = int(request.form.get('datalength'))
    if request.form.get('huff'):
      if request.form.get('huff') == "true":
        huff = True

    if chance > 98 or length > 20:
      return 'HACKER'
    
    if str(request.form.get('url')) != "":
        url = request.form.get('url')
        webFile = urllib.urlopen(url)
        localFile = open(UPLOAD_FOLDER + secure_filename(url.split('/')[-1]), 'wb')
        if url.split('/')[-1][len(url.split('/')[-1]) - 3:len(url.split('/')[-1])] not in ALLOWED_EXTENSIONS:
          return 'invalid.png'
        localFile.write(webFile.read())
        webFile.close()
        localFile.close()
        result = datamosh.ProcessImage(secure_filename(url.split('/')[-1]),chance,length,3,seed,huff)
        return result
    if file and allowed_file(file.filename):
      filename = secure_filename(file.filename)
      file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
      result = datamosh.ProcessImage(filename,float(chance),length,3,seed,huff)
      return result
  return render_template('index.html')

if __name__ == '__main__':
  app.run()