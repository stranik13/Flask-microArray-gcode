import re
import json

def cmtcl(cmdstr):
	cmdstr= re.sub('\(.*\)','',cmdstr)
	ar = re.split(',', cmdstr)
	nstr = ''
	d = {}
	for a in ar:
		b = re.split(':', a)
		b[0] = '' + b[0] + ''
		d[b[0]] = b[1]
	return d


def getobj(cmdstr,jsdata):
	a = 'no'
	for c in jsdata['objlist']:
		if c['name'] == cmdstr['obj']:
			a = 'yes'
			d = c
	if a == 'no':
		print 'This object does not exist'
	else:
		return d

def washvar(obj,zf,xyf,gcode,cmdstr):
	#Here need to address feedrate
	#Here a unique m code for turning on pump
	#Here a unique m code for turning on vacuum
	trk = '(name:'+obj['name']+',v:'+cmdstr['v']+',t:'+cmdstr['t']+',f:'+re.sub(' ','',cmdstr['f'])+')'
	gcode.append(trk)
	gcode.append('G1 Z0 F'+str(zf))
	gcode.append('G1 X'+str(obj['x']) + ' Y'+str(obj['y']) + ' F'+str(xyf))
	gcode.append('G1 Z'+str(obj['z']) + ' F'+str(zf))
	return gcode

def microwellvar(obj,zf,xyf,gcode,cmdstr):
	#Here need to specify where to calibrate position the maxtip
	#And also where the first slide position is
	x = obj['x'] + (obj['wllcolsp']*int(cmdstr['sc']))
	y = obj['y'] + (obj['wllrowsp']*int(cmdstr['sr']))
	z = obj['z']
	trk = '(name:'+obj['name']+',sr:'+cmdstr['sr']+',sc:'+re.sub(' ','',cmdstr['sc'])+')'
	gcode.append(trk)
	gcode.append('G1 X'+str(x)+' Y'+str(y) + ' F'+str(xyf))
	gcode.append('G1 Z'+str(z) + ' F'+str(zf))
	return gcode


def spots(obj,cmdstr,bx,by,trk):
	#cmdstr = 'obj:slides,tbr:1,ter:1,tbc:1,tec:5,sbr:1,ser:2,sbc:1,sec:5 (microarray spotting)'
	coords = []
	for sr in range(int(cmdstr['sbr']), int(cmdstr['ser'])+1):
		for sc in range(int(cmdstr['sbc']), int(cmdstr['sec'])+1):
			sy = by + (obj['sprowsp'] * (sr-1));
			sx = bx + (obj['spcolsp'] * (sc-1));
			trk = 'sr:'+str(sr) + ',sc:'+str(sc)+')'
			coord = [sx,sy,trk]
			coords.append(coord)
	return coords

#default check
def blockcheck(obj,cmdstr):
	for a in cmdstr:
		if a == 'bbc':
			bbc = a['bbc']
		else: 
			bbc = 1
		if a == 'bec':
			bec = a['bec']
		else: 
			bec = obj['blcol']
		if a == 'bbr':
			bbr = a['bbr']
		else: 
			bbr = 1
		if a == 'ber':
			ber = a['ber']
		else: 
			ber = obj['blrow']
			
		blcoords = [bbc,bec,bbr,ber]
		return blcoords

def blocks(obj,cmdstr,tx,ty,trk):
	#For blocks if not indicated in command then it defaults to 1
	blcoords = blockcheck(obj,cmdstr)
	bbc = blcoords[0]
	bec = blcoords[1]
	bbr = blcoords[2]
	ber = blcoords[3]
	coords = []
	for br in range(int(bbr),int(ber)+1):
		for bc in range(int(bbc),int(bec)+1):
			by = ty + (obj['mrgtp'] + (obj['blrowsp'] * (br-1)))
			bx = tx + (obj['mrglft'] + (obj['blcolsp'] * (bc-1)))
			spcoords = spots(obj,cmdstr,bx,by,trk)
			for sp in spcoords:
				trk = 'br:'+str(br)+',bc:'+str(bc)+','+sp[2]
				coords.append([sp[0],sp[1],trk])
	return coords

def targets(obj,cmdstr,trk):
	coords = []
	for tr in range(int(cmdstr['tbr']),(int(cmdstr['ter'])+1)):
		for tc in range(int(cmdstr['tbc']),(int(cmdstr['tec'])+1)):
			ty = obj['y'] + ((obj['trgprowsp']+obj['dimy']) * (tr - 1))
			tx = obj['x'] + ((obj['trgpcolsp']+obj['dimx']) * (tc - 1))
			blcoords = blocks(obj,cmdstr,tx,ty,trk)
			for cd in blcoords:
				trk = '(name:'+obj['name']+',tr:'+str(tr)+',tc'+str(tc)+','+cd[2]
				coords.append([cd[0],cd[1],trk])
	return coords
			

def microarrayvar(obj,zf,xyf,gcode,cmdstr):
	#Again need to mention where to position 
	#Also need to indicate that really the top and left margins
	#Z array height needs to be created variable too
	zarh = 0
	#Now loop through the various objects
	#Track the commands
	trk = ''
	coords= targets(obj,cmdstr,trk)
	for cd in coords:
		gcode.append(cd[2])
		gcode.append('G1 X'+str(cd[0])+' Y'+str(cd[1]) + ' F'+str(xyf))
		gcode.append('G1 Z'+str(obj['z']) + ' F'+str(zf))
		gcode.append('G1 Z'+str(zarh) + ' F'+str(zf))
	return gcode

zf = 500
xyf = 2000
a = open('wkp')
b = json.load(a)
c = open('obj')

#cmdstr = 'obj:sourceplate,sr:1,sc:2 (source plate, row, col)'
#cmdstr = 'obj:wash1,v:1,t:30,f:50 (wash bowl 1, valve 1, wash time 30 seconds)'
#cmdstr = 'obj:maslides,tbr:1,ter:1,tbc:1,tec:5,sbr:1,ser:1,sbc:1,sec:5 (microarray spotting)'

gcode = []
for l in c:
	cmdstr = cmtcl(l)
	obj = getobj(cmdstr,b)
	if obj['typ'] == 'wash':
		gcode = washvar(obj,zf,xyf,gcode,cmdstr)
	if obj['typ'] == 'microwell':
		gcode = microwellvar(obj,zf,xyf,gcode,cmdstr)
	if obj['typ'] == 'microarray':
		gcode = microarrayvar(obj,zf,xyf,gcode,cmdstr)

a.close()
c.close()

for gc in gcode:
	print gc
