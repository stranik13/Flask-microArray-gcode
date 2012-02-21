import os,re,shutil,string,time
import json





def xmlsessbegin():
    f = open('jsessval')
    data = json.load(f)
    f.close()
    data['init'] = 0
    filen = data['file']
    filen = re.sub('.txt', '', filen)
    f = open('jsessval','w')
    f.write(json.dumps(data))
    f.close()
    return filen

def xmlsessinit(state):
    f = open('jsessval')
    data = json.load(f)
    f.close()
    data['init'] = state
    f = open('jsessval', 'w')
    f.write(json.dumps(data))
    f.close()

def xmlsessload(filen):
    f = open('jsessval')
    data = json.load(f)
    f.close()
    data['file'] = filen
    f = open('jsessval', 'w')
    f.write(json.dumps(data))
    f.close()

def xmlsessread():
    f = open('jsessval')
    #<init>0</init><leng>1000</leng><wid>500</wid><file>data</file><img>plotarea</img>
    data = json.load(f)
    f.close()
    confiles = os.listdir('./jsfiles')
    data['files'] = confiles
    if data['leng'] == '0':
   	data['leng'] = ''
    if data['wid'] == '0':
    	data['wid'] = ''
    f = open('jsessval', 'w')
    f.write(json.dumps(data))
    f.close()
    return data

def sessconfwrite(data):
    f = open('jsessval', 'w')
    f.write(json.dumps(data))
    f.close()


def confread(filen):
    f = open('jsfiles/'+filen)
    data = json.load(f)
    f.close()
    return data

def confwrite(filen,data):
    print "confwrite is called"
    f = open('jsfiles/'+filen+'.txt','w')
    f.write(json.dumps(data))
    f.close()

def confdatadelete(filen,objnumber):
    print "confdatadelete is called"
    data = confread(filen)
    data['objlist'].pop(objnumber) 
    confwrite(filen,data)
    return data
