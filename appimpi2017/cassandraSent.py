import json
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import SimpleStatement
import os
from InternalControl import cInternalControl

objControl=cInternalControl()
timeOut=objControl.timeout
idControl=objControl.idControl
hfolder=objControl.hfolder



def getCluster():
    #Connect to Cassandra
    objCC=CassandraConnection()
    cloud_config=''
    if objControl.heroku:
        cloud_config= {'secure_connect_bundle': objControl.rutaHeroku+'/secure-connect-dbquart.zip'}
    else:
        cloud_config= {'secure_connect_bundle': objControl.rutaLocal+'secure-connect-dbquart.zip'}


    auth_provider = PlainTextAuthProvider(objCC.cc_user,objCC.cc_pwd)
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider) 

    return cluster  
              
def cassandraBDProcess(json_doc):
     
    record_added=False

    cluster=getCluster()
    session = cluster.connect()
    session.default_timeout=timeOut
    row=''
    value=json_doc['document']
    #Check wheter or not the record exists, check by numberFile and date
    #Date in cassandra 2020-09-10T00:00:00.000+0000
    querySt="select id from thesis.impi_docs where document='"+str(value)+"'  ALLOW FILTERING"
    
                
    future = session.execute_async(querySt)
    row=future.result()
    lsRes=[]
        
    if row: 
        record_added=False
        valid=''
        for val in row:
            valid=str(val[0])
        lsRes.append(record_added) 
        lsRes.append(valid)   
        cluster.shutdown()
    else:        
        #Insert Data as JSON
        jsonS=json.dumps(json_doc)           
        insertSt="INSERT INTO thesis.impi_docs JSON '"+jsonS+"';" 
        future = session.execute_async(insertSt)
        future.result()  
        record_added=True
        lsRes.append(record_added)
        cluster.shutdown()         
                    
                         
    return lsRes

def updatePage(page):

    cluster=getCluster()
    session = cluster.connect()
    session.default_timeout=timeOut
    page=str(page)
    querySt="update thesis.cjf_control set page="+page+" where id_control="+str(idControl)+";"          
    future = session.execute_async(querySt)
    future.result()
                         
    return True

def returnQueryResult(querySt):
    cluster=getCluster()
    session = cluster.connect()
    session.default_timeout=timeOut
    result=''
    future = session.execute_async(querySt)
    result=future.result()
    cluster.shutdown()

    return result  

def executeNonQuery(querySt):
    cluster=getCluster()
    session = cluster.connect()
    session.default_timeout=timeOut
    future = session.execute_async(querySt)
    future.result()
    cluster.shutdown()

    return True  


def insertPDF(json_doc):
     
    record_added=False

    cluster=getCluster()
    session = cluster.connect()
    session.default_timeout=timeOut

    iddocumento=str(json_doc['idDocumento'])
    documento=str(json_doc['documento'])
    fuente=str(json_doc['fuente'])
    secuencia=str(json_doc['secuencia'])
    querySt="select id from thesis.tbDocumento_impi where iddocumento="+iddocumento+" and documento='"+documento+"' and fuente='"+fuente+"' AND secuencia="+secuencia+"  ALLOW FILTERING"          
    future = session.execute_async(querySt)
    row=future.result()

    if row:
        cluster.shutdown()
    else:    
        jsonS=json.dumps(json_doc)           
        insertSt="INSERT INTO thesis.tbDocumento_impi JSON '"+jsonS+"';" 
        future = session.execute_async(insertSt)
        future.result()  
        record_added=True
        cluster.shutdown()     
                    
                         
    return record_added         

   
class CassandraConnection():
    cc_user='quartadmin'
    cc_keyspace='thesis'
    cc_pwd='P@ssw0rd33'
        

