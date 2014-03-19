import sys
import os
import re
xfile  = sys.argv[1]
eggfile = re.sub("\.x$", ".egg", xfile)
if xfile == eggfile: # safety check
    print "Refusing to overwrite source file %s" % xfile
    sys.exit(1)

# clean up some blender conventions that x2egg doesn't like
xdata = open(xfile).read()
xdata = re.sub ("\.L", "_L", xdata)
xdata = re.sub ("\.R", "_R", xdata)
fh = open(xfile, "w")
fh.write(xdata)
fh.close()

os.system("x2egg %s -o %s -TR -90,0,0 %s" %
    (xfile, eggfile, " ".join(sys.argv[2:])))


