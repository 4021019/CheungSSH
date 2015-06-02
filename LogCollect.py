#!/usr/bin/python
#coding:utf-8
import os,sys,random,paramiko,time
def LogCollect(ip,port,username,password,cmd,ListenTime,UseKey):
	try:
		outchar=''
		errchar=''
		ssh=paramiko.SSHClient()
		if UseKey=='y':
			KeyPath=os.path.expanduser('~/.ssh/id_rsa')
			key=paramiko.RSAKey.from_private_key_file(KeyPath)
			ssh.load_system_host_keys()
			ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) #使用这个，如果是第一次连接，就不会不会弹出(yes/no) 提示
			ssh.connect(ip,port,username,pkey=key)  			#paramiko用法  http://docs.paramiko.org/en/latest/api/client.html		
		else:
			ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			ssh.connect(ip,port,username,password)
			
		Timeout_i=1
		while Timeout_i<=int(ListenTime):
			stdin,stdout,stderr=ssh.exec_command(cmd)
			out=stdout.readlines()
			error_out=stderr.readlines()
			for o in out:
				outchar+=o
			for err in error_out:
				errchar+=err
			if errchar:
				print "\033[1;31m-ERR %s Deployment Faild , Check deployment FlagFile error  (%s)\033[0m\a" %(ip,errchar)
				return False
			if outchar=='DoneSucc': #shell的终端输出应该是  echo  -n 'DoneSucc'
				print "\033[1;32m+OK %s Deployment \033[0m" % (ip)
				return True
			#print "Wating %s (%d Sec) Deploeymenting..." %(ip,Timeout_i),
			Timeout_i+=1
			time.sleep(1)
		stdin,stdout,stderr=ssh.exec_command("""killall -9 tail 2&>/dev/null""")
			
	except Exception,e:
			print "\033[1;31m-ERR  %s\033[0m\a" % e
			return False


if __name__ =='__main__':
	#LogCollect(ip,port,username,passwd,cmd,Timeout)
	 LogCollect('127.0.0.1',22,'sshd','zaq1ZAQ!',"""grep  'a'  /tmp/a -q && echo  -n 'DoneSucc'""",10,'n')

