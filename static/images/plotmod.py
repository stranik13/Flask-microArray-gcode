import Image, ImageDraw

l = 1000
w = 500

a = Image.new('RGB', [l,w], (238,232,170))

b = Image.new('RGB', [2,5], (0,0,0))
d = Image.new('RGB', [5,2], (0,0,0))

c = a

e  = ImageDraw.Draw(c)

ct = 0
for i in range(0,(l/100)):
	ct = ct + 100
	c.paste(b,(ct,0))
	e.text(((ct-5), 7),str(ct), (0,0,0)) 

ct = 0
for i in range(0,(w/100)):
	ct = ct + 100
	c.paste(d,(0,ct))
	e.text((7, (ct-5)), str(ct), (0,0,0)) 


c.save('newplot.gif')

