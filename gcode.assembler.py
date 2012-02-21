from flask import Flask
from flask import request
from flask import abort, redirect, url_for, g,send_from_directory
from flask import jsonify, render_template,sessions
from werkzeug import secure_filename
#import htsrijsonimagetools as htsi
import htsrijsonparser as htsip
import os,re,shutil,string,time,json

# so mark it as modified yourself

UPLOAD_FOLDER = 'jsfiles'
TMP_FOLDER = ''

ALLOWED_EXTENSIONS = set(['txt', 'gcode'])


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TMP_FOLDER'] = TMP_FOLDER


def newobjlist(confdat):
	if 'objlist' in confdat:
		pass
	else:
		confdat['objlist'] = []
	return confdat	



@app.route('/downloads/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

	
@app.route('/')
def index():
    	#return render_template('gui.init.html')
	filen = htsip.xmlsessbegin()
	dat = htsip.xmlsessread()
    	return render_template('gui.init.html', condat=dat)

@app.route('/svresp', methods=['GET','POST'])
def svresp():
	if request.method == 'POST':
		but = request.form['but']
		sel = request.form['sel']
		dat = htsip.xmlsessread()
		print but + ' ' + sel
    		return render_template('gui.init.html', condat=dat)
	else:
		return 'no'

@app.route('/homing', methods=['GET','POST'])
def homing():
	if request.method == 'POST':
		ho = request.form['ho']
		print ho + 'homing'
		return redirect(url_for('nindex'))
	else:
		return 'no'


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/gfile', methods=['GET','POST'])
def gfile():
	if request.method == 'POST':
		file = request.files['datafile']
		print file.filename
		htsip.xmlsessload(file.filename)
		dat = htsip.xmlsessread()
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			print filename
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			dat = htsip.xmlsessread()
    			return render_template('gui.init.html', condat=dat)







@app.route('/editconf', methods=['GET','POST'])
def editconf():
        dat = htsip.xmlsessread()
	confdat=htsip.confread(dat['file'])
	ti = str(time.time())
	if len(confdat['objlist']) == 0:
		mod='n'
	else: 
		mod = 'y'
    	return render_template('gui.img.edit.html', dat=dat, confdat=confdat, act='plotarea', ti=ti, mod=mod)

@app.route('/confnew', methods=['GET','POST'])
def confnew():
	if request.method == 'POST':
		filen = request.form['filen']
        	dat = htsip.xmlsessread()
		err = 'n'
		#here i need to figure out a way to check directory so its wrong
		for i in dat['files']:
			print i
			if filen == i:
				err = 'y'
	 	if err == 'y':
			return 'This file already exists'
		else:
			fl = open('jsfiles/'+filen+'.txt', 'w')
			stdat = '{"plothead": {"reftip": 11, "camy": "25", "camx": "15", "camdiam": "30", "xsp": "4.5", "tipy": 5, "tipx": 3, "posx": "10", "posy": "100", "y": "150", "x": "100", "ysp": "4.5"},"deck": {"ply": 600.0, "plx": 600.0},"objlist":[]}'
			fl.write(stdat)
			fl.close()
			htsip.xmlsessload(filen)
       			dat = htsip.xmlsessread()
			confdat=htsip.confread(dat['file'])
    			return render_template('gui.img.edit.html', dat = dat, confdat=confdat, act='newobject',  mod='n')

@app.route('/confsel', methods=['GET','POST'])
def confsel():
	filen = request.form['filen']
	acti = request.form['act']
	htsip.xmlsessload(filen)
        dat = htsip.xmlsessread()
	confdat=htsip.confread(dat['file'])
	if len(confdat['objlist']) == 0:
		pg = 'plotarea'
		mod = 'n'
	else:
		pg = 'newobject'
		mod = 'y'
	if acti == 'Load':
    		return render_template('gui.img.edit.html', dat = dat, confdat=confdat, act=pg,  mod=mod)
	if acti == 'Download':
    		f = open('templates/gui.tmp.txt','w')
   		f.write(json.dumps(confdat))
    		f.close()
    		return render_template('gui.tmp.html', dat=dat)


@app.route('/adjustview', methods=['GET','POST'])
def adjustview():
	if request.method == 'POST':
		dat = htsip.xmlsessread()
		dat['leng'] = request.form['len']
		dat['wid'] = request.form['wid']
		dat['img'] = request.form['img']
		htsip.sessconfwrite(dat)
		confdat=htsip.confread(dat['file'])
		ti = str(time.time())
		mod='n'
		if len(confdat['objlist']) > 0:
			mod = 'y'
    		return render_template('gui.img.edit.html', dat=dat, confdat=confdat, act='adjustview', ti=ti,mod=mod)

@app.route('/plotarea', methods=['GET','POST'])
def plotarea():
	if request.method == 'POST':
		dat = htsip.xmlsessread()
		confdat = htsip.confread(dat['file'])
		#Plot area dimensions
		if len(request.form['len']) > 0:
			confdat['deck']['plx'] = float(request.form['len'])
		if len(request.form['wid']) > 0:
			confdat['deck']['ply'] = float(request.form['wid'])
		dat['displothead'] = int(request.form['displothead'])
		dat['disobjs'] = int(request.form['disobjs'])
		#Display plothead position
		if len(request.form['pxpos']) > 0:
			dat['pxpos'] = request.form['pxpos']
		if len(request.form['pypos']) > 0:
			dat['pypos'] = request.form['pypos']
		htsip.sessconfwrite(dat)
		htsip.confwrite(dat['file'],confdat)
		ti = str(time.time())
		mod='n'
		if len(confdat['objlist']) > 0:
			mod = 'y'
    		return render_template('gui.img.edit.html', dat=dat, act='plotarea', confdat=confdat, ti=ti,mod=mod)

@app.route('/plothead', methods=['GET','POST'])
def plothead():
	if request.method == 'POST':
		dat = htsip.xmlsessread()
		confdat = htsip.confread(dat['file'])
		if len(request.form['len']) > 0:
			confdat['plothead']['x'] = request.form['len']
		if len(request.form['wid']) > 0:
			confdat['plothead']['y'] = request.form['wid']
		if len(request.form['posx']) > 0:
			confdat['plothead']['posx'] = request.form['posx']
		if len(request.form['posy']) > 0:
			confdat['plothead']['posy'] = request.form['posy']
		if len(request.form['xsp']) > 0:
			confdat['plothead']['xsp'] = request.form['xsp']
		if len(request.form['ysp']) > 0:
			confdat['plothead']['ysp'] = request.form['ysp']
		if len(request.form['tipx']) > 0:
			confdat['plothead']['tipx'] = float(request.form['tipx'])
		if len(request.form['tipy']) > 0:
			confdat['plothead']['tipy'] = float(request.form['tipy'])
		if len(request.form['reftip']) > 0:
			confdat['plothead']['reftip'] = int(request.form['reftip'])
		if len(request.form['camx']) > 0:
			confdat['plothead']['camx'] = request.form['camx']
		if len(request.form['camy']) > 0:
			confdat['plothead']['camy'] = request.form['camy']
		if len(request.form['camdiam']) > 0:
			confdat['plothead']['camdiam'] = request.form['camdiam']
		dat['img'] = request.form['img']
		htsip.sessconfwrite(dat)
		htsip.confwrite(dat['file'],confdat)
		ti = str(time.time())
		mod='n'
		if len(confdat['objlist']) > 0:
			mod = 'y'
    		return render_template('gui.img.edit.html', dat=dat, act='plothead', confdat=confdat, ti=ti,mod=mod)

@app.route('/modplot', methods=['GET','POST'])
def modplot():
	if request.method == 'POST':
		dat = htsip.xmlsessread()
		confdat = htsip.confread(dat['file'])
		cmd = request.form['but']
		ti = str(time.time())
		mod='n'
		if len(confdat['objlist']) > 0:
			mod = 'y'
		if cmd == 'Plot Area':
			dat['img'] = 'plotarea'
			htsip.sessconfwrite(dat)
			confdat = htsip.confread(dat['file'])
    			return render_template('gui.img.edit.html', dat=dat, act='plotarea', confdat=confdat, ti=ti, mod=mod)
		if cmd == 'Adjust View':
			confdat = htsip.confread(dat['file'])
    			return render_template('gui.img.edit.html', dat=dat, confdat=confdat, act='adjustview', ti=ti, mod=mod)
		if cmd == 'New Object':
			confdat = htsip.confread(dat['file'])
    			return render_template('gui.img.edit.html', dat=dat, confdat=confdat, act='newobject', ti=ti, mod=mod)
		if cmd == 'Modify Object':
			confdat = htsip.confread(dat['file'])
    			return render_template('gui.img.edit.html', dat=dat, confdat=confdat, act='modifyobject', mod=mod, objnumber=0)
		if cmd == 'Plot Head':
			dat['img'] = 'plotarea'
			htsip.sessconfwrite(dat)
			confdat = htsip.confread(dat['file'])
    			return render_template('gui.img.edit.html', dat=dat, act='plothead', confdat=confdat, ti=ti,mod=mod)
		if cmd == 'Assemble Gcode':
			confdat = htsip.confread(dat['file'])
			f = open('templates/gui.tmp.txt','w')
	                f.write(json.dumps(confdat))
       			f.close()
    			return render_template('gui.img.edit.html', dat=dat, confdat=confdat, act='assemblegcode', mod=mod, objnumber=0)

@app.route('/menu', methods=['GET','POST'])
def menu():
	dat = htsip.xmlsessread()
	confdat = htsip.confread(dat['file'])
	cmd = request.form['but']
	if cmd == 'Delete':
		os.rename('jsfiles/'+dat['file'], 'delfiles/del'+dat['file'])
		htsip.xmlsessload('')
		dat = htsip.xmlsessread()
    	return render_template('gui.init.html', condat=dat)

@app.route('/pointobj', methods=['GET','POST'])
def pointobj():
	if request.method == 'POST':
		dat = htsip.xmlsessread()
		confdat = htsip.confread(dat['file'])
		objname = request.form['name']
		confdat = newobjlist(confdat)
		if objname in confdat:
    			return render_template('gui.img.edit.html', dat=dat, confdat=confdat, act='newobject', error='y')
		else:
			x = request.form['x']
			y = request.form['y']
			z = request.form['z']
			confdat['objlist'].append({'name':objname,'x':float(x),'y':float(y),'z':float(z)})
		htsip.confwrite(dat['file'],confdat)
		ti = str(time.time())
		htsi.drawpoint(dat,objname)
		mod='n'
		if len(confdat['objlist']) > 0:
			mod = 'y'
    		return render_template('gui.img.edit.html', dat=dat, confdat=confdat, act='plotarea', ti=ti,mod=mod)

@app.route('/microarrayobj', methods=['GET','POST'])
def microarrayobj():
	dat = htsip.xmlsessread()
	confdat = htsip.confread(dat['file'])
	name = request.form['trgpname']
	modify = request.form['modify']
	confdat = newobjlist(confdat)
	if request.form['subval'] == 'delete':
		confdat = htsip.confdatadelete(dat['file'],int(request.form['objnumber']))
	else:
		ld = 'y'
		for cn in confdat['objlist']:
			if cn['name'] == name:
				if modify == 'no':
					ld = 'n'
		if ld == 'n':
    			return render_template('gui.img.edit.html', dat=dat, confdat=confdat, act='newobject', error='y', objname=name)
		else:
			trgpx = request.form['trgpx']
			trgpy = request.form['trgpy']
			trgpz = request.form['trgpz']
			dimx = request.form['dimx']
			dimy = request.form['dimy']
			trgpcol = request.form['trgpcol']
			trgprow = request.form['trgprow']
			trgpcolsp = request.form['trgpcolsp']
			trgprowsp = request.form['trgprowsp']
			mrglft = request.form['mrglft']
			mrgrt = request.form['mrgrt']
			mrgtp = request.form['mrgtp']
			mrgbt = request.form['mrgbt']
			blcol = request.form['blcol']
			blrow = request.form['blrow']
			blcolsp = request.form['blcolsp']
			blrowsp = request.form['blrowsp']
			spcol = request.form['spcol']
			sprow = request.form['sprow']
			spcolsp = request.form['spcolsp']
			sprowsp = request.form['sprowsp']
			if modify == 'no':
				confdat['objlist'].append({'mrglft':float(mrglft),'mrgrt':float(mrgrt),'mrgtp':float(mrgtp),'mrgbt':float(mrgbt),'name':name,'x':float(trgpx),'y':float(trgpy),'dimx':float(dimx),'dimy':float(dimy),'z':float(trgpz),'trgpcol':int(trgpcol),'trgprow':int(trgprow),'trgpcolsp':float(trgpcolsp),'trgprowsp':float(trgprowsp),'blcol':int(blcol),'blrow':int(blrow),'blcolsp':float(blcolsp),'blrowsp':float(blrowsp),'spcol':int(spcol),'sprow':int(sprow),'spcolsp':float(spcolsp),'sprowsp':float(sprowsp),'typ':'microarray'})
			if modify == 'yes':
				objnumber=int(request.form['objnumber'])
				confdat['objlist'][objnumber]['name'] = name
				confdat['objlist'][objnumber]['typ'] = 'microarray'
				confdat['objlist'][objnumber]['dimx']=float(dimx)
				confdat['objlist'][objnumber]['dimy']=float(dimy)
				confdat['objlist'][objnumber]['name']=name
				confdat['objlist'][objnumber]['x']=float(trgpx)
				confdat['objlist'][objnumber]['y']=float(trgpy)
				confdat['objlist'][objnumber]['z']=float(trgpz)
				confdat['objlist'][objnumber]['mrglft']=float(mrglft)
				confdat['objlist'][objnumber]['mrgrt']=float(mrgrt)
				confdat['objlist'][objnumber]['mrgtp']=float(mrgtp)
				confdat['objlist'][objnumber]['mrgbt']=float(mrgbt)
				confdat['objlist'][objnumber]['trgpcol']=int(trgpcol)
				confdat['objlist'][objnumber]['trgprow']=int(trgprow)
				confdat['objlist'][objnumber]['trgpcolsp']=float(trgpcolsp)
				confdat['objlist'][objnumber]['trgprowsp']=float(trgprowsp)
				confdat['objlist'][objnumber]['blcol']=int(blcol)
				confdat['objlist'][objnumber]['blrow']=int(blrow)
				confdat['objlist'][objnumber]['blcolsp']=float(blcolsp)
				confdat['objlist'][objnumber]['blrowsp']=float(blrowsp)
				confdat['objlist'][objnumber]['spcol']=int(spcol)
				confdat['objlist'][objnumber]['sprow']=int(sprow)
				confdat['objlist'][objnumber]['spcolsp']=float(spcolsp)
				confdat['objlist'][objnumber]['sprowsp']=float(sprowsp)
			htsip.confwrite(dat['file'],confdat)
		ti = str(time.time())
		mod='n'
		if len(confdat['objlist']) > 0:
			mod = 'y'
    		return render_template('gui.img.edit.html', dat=dat, confdat=confdat, act='plotarea', ti=ti,error='n',mod=mod)
			

@app.route('/microwellobj', methods=['GET','POST'])
def microwellobj():
	dat = htsip.xmlsessread()
	modify = request.form['modify']
	confdat = htsip.confread(dat['file'])
	name = request.form['trgpname']
	if request.form['subval'] == 'delete':
		confdat = htsip.confdatadelete(dat['file'],int(request.form['objnumber']))
	else:
		ld = 'y'
		for cn in confdat['objlist']:
			if cn['name'] == name:
				if modify == 'no':
					ld = 'n'
		if ld == 'n':
    			return render_template('gui.img.edit.html', dat=dat, confdat=confdat, act='newobject', error='y', objname=name)
		else:
			orient = request.form['orient']
			trgpx = request.form['trgpx']
			trgpy = request.form['trgpy']
			trgpz = request.form['trgpz']
			dimx = request.form['dimx']
			dimy = request.form['dimy']
			wllrow = request.form['wllrow']
			wllrowsp = request.form['wllrowsp']
			wllcol = request.form['wllcol']
			wllcolsp = request.form['wllcolsp']
			if modify == 'no':
				confdat['objlist'].append({'name':name,'x':float(trgpx),'y':float(trgpy),'dimx':float(dimx),'dimy':float(dimy),'z':float(trgpz),'wllrow':int(wllrow),'wllrowsp':float(wllrowsp),'wllcol':int(wllcol),'wllcolsp':float(wllcolsp),'typ':'microwell','orient':orient})
			if modify == 'yes':
				objnumber=int(request.form['objnumber'])
				confdat['objlist'][objnumber]['orient'] = orient
				confdat['objlist'][objnumber]['name'] = name
				confdat['objlist'][objnumber]['x'] = float(trgpx)
				confdat['objlist'][objnumber]['y'] = float(trgpy)
				confdat['objlist'][objnumber]['z'] = float(trgpz)
				confdat['objlist'][objnumber]['dimx'] = float(dimx)
				confdat['objlist'][objnumber]['dimy'] = float(dimy)
				confdat['objlist'][objnumber]['wllrow'] = int(wllrow)
				confdat['objlist'][objnumber]['wllrowsp'] = float(wllrowsp)
				confdat['objlist'][objnumber]['wllcol'] = int(wllcol)
				confdat['objlist'][objnumber]['wllcolsp'] = float(wllcolsp)
			htsip.confwrite(dat['file'],confdat)
	ti = str(time.time())
	mod='n'
	if len(confdat['objlist']) > 0:
		mod = 'y'
     	return render_template('gui.img.edit.html', dat=dat, confdat=confdat, act='plotarea', error='n',mod=mod)

@app.route('/washobj', methods=['GET','POST'])
def washobj():
	dat = htsip.xmlsessread()
	confdat = htsip.confread(dat['file'])
	modify = request.form['modify']
	name = request.form['trgpname']
	if request.form['subval'] == 'delete':
		confdat = htsip.confdatadelete(dat['file'],int(request.form['objnumber']))
	else:
		ld = 'y'
		for cn in confdat['objlist']:
			if cn['name'] == name:
				if modify == 'no':
					ld = 'n'
		if ld == 'n':
    			return render_template('gui.img.edit.html', dat=dat, confdat=confdat, act='newobject', error='y', objname=name)
		else:
			trgpx = request.form['trgpx']
			trgpy = request.form['trgpy']
			trgpz = request.form['trgpz']
			dimx = request.form['dimx']
			dimy = request.form['dimy']
			flrt = request.form['flrt']
			wshtm = request.form['wshtm']
			if modify == 'no':
				confdat['objlist'].append({'name':name,'x':float(trgpx),'y':float(trgpy),'dimx':float(dimx),'dimy':float(dimy),'z':float(trgpz),'flrt':float(flrt),'wshtm':float(wshtm),'typ':'wash'})
			if modify == 'yes':
				objnumber=int(request.form['objnumber'])
				confdat['objlist'][objnumber]['x'] = float(trgpx)
				confdat['objlist'][objnumber]['y'] = float(trgpy)
				confdat['objlist'][objnumber]['z'] = float(trgpz)
				confdat['objlist'][objnumber]['dimx'] = float(dimx)
				confdat['objlist'][objnumber]['dimy'] = float(dimy)
				confdat['objlist'][objnumber]['flrt'] = float(flrt)
				confdat['objlist'][objnumber]['wshtm'] = float(wshtm)
	htsip.confwrite(dat['file'],confdat)
	ti = str(time.time())
	mod='n'
	if len(confdat['objlist']) > 0:
		mod = 'y'
     	return render_template('gui.img.edit.html', dat=dat, confdat=confdat, act='plotarea', error='n',mod=mod)

@app.route('/pointobj', methods=['GET','POST'])
def pointobj():
	dat = htsip.xmlsessread()
	confdat = htsip.confread(dat['file'])
	modify = request.form['modify']
	name = request.form['trgpname']
	if request.form['subval'] == 'delete':
		confdat = htsip.confdatadelete(dat['file'],int(request.form['objnumber']))
	else:
		ld = 'y'
		for cn in confdat['objlist']:
			if cn['name'] == name:
				if modify == 'no':
					ld = 'n'
		if ld == 'n':
    			return render_template('gui.img.edit.html', dat=dat, confdat=confdat, act='newobject', error='y', objname=name)
		else:
			trgpx = request.form['trgpx']
			trgpy = request.form['trgpy']
			trgpz = request.form['trgpz']
			dimx = request.form['dimx']
			dimy = request.form['dimy']
			if modify == 'no':
				confdat['objlist'].append({'name':name,'x':float(trgpx),'y':float(trgpy),'dimx':float(dimx),'dimy':float(dimy),'z':float(trgpz),'typ':'point'})
			if modify == 'yes':
				objnumber=int(request.form['objnumber'])
				confdat['objlist'][objnumber]['x'] = float(trgpx)
				confdat['objlist'][objnumber]['y'] = float(trgpy)
				confdat['objlist'][objnumber]['z'] = float(trgpz)
				confdat['objlist'][objnumber]['dimx'] = float(dimx)
				confdat['objlist'][objnumber]['dimy'] = float(dimy)
	htsip.confwrite(dat['file'],confdat)
	ti = str(time.time())
	mod='n'
	if len(confdat['objlist']) > 0:
		mod = 'y'
     	return render_template('gui.img.edit.html', dat=dat, confdat=confdat, act='plotarea', error='n',mod=mod)


@app.route('/selectobject', methods=['GET','POST'])
def selectobject():
		dat = htsip.xmlsessread()
		confdat = htsip.confread(dat['file'])
		objnumber = request.form['object']
		confdat = newobjlist(confdat)
		mod='n'
		if len(confdat['objlist']) > 0:
			mod = 'y'
    		return render_template('gui.img.edit.html', dat=dat, confdat=confdat, act='modifyobject', objnumber=int(objnumber),mod=mod)

@app.route('/assemblecode', methods=['GET','POST'])
def assemblecode():
	if request.method == 'POST':
		dat = htsip.xmlsessread()
		confdat = htsip.confread(dat['file'])
		gcmd = request.form['gcmd']
		error = 'n'
		errordet = ''
		if len(gcmd) > 0:
			cmdry = re.split('\n', gcmd)
			f = open('obj','w')
			for l in cmdry:
			  f.write(l)
			f.close()
			fl = dat['file']
			cmd = 'cp jsfiles/'+fl+' ./wkp'
			os.system(cmd)
			cmd = 'zip gcode.formatter.zip obj gcode.formatter.py wkp'
			os.system(cmd)
			cmd = 'mv gcode.formatter.zip jsfiles/'
			os.system(cmd)
		else:
			cmdry = []
			error = 'y'
			errordet = 'Please enter data'
    		return render_template('gui.img.edit.html', dat=dat, confdat=confdat, act='setuptranslate', error=error, errordet=errordet,cmdry=cmdry,mod='y')

@app.route('/uploadcode', methods=['GET','POST'])
def uploadcode():
	if request.method == 'POST':
		file = request.files['file']
		dat = htsip.xmlsessread()
		confdat = htsip.confread(dat['file'])
		error = 'n'
		errordet = ''
		if len(file.filename) > 0:
			file.save(os.path.join(app.config['TMP_FOLDER'], 'tmpfile'))
			of = open('tmpfile')
			f = open('obj','w')
			cmdry = ['yes']
			for l in of:
				f.write(l)	
			f.close()
			of.close()
			fl = dat['file']
			cmd = 'cp jsfiles/'+fl+' ./wkp'
			os.system(cmd)
			cmd = 'zip gcode.formatter.zip obj gcode.formatter.py wkp'
			os.system(cmd)
			cmd = 'mv gcode.formatter.zip jsfiles/'
			os.system(cmd)
		else:
			cmdry = []
			error = 'y'
			errordet = 'File was not submitted'
    		return render_template('gui.img.edit.html', dat=dat, confdat=confdat, act='setuptranslate', error=error, errordet=errordet,cmdry=cmdry,mod='y')



if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')

