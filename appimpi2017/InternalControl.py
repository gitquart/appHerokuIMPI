import os

class cInternalControl:
    idControl=6
    timeout=70
    version='2017'
    hfolder='appimpi'+version   
    heroku=True
    rutaHeroku='/app/'+hfolder
    rutaLocal=os.getcwd()+'\\'+hfolder+'\\'
    download_dir='Download_impi'+version
    enablePdf=False   