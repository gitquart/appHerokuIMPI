import os

class cInternalControl:
    idControl=5
    timeout=70
    version='2016'
    hfolder='appimpi'+version   
    heroku=True
    rutaHeroku='/app/'+hfolder
    rutaLocal=os.getcwd()+'\\'+hfolder+'\\'
    download_dir='Download_impi'+version
    enablePdf=False   