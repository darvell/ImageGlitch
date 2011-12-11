import os
from flask import Flask, request, redirect, url_for,send_from_directory
from werkzeug import secure_filename
import datamosh
import urllib

UPLOAD_FOLDER = str(os.getcwd())
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
    file = request.files['file']
    chance = 70
    length = 4
    seed = 420
    try:
      chance = int(request.form.get('chance'))
      length = int(request.form.get('datalength'))
      seed = int(request.form.get('randseed'))
    except:
      pass
      
    if chance > 98 or length > 10:
      return 'idiot dont exceed the values'
    
    if str(request.form.get('url')) != "":
        url = request.form.get('url')
        webFile = urllib.urlopen(url)
        localFile = open(secure_filename(url.split('/')[-1]), 'wb')
        if url.split('/')[-1][len(url.split('/')[-1]) - 3:len(url.split('/')[-1])] not in ALLOWED_EXTENSIONS:
          return 'Invalid remote image.'
        localFile.write(webFile.read())
        webFile.close()
        localFile.close()
        result = datamosh.ProcessImage(secure_filename(url.split('/')[-1]),chance,length,30,seed)
        if result == 'CANTGLITCH':
           return 'Your paramaters are terrible, I can\'t glitch this and keep the file valid.'
        if result == 'INVALID':
           return 'This file is not considered valid. Why? Who cares.'
        else:
           return redirect(url_for('uploaded_file',filename=result))




    if file and allowed_file(file.filename):
      filename = secure_filename(file.filename)
      file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
      result = datamosh.ProcessImage(filename,float(chance),length,30,seed)
      if result == 'CANTGLITCH':
        return 'Your paramaters are terrible, I can\'t glitch this and keep the file valid.'
      if result == 'INVALID':
        return 'This file is not considered valid. Why? Who cares.'
      else:
           return redirect(url_for('uploaded_file',filename=result))
  

  
  return '''
  <!doctype html>
  <title>Image Glitch</title>
  <h1>Upload a file idiot</h1>
  <form action="" method=post enctype=multipart/form-data>
    <p>File: <input type=file name=file><br>
    Or URL: <input type=text name=url><br>
       <br>Percent chance of corrupting data (Max: 98%)<input type=text name=chance>
       <br>Max amount of data to write (Max 10):<input type=text name=datalength> <br>
    Seed value (use a number): <input type=text name=randseed><br>
     <input type=submit value=Upload>
     <br> Good params are 75-90% chance and 4 data write.
  </form>
  '''



if __name__ == '__main__':
  app.run()