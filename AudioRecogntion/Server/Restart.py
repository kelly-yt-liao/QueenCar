import subprocess


var = 1
while var == 1 :

	bashCommand = "python AWWW_web.py"
	restart = subprocess.check_output(['bash','-c', bashCommand])
	print("test_output = "+ str(restart.decode('utf8')))
