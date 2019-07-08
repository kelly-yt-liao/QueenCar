import subprocess



def pred():
	bashCommand = "curl localhost/models/images/classification/classify_one.json -XPOST -F job_id=20180517-150844-8e32 -F image_file=@/home/willy/Ubuntu-Sever-Code/android-server/android/test.png"
	output = subprocess.check_output(['bash','-c', bashCommand])
	print("output = "+ str(output.decode('utf8')))
	return output