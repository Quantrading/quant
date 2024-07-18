import sys


def installWindPy():
    version=sys.version
    print(version);
    verss=version.split()[0].split('.');
    ver=int(verss[0])+float(verss[1])/10;
    bit=int(version.split(' bit ')[0].split()[-1]);

    if(len(sys.argv)<=1):
        print('No WindPy path!');
        return;
    #print(sys.argv[1:])

    srcpath=sys.argv[1];
    if not (srcpath.endswith('\\') or srcpath.endswith('//')):
        srcpath=srcpath+'\\'
        
    sitepath=".";
    for x in sys.path:
        ix=x.find('site-packages')
        if( ix>=0 and x[ix:]=='site-packages'):
          sitepath=x;
          break;

    filepath=sitepath+"\\WindPy.pth"
    #print(sitepath);    

    if(ver<2.6):
       print('Error: Python version must be >=2.6!')
       return;

    if(bit==64 ):
       print('Python is 64 bits')
       srcpath=srcpath+"x64"
    else:#if(bit==64 ):
       print('Python is 32 bits')
       srcpath=srcpath+"bin"

    #print(srcpath);
    sitefile=open(filepath,'w');
    sitefile.writelines(srcpath)
    sitefile.close();
    print('Installed into'),
    print(sitepath),
    print('OK!');
    
    

installWindPy()
