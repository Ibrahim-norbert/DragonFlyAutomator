# This generates a script for depth of field enhancement.  It assumes you have
# multiple images of each drop with small changes in Z and one unfocused image
# between each stack.  You need to enter the number of data images per well 
# and the number of drops.  It should not be a problem if some files are missing.

import os,sys
import numpy as np

try:
    with open(sys.argv[1]) as f:
        nimages=int((f.readline()).split('#', 1)[0])
        ndrops= int((f.readline()).split('#', 1)[0])
        name_root=((f.readline()).split('#', 1)[0]).strip()
        img_dir=((f.readline()).split('#', 1)[0]).strip()
except:
    print'The configuration file was missing or the format was not right'
    print'usage: python prep_stack.py config_file.txt output_file.com'
    print 'Tthe configuration file should look something like this:'
    print'  5                        # number of data images per well'
    print'  96                       # number of wells'
    print'  IMG                      # Image file root'
    print'  /media/user/SD_card/DCIM # location of the image files'
    print; quit()
if img_dir[-1]!='/':img_dir=img_dir+'/'

print; print ndrops,' well plate with ',nimages,' images per drop'
print 'files begin with ',name_root,' and are in directory',img_dir; print
tmpx=raw_input("return to continue or any other key if these are not correct ")
if tmpx!='': 
	print 'You will need to edit the configuration file to fix this'
	print; quit()

files=[]; sizes=[]; fnums=[]

for filename in os.listdir(img_dir):
	if filename[0:3]==name_root:
		files.append(filename)
files.sort()
for filename in files:
	fnum=int(filename[4:8]) # this might need to change if image names do not have a 3 character root or a different number of leading zeros 
	fnums.append(fnum)
	size = os.path.getsize((img_dir+'/'+filename))
        sizes.append(size)
print len(sizes),' of ',(nimages+1)*ndrops,' images found' 
if len(sizes)==(nimages+1)*ndrops: 
	print'Congratulations, it looks like you have all your images!'
	allthere=1
else: 
	print 'The program will try to use out of focus images to build the stacks'
	allthere=0
last=-1 
print; print'the output command file will be written to ',sys.argv[2]
print'images will be moved from ',img_dir,' to ./raw_images' 
print'type \"source ',sys.argv[2],'\" to process the images'  
# the following line will direct print output to $2
sys.stdout = open(sys.argv[2],'w')
print'mkdir raw_images'
print'mv -v ',img_dir + '*.JPG raw_images/.' 
for drop in range(ndrops):
	print 'echo \'processing drop ' + str((drop+1)) + '\''
	if drop < (ndrops-1):
	   if allthere: oof=last+nimages+1
	   else:
		oof=last+nimages
		smallest=sizes[(last+nimages)] # start comparing sizes at the top image 
		for n in range((last+nimages+1),(last+nimages+2)):
			if smallest>=sizes[n]:
				smallest=sizes[n]
				oof=n # this is the index of the smallest file and thus (hopefully) the most out of focus
				#print 'n',n, 'sizes[n]',sizes[n],'smallest',smallest,'oof',oof
	else: oof = len(fnums)-1
	firstimg=fnums[(last+1)]
	oofimg=fnums[oof]
	print '# images: ',firstimg,' to ',(oofimg-1),' : ',(oofimg-firstimg),' images'
	print 'rm OUT*.tif'
	line='align_image_stack -m -a OUT ' 
	for imgnum in range(firstimg,oofimg):
		line = line + 'raw_images/' + name_root + str(imgnum).zfill(5) + '.JPG '
	print line		
	last=oof
	print 'enfuse --exposure-weight=0 --saturation-weight=0 --contrast-weight=1 --hard-mask --output=' + 'stacked' + str((drop+1)).zfill(5) + '.tif OUT*.tif'
	print 'rm OUT*.tif'
#the following lines run the neural network prediction
#print 'for f in *.tif; do  echo "Converting $f"; convert "$f"  "$(basename "$f" .tif).jpg"; done'
#print 'for f in *.jpg; do  echo "Converting $f"; python jpeg2json.py "$f" > "$(basename "$f" .jpg).json"; done'
#print 'for f in *.json; do echo "Are there crystals? $f"; gcloud ml-engine local predict --model-dir=savedmodel --json-instances="$f"; done'
 
