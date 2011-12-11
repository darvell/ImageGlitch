import Image
import os
import random
import shutil
import time

# todo: proper differentiate
def CurrentDirectory():
  if os.name == "nt":
    return str(os.getcwd()) + '\\'
  else:
    return str(os.getcwd()) + '/'

def CorruptImage(filename,chance,maxlen):
  with open(filename,"r+b") as f:
    filesize = os.path.getsize(filename)
    #start at 10% in so we dont mess with the header, seems to work well.
    start = (filesize / 100) * 10
    end = (filesize / 100) * 95
    for i in range(start,end):
      if(random.randint(0,chance) == 1):
        f.seek(i)
        for i in range(0,random.randint(1,maxlen)):
          f.write(hex(random.randint(0,255)))


def ValidFileCheck(filename):
  try:
    file = Image.open(filename)
    # Sometimes it can open an image but it can't save it. We double check as a result.
    file.save(filename[:-4] + '.temp.jpg')
    os.remove(CurrentDirectory() + filename[:-4] + '.temp.jpg')
    return True
  except:
    return False

def ProcessImage(filename,chance,maxlen,maxFailedGlitches,seed):
  failedglitches = 0
  random.seed(seed)

  # Convert non-jpg's
  if filename[len(filename) - 3:len(filename)] != "jpg":
    try:
      tempImg = Image.open(filename)
      tempImg.save(filename[:-4] + '.jpg')
      os.remove(CurrentDirectory() + filename)
      filename = filename[:-4] + '.jpg'
    except:
      return 'INVALID'

  if ValidFileCheck(filename):
    glitchFileName = filename[:-4] + '-working.jpg'
    shutil.copy(filename,glitchFileName)
    CorruptImage(glitchFileName,chance,maxlen)
    

    # If it's too corrupt to be handled by PIL, we just start brute forcing.
    # If I care about this still in a week, I'll look at what causes it unrenderable. The header isn't touched so, :shrug:
    if ValidFileCheck(glitchFileName) == False:
      while (ValidFileCheck(glitchFileName) == False) and (failedglitches != maxFailedGlitches):
        # Sleep before/after remove, failure to causes a weird permissions bug in windows sometimes
        # Can't work out why!
        time.sleep(0.2)
        os.remove(CurrentDirectory() + glitchFileName)
        time.sleep(0.2)
        shutil.copy(filename,glitchFileName)
        CorruptImage(glitchFileName,chance,maxlen)
        failedglitches += 1
    
    if failedglitches != maxFailedGlitches:
      finalFileName = filename[:-4] + '-' + str(chance) + '-' + str(maxlen) + '-' + str(seed) + '.jpg'
      imaeg = Image.open(glitchFileName)
      imaeg.save(finalFileName)
      # Clean up
      os.remove(CurrentDirectory() + glitchFileName)
      os.remove(CurrentDirectory() + filename)
      return finalFileName
    else:
      os.remove(CurrentDirectory() + glitchFileName)
      os.remove(CurrentDirectory() + filename)
      return 'CANTGLITCH'
  else:
    os.remove(CurrentDirectory() + filename)  
    return 'INVALID'
