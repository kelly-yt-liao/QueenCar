import os


def pred_del(filename):
	delfilename = "test.png"
	path = "/home/willy/Ubuntu-Sever-Code/android-server/android/uploads/"
	pathname = os.path.abspath(os.path.join(path, filename))
	os.remove(delfilename)
	if pathname.startswith(path):
		os.remove(pathname)