import Image, ImageDraw
import re
import htsrijsonparser as htsip


def drawhead(filen,confdat,l,w,sessdat):
	#plot head
	if l > 0 and w > 0:
		ph = Image.new('RGB', [l,w], (255,165,0))
		ph.save('static/images/'+filen+'-ph.gif')


def drawdeck(filen,confdat,sessdat):
	#plot area
	pa = Image.new('RGB', [int(confdat['plx']),int(confdat['ply'])], (238,232,170))
	ph = Image.open('static/images/'+filen+'-ph.gif')
	phsz = ph.size
	rph = ph.resize([int((phsz[0]/10)) , int((phsz[1]/10))])

	#hashmarks
	hx = Image.new('RGB', [2,5], (0,0,0))
	hy = Image.new('RGB', [5,2], (0,0,0))

	e  = ImageDraw.Draw(pa)
	ct = 0
	for i in range(0,(int(confdat['plx'])/100)):
		ct = ct + 100
		pa.paste(hx,(ct,0))
		e.text(((ct-5), 7),str(ct), (0,0,0)) 
	ct = 0
	for i in range(0,(int(confdat['ply'])/100)):
		ct = ct + 100
		pa.paste(hy,(0,ct))
		e.text((7, (ct-5)), str(ct), (0,0,0)) 

	#paste the plot head
	if sessdat['displothead'] == 'yes':
		if confdat['phx'] > 0 and confdat['phy'] > 0:
			pa.paste(rph,(int(sessdat['pxpos']),int(sessdat['pypos'])))
	pa.save('static/images/'+filen+'.gif')

def drawpoint(dat,objname):
	ph = Image.new('RGB', [10,10], (255,165,0))
	dr = ImageDraw.Draw(ph)
	dr.line((0,0) + ph.size, fill=128)
	dr.line((0,ph.size[1]) + (ph.size[1],0), fill=128)
	filen = dat['file']
	ph.save('static/images/'+filen+'-'+objname+'.gif')


def plotarea(sessdat):
	filen = sessdat['file']
        confdat = htsip.confread(filen)
	return confdat

def plothead(sessdat,confdat):
	filen = sessdat['file']
	l = int(confdat['plothead']['x']) * 10
	w = int(confdat['plothead']['y']) * 10
	drawhead(filen,confdat,l,w,sessdat)
	
