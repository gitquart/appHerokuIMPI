import os

class cInternalControl:
    idControl=3
    timeout=70
    version='2015'
    hfolder='appimpi'+version   
    heroku=False
    rutaHeroku='/app/'+hfolder
    rutaLocal=os.getcwd()+'\\'+hfolder+'\\'
    download_dir='Download_impi'+version
    enablePdf=False   