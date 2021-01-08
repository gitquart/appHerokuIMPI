import os

class cInternalControl:
    idControl=9
    timeout=70
    hfolder='appimpi2020'   
    heroku=True
    rutaHeroku='/app/'+hfolder
    rutaLocal=os.getcwd()+'\\'+hfolder+'\\'
    download_dir='Download_impi2020'
    enablePdf=False   