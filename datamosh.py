import Image
import os
import random
import shutil
import time
import math
import encodings
import sys
import glob

# todo: proper differentiate
def CurrentDirectory():
  if os.name == "nt":
    return str(os.getcwd()) + '\\static\\glitch\\'
  else:
    return str(os.getcwd()) + '/static/glitch/'

def CorruptImage(filename,chance,maxlen,seed,huff=False):
  if huff:
    CorruptHuffman(filename)
  else:
    with open(CurrentDirectory() + filename,"r+b") as f:
      filesize = os.path.getsize(CurrentDirectory() + filename) - 1
      i = math.floor(filesize / 100) * 5
      random.seed(seed)
      while i < filesize:
        f.seek(i)
        if random.randint(0,100) < chance:
          for j in range(1,random.randint(1,maxlen)):
            f.write(hex(random.randint(0,255)))
            f.seek(i + j)
        i += random.randint(1,300)

def CorruptHuffman(filename):
  with open(CurrentDirectory() + filename,"r+b") as f:
    filesize = os.path.getsize(CurrentDirectory() + filename)
    huffmanStart = 0
    huffmanEnd = 0
    found = 0

    for i in range(0,filesize):
      if found == 2:
        break
      f.seek(i)
      if f.read(1) == '\xFF':
        f.seek(i + 1)
        if f.read(1) == '\xC4':
          # Ok, we found a single huffman table, that's good!
          # Let's go hunt for the end of it.
          huffmanStart = i + 2
          found += 1
    
    found = False
    
    for i in range(huffmanStart + 2,filesize):
      if found == True:
        break
      f.seek(i)
      if f.read(1) == '\xFF':
        f.seek(i + 1)
        if f.read(1) != '\x00':
          huffmanEnd = i - 2
          found = True
    
    f.seek(random.randint(huffmanStart,huffmanEnd))
    f.write(hex(random.randint(1,250)))

def ValidFileCheck(filename):
  try:
    file = Image.open(CurrentDirectory() + filename)
    # Sometimes it can open an image but it can't save it. We double check as a result.
    file.save(CurrentDirectory() + filename[:-4] + '.temp.jpg')
    os.remove(CurrentDirectory() + filename[:-4] + '.temp.jpg')
    return True
  except:
    return False

def CleanUp(filename,glitch):
  os.remove(CurrentDirectory() + glitch)
  for filename in glob.glob(CurrentDirectory() + filename[:-4] + '.*'):
    os.remove(filename)
  date_file_list = []
  for file in glob.glob(CurrentDirectory() + '*.jpg'):
      stats = os.stat(file)
      lastmod_date = time.localtime(stats[8])
      date_file_tuple = lastmod_date, file
      date_file_list.append(date_file_tuple)
  date_file_list.sort()
  if len(date_file_list) > 100:
    for i in range(100,len(date_file_list)):
      try:
        os.remove(date_file_list[0][1])
      except:
        pass

def ProcessImage(filename,chance,maxlen,maxFailedGlitches,seed,huff=False):
  failedglitches = 0
  random.seed(seed)

  # Dump to BMP then back to JPG, good way to strip EXIF data and whatnot.
  # Helps make corruption not so awful.
  try:
    tempImg = Image.open(CurrentDirectory() + filename)
    tempImg.convert("RGB").save(CurrentDirectory() + filename[:-4] + '.bmp')
    tempImg = Image.open(CurrentDirectory() + filename[:-4] + '.bmp')
    tempImg.convert("RGB").save(CurrentDirectory() + filename[:-4] + '.jpg')
    os.remove(CurrentDirectory() + filename[:-4] + '.bmp')
    filename = filename[:-4] + '.jpg'
  except:
    return 'invalid.png'

  
  if ValidFileCheck(filename):
    glitchFileName = filename[:-4] + '-working.jpg'
    shutil.copy(CurrentDirectory() + filename,CurrentDirectory() + glitchFileName)
    CorruptImage(glitchFileName,chance,maxlen,seed,huff)
    
    # If it's too corrupt to be handled by PIL, we just start brute forcing.
    if ValidFileCheck(glitchFileName) == False:
      while (ValidFileCheck(glitchFileName) == False) and (failedglitches != maxFailedGlitches):
        # Sleep before/after remove, failure to causes a weird permissions bug in windows sometimes
        # Can't work out why!
        time.sleep(0.2)
        os.remove(CurrentDirectory() + glitchFileName)
        time.sleep(0.2)
        shutil.copy(CurrentDirectory() + filename,CurrentDirectory() + glitchFileName)
        CorruptImage(glitchFileName,chance,maxlen,seed,huff)
        failedglitches += 1
    
    if failedglitches != maxFailedGlitches:
      if huff:
        finalFileName = filename[:-4] + '-huff-' + str(seed) + '.jpg'
      else: 
        finalFileName = filename[:-4] + '-' + str(chance) + '-' + str(maxlen) + '-' + str(seed) +  '.jpg'
      imaeg = Image.open(CurrentDirectory() + glitchFileName)
      imaeg.save(CurrentDirectory() + finalFileName)
      CleanUp(filename,glitchFileName)
      return finalFileName
    else:
      os.remove(CurrentDirectory() + glitchFileName)
      os.remove(CurrentDirectory() + filename)
      return 'cantglitch.png'
  else:
    os.remove(CurrentDirectory() + filename)  
    return 'invalid.png'