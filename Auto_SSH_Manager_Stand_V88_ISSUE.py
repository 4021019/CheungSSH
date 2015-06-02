#!/usr/bin/python
#coding:utf8
VERSION=86
import os,sys
BUILD_CMD=['exit','flush logs']
os.sys.path.insert(0,os.path.abspath('./'))
os.sys.path.insert(0,os.path.abspath('/cheung/bin/'))
try:
	import paramiko,threading,socket,ConfigParser,time,commands,threading,re,getpass,Format_Char_Show,shutil,random,getpass,LogCollect
except Exception,e:
	print "\033[1m\033[1;31m-ERR %s\033[0m\a"	% (e)
	sys.exit(1)
LogFile='/cheung/logs/auto_ssh.log'
DeploymentFlag="/tmp/DeploymentFlag%s" % (str(random.randint(999999999,999999999999)))
KEYDAY=30
try:
	paramiko.util.log_to_file('/cheung/logs/paramiko.log')
except Exception,e:
	pass
os.system('stty erase ^H 2>/dev/null')
def Write_Log(ip,stderr,stdout,Logcmd,LogFile,useroot,username,UseLocalScript,Deployment,DeploymentStatus):
	if DeploymentStatus:
		DeploymentStatus='Y'
	else:
		DeploymentStatus='N'
	Deployment=Deployment.upper()
	
	try:
		T=open(LogFile,"a")
		T.write(ip+ '===' + username  + '===' + time.strftime('%Y%m%d%H%M%S',time.localtime())   + '===' + useroot + '===' + UseLocalScript + '===' + Deployment + '===' + DeploymentStatus + '===' + Logcmd + '===' + stderr + '===' + stdout)
		T.close()
	except Exception,e:
		print "Warning: Can't write log. (%s)" % e
def LocalScriptUpload(ip,port,username,password,s_file,d_file):
	try:		
		t = paramiko.Transport((ip,port))
                if UseKey=='y':
                        KeyPath=os.path.expanduser('~/.ssh/id_rsa')
                        key=paramiko.RSAKey.from_private_key_file(KeyPath)
			t.connect(username = username,pkey=key)
		else:
			t.connect(username = username,password = password)
		sftp = paramiko.SFTPClient.from_transport(t)
		ret=sftp.put(s_file,d_file)
	except Exception,e:		
		print "LocalScript inited Failed",e
		return False	
	else:
		t.close()
def InitInstall():
	if not os.path.isdir("/cheung"):
		if getpass.getuser()=="root":
			os.system("mkdir -p /cheung/logs /cheung/.db/.key  /cheung/conf /cheung/bin")
		else:
			print "Sorry Must be as root install !"
			sys.exit(1)
	if not os.path.isfile('/cheung/conf/cheung.conf'):
		T=open('/cheung/conf/cheung.conf','w')
		T.write("""[AUTO_SSH]
Servers=localhost,127.0.0.1,www.baidu.com
Username=YourServerCount
Password=Yourcount-Password
Useroot=N
#localhost_User=apache
#localhost_Password=apache-password
#localhost_Port=222
#如果您的每个服务器的账户对应的密码不是都一样，那么您可以使用这个配置
#Passwordroot=root-password
#Timeout=10
RunMode=M
UseKey=n
Deployment=n
#ListenFile=/var/log/messages
#ListenTime=60
#ListenChar=Server startup
Port=22""")
		T.close()



def SSH_cmd(ip,username,password,port,cmd,UseLocalScript):
	
	global All_Servers_num,All_Servers_num_all,All_Servers_num_Succ,Done_Status,Global_start_time
	start_time=time.time()
	ResultSum=''
	ResultSumLog=''
	DeploymentStatus=False
	DeploymentInfo=None
	try:
		o=None
		err=None
		ssh=paramiko.SSHClient()
		if UseKey=='y':
	
			KeyPath=os.path.expanduser('~/.ssh/id_rsa')
			###
			key=paramiko.RSAKey.from_private_key_file(KeyPath)
			ssh.load_system_host_keys()
			ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			ssh.connect(ip,port,username,pkey=key)  
		else:
			ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			ssh.connect(ip,port,username,password)
		if Deployment=='y':
			stdin,stdout,stderr=ssh.exec_command(ListenLog+cmd)
		else:
			stdin,stdout,stderr=ssh.exec_command(cmd)
		out=stdout.readlines()
		All_Servers_num += 1
		print "\r"
		for o in out:
			ResultSum +=o
			ResultSumLog +=o.strip('\n') + '\\n'
		
		error_out=stderr.readlines()
		for err in error_out:
			ResultSum +=err
			ResultSumLog +=err.strip('\n') + '\\n'
		if err:
			ResultSum_count="\033[1m\033[1;32m+OK %s (%0.2f Sec, All %d Done %d \033[1m\033[1;31mCmd:Failed\033[1m\033[1;32m)\033[1m\033[0m" % (ip,float(time.time()-start_time),All_Servers_num_all,All_Servers_num)
			out='Null\n'
			if Deployment=='y':
				DeploymentStatus=False
			Write_Log(ip,ResultSumLog.strip('\\n'),out,cmd,LogFile,'N',username,UseLocalScript,Deployment,DeploymentStatus)
		else:
			error_out='NULL'
			ResultSum_count="\033[1m\033[1;32m+OK %s (%0.2f Sec, All %d Done %d  Cmd:Sucess)\033[1m\033[0m" % (ip,float(time.time()-start_time),All_Servers_num_all,All_Servers_num)
			All_Servers_num_Succ+=1
			if Deployment=='y':
				print  "Wating %s deployment (for %d Sec)..." % (ip,ListenTime)
				T=LogCollect.LogCollect(ip,port,username,password,"""grep  -E "%s"  %s -q && echo  -n 'DoneSucc'""" % (ListenChar,DeploymentFlag),ListenTime,UseKey)
				if T:
					DeploymentStatus=True
				else:
					DeploymentInfo="Main commands excuted success, But deployment havn't check suncess info (%s) " %(ListenChar)
					DeploymentStatus=False
					

			Write_Log(ip,error_out,ResultSumLog.strip('\\n') + '\n',cmd,LogFile,'N',username,UseLocalScript,Deployment,DeploymentStatus)

		Show_Result=ResultSum + '\n' +ResultSum_count
		Format_Char_Show.Show_Char(Show_Result,0)  
	except Exception,e:
		All_Servers_num += 1
		ResultSum_count="\n\033[1m\033[1;31m-ERR %s %s (%0.2f Sec All %d Done %d)\033[1m\033[0m\a"	% (ip,e,float(time.time() - start_time),All_Servers_num_all,All_Servers_num)
		Show_Result= ResultSum+ResultSum_count
		Format_Char_Show.Show_Char(Show_Result,1)  
		Write_Log(ip,str(e),'NULL\n',cmd,LogFile,'N',username,UseLocalScript,Deployment,DeploymentStatus)
	else:
		ssh.close()
	if Deployment=='y' and not  DeploymentStatus:
		while True:
			TT=raw_input("%s Deployment not Success (%s) want contiue deployment next server (yes/no) ? " %(ip,DeploymentInfo))
			if TT=='yes':
				break
			elif TT=='no':
				sys.exit(1)
	if All_Servers_num == All_Servers_num_all: #这里防止计数器永远相加下去
		print "+Done (Succ:%d,Fail:%d, %0.2fSec GUN/Linux Cheung Kei-Chuen All Right Reserved)" % (All_Servers_num_Succ,All_Servers_num_all-All_Servers_num_Succ,time.time()-Global_start_time)
		All_Servers_num =0
		All_Servers_num_Succ=0
		Done_Status='end'

def Read_config(file="/cheung/conf/cheung.conf"):
	global Username,Password,Servers,Port,PsswordType,Useroot,Passwordroot,All_pass,All_user,All_port,Timeout,RunMode,UseKey,Deployment,ListenTime,ListenFile,ListenChar
	c=ConfigParser.ConfigParser()
	try:
		c.read(file)
	except ConfigParser.ParsingError,e:
		print "The %s format Error.\a\n\t%s" % (file,e)
		sys.exit(1)
	try:
		Servers=c.get("AUTO_SSH","Servers")
	except Exception,e:
		print "No Servers"
		sys.exit()
	try:
		UseKey=c.get("AUTO_SSH","UseKey").lower()
	except Exception,e:
		UseKey='n'
	
	if UseKey=='n':
		try:
			Password=c.get("AUTO_SSH","Password")
		except Exception,e:
			print "No Password"
			sys.exit()
		try:
			Username=c.get("AUTO_SSH","Username")
		except Exception,e:
			print "No Username"
			sys.exit()
	else:
		Password=None
		Username=getpass.getuser()
	try:
		Port=int(c.get("AUTO_SSH","Port"))
	except Exception,e:
		Port=22
		print "No Port default 22"
	try:
		RunMode=c.get("AUTO_SSH","RunMode").upper()
	except Exception,e:
		RunMode='M'
		print "No Runmode default Mutiple(M)"
	try:
		Deployment=c.get("AUTO_SSH","Deployment").lower()
		if Deployment=='y':
			try:
				ListenFile=c.get("AUTO_SSH","ListenFile")
			except Exception,e:
				print "In deployment mode ,must be specify ListenFile"
				sys.exit(1)
			try:
				ListenTime=int(c.get("AUTO_SSH","ListenTime"))
			except Exception,e:
				print  "Warning : ListenTime default is 60"
				ListenTime=60
			try:
				ListenChar=c.get("AUTO_SSH","ListenChar")
			except Exception,e:
				print "In deployment mode ,must be specify ListenChar"
				sys.exit(1)
	except Exception,e:
		Deployment='n'
	if RunMode=='M' and Deployment=='y':
		print "In Mutiple-threading mode,do not support deployment mode!"
		sys.exit(1)
			
		
	try:
		Useroot=c.get("AUTO_SSH","Useroot").lower()
		if Useroot=='y' and Deployment=='y':
			print "In Deployment no support su  - root "
			sys.exit(1)
	except Exception,e:
		Useroot="n"
	try:
		Timeout=c.get("AUTO_SSH","Timeout")
		try:
			Timeout=socket.setdefaulttimeout(int(Timeout))
		except Exception,e:
			Timeout=10
			print "Warning: Timeout's Value Error, default=10 (Sec)"
	except Exception,e:
		Timeout=socket.setdefaulttimeout(10)

	if Useroot == "y":
		try:
			Passwordroot=c.get("AUTO_SSH","Passwordroot")
		except Exception,e:
			print "Need root's Password"
			sys.exit(1)
	All_pass={}
	All_user={}
	All_port={}
	for t_server in Servers.split(","):
		try:
			t=c.get("AUTO_SSH","%s_Password" % (t_server))
			All_pass["%s_Password" % (t_server)]=t
		except Exception,e:
			pass
		try:
			t=c.get("AUTO_SSH","%s_Username" % (t_server))
			All_user["%s_Username" % (t_server)]=t
		except:
			pass
		try:
			t=c.get("AUTO_SSH","%s_Port" % (t_server))
			All_pass["%s_Port" % (t_server)]=t
		except:
			pass
	print "Servers:%d|RunMode:%s|UseKey:%s|Deployment:%s  \n" % (len(Servers.split(',')),RunMode,UseKey,Deployment)


def Upload_file(ip,port,username,password):
	start_time=time.time()
	global All_Servers_num,All_Servers_num_all,All_Servers_num_Succ,Global_start_time
	try:
		t = paramiko.Transport((ip,port))
		if UseKey=='y':
                        KeyPath=os.path.expanduser('~/.ssh/id_rsa')
                        key=paramiko.RSAKey.from_private_key_file(KeyPath)
			try:
				t.connect(username = username,pkey=key)
			except EOFError:
				print "Try use RunMode=D"
			##########################################
		else:
			try:
				t.connect(username = username,password = password)
			except EOFError:
				print "Try use RunMode=D"
		sftp = paramiko.SFTPClient.from_transport(t)
		New_d_file=re.sub('//','/',d_file + '/')+ os.path.split(s_file)[1]
		Bak_File=New_d_file+'.bak'+"%d" % (Global_start_time)
		try:
			sftp.rename(New_d_file,Bak_File)
			SftpInfo="Warning: %s %s  already exists, and has been backed up to %s \n" % (ip,New_d_file,Bak_File)
		except Exception,e:
			SftpInfo='\n'
		ret=sftp.put(s_file,New_d_file)
		All_Servers_num += 1
		All_Servers_num_Succ+=1
		print SftpInfo + "\033[1m\033[1;32m+OK %s (%0.2f Sec  All %d Done %d)\033[1m\033[0m" % (ip,time.time() - start_time,All_Servers_num_all,All_Servers_num)
	except Exception,e:
		All_Servers_num += 1
		print "\033[1m\033[1;31m-ERR %s %s(%0.2f Sec,All %d Done %d)\033[1m\033[0m" % (ip,e,float(time.time() -start_time),All_Servers_num_all,All_Servers_num)	
	else:
		t.close()

	if All_Servers_num_all == All_Servers_num:
		print "+Done (Succ:%d,Fail:%d, %0.2fSec GUN/Linux Cheung Kei-Chuen All Right Reserved)" % (All_Servers_num_Succ,All_Servers_num_all-All_Servers_num_Succ,time.time()-Global_start_time)
		All_Servers_num =0
		All_Servers_num_Succ=0


def Download_file_regex(ip,port,username,password):
	global All_Servers_num_all,All_Servers_num,All_Servers_num_Succ
	start_time=time.time()
	try:
		t = paramiko.Transport((ip,port))
                if UseKey=='y':
                        KeyPath=os.path.expanduser('~/.ssh/id_rsa')
                        key=paramiko.RSAKey.from_private_key_file(KeyPath)
			t.connect(username = username,pkey=key)
		else:
			t.connect(username = username,password = password)
		sftp = paramiko.SFTPClient.from_transport(t)
		t_get=sftp.listdir(os.path.dirname(s_file))
		for getfilename in t_get:
			if re.search(os.path.basename(s_file),getfilename):
				download_fullpath=os.path.join(os.path.dirname(s_file),getfilename)
				try:
					if os.path.isfile(os.path.join(d_file,getfilename)):
						ret=sftp.get(download_fullpath,"%s_%s" % (os.path.join(d_file,getfilename),ip))
					else:
						ret=sftp.get(download_fullpath,os.path.join(d_file,getfilename))
					print  '\t\033[1m\033[1;32m+OK %s : %s' % (ip,download_fullpath)
				except Exception,e:
					print  '\t\033[1m\033[1;33m-Failed %s : %s %s' % (ip,download_fullpath,e)
		All_Servers_num +=1
		All_Servers_num_Succ+=1
		print "\033[1m\033[1;32m+OK %s (%0.2f Sec All %d Done %d)\033[1m\033[0m" % (ip,float(time.time()) - start_time,All_Servers_num_all,All_Servers_num)
	except Exception,e:
		All_Servers_num +=1
		print "\033[1m\033[1;31m-ERR %s %s (%0.2f Sec All %d Done %d)\033[1m\033[0m" % (ip,e,float(time.time() - start_time),All_Servers_num_all,All_Servers_num)
	else:
		t.close()
	if All_Servers_num_all == All_Servers_num:
		All_Servers_num = 0
		print "+Done (Succ:%d,Fail:%d, %0.2fSec GUN/Linux Cheung Kei-Chuen All Right Reserved)" % (All_Servers_num_Succ,All_Servers_num_all-All_Servers_num_Succ,time.time()-Global_start_time)
		

def Download_file(ip,port,username,password):
	global All_Servers_num_all,All_Servers_num,All_Servers_num_Succ
	start_time=time.time()
	try:
		t = paramiko.Transport((ip,port))
                if UseKey=='y':
                        KeyPath=os.path.expanduser('~/.ssh/id_rsa')
                        key=paramiko.RSAKey.from_private_key_file(KeyPath)
			t.connect(username = username,pkey=key)
               	else:
			t.connect(username = username,password = password)
		sftp = paramiko.SFTPClient.from_transport(t)
		New_d_file=re.sub('//','/',d_file + '/')
		ret=sftp.get(s_file,"%s%s_%s" % (New_d_file,os.path.basename(s_file),ip))
		All_Servers_num +=1
		All_Servers_num_Succ+=1
		print "\033[1m\033[1;32m+OK %s (%0.2f Sec All %d Done %d)\033[1m\033[0m" % (ip,float(time.time()) - start_time,All_Servers_num_all,All_Servers_num)
	except Exception,e:
		All_Servers_num +=1
		print "\033[1m\033[1;31m-ERR %s %s (%0.2f Sec All %d Done %d)\033[1m\033[0m" % (ip,e,float(time.time() - start_time),All_Servers_num_all,All_Servers_num)
	else:
		t.close()
	if All_Servers_num_all == All_Servers_num:
		All_Servers_num = 0
		print "+Done (Succ:%d,Fail:%d, %0.2fSec GUN/Linux Cheung Kei-Chuen All Right Reserved)" % (All_Servers_num_Succ,All_Servers_num_all-All_Servers_num_Succ,time.time()-Global_start_time)





	
def Main_p(Server,Port,Username,Password):
	global s_file,d_file,All_Servers_num_Succ,LocalScript,Global_start_time
	global All_Servers_num_all,All_Servers_num
	All_Servers_num_all=len(Servers.split(','))
	All_Servers_num    =0
	All_Servers_num_Succ=0
	try:
		from optparse import OptionParser
		p=OptionParser()
		p.add_option("-t","--excute-type",help="""Description: select excute type
			Parameter: [cmd|download|upload]
				cmd     : Excute Shell Command
				download: Download file
				upload  : Upload file
			
			Example: %s -t cmd""" % sys.argv[0])
		p.add_option("-s","--source-file",help="""Description:	Specific Source file  path
			Example:
				%s  -t upload   -s /local/file  -d /remote/dir
				%s  -t download -s /remote/file -d /local/dir""" %(sys.argv[0],sys.argv[0]))
		p.add_option("-d","--destination-file",help="""
			Description: Specific a destination directory Path""")
		p.add_option("-r","--regex",action='store_false',default=True,help="""
			Description: Use regex match filename
			Example: 
			%s  -t download -s '^/remote/tomcat/logs/localhost_2015-0[1-3].*log$' -d  /local/dir/

			Notice: This parameter applies only to download""" % sys.argv[0])
		p.add_option("-f","--File",action='store_false',default=True,help="""Use LocalScript File""")
		(option,args)=p.parse_args()
		if option.File :
			LocalScript='n'
			#print 'no use'
		else:
			LocalScript='y'
			#print 'use'
			
		if option.excute_type == "cmd":
			Excute_cmd()
		elif option.excute_type == "upload":
			if option.source_file and option.destination_file:
				s_file=option.source_file
				d_file=option.destination_file
			else:
				print "Upload File"
				s_file=raw_input("Local Source Path>>>")
				d_file=raw_input("Remote Destination Full-Path>>>")
			Global_start_time=time.time()
			for s in Servers.split(","):
				try:
						t_password=All_pass["%s_Password" % (s)]
				except:
						t_password=Password
				try:
						t_username=All_user["%s_Username" % (s)]
				except:
						t_username=Username
				try:
						t_port=All_port["%s_Port" % (s)]
				except:
						t_port=Port
				if RunMode.upper()=='M':
					a=threading.Thread(target=Upload_file,args=(s,t_port,t_username,t_password))
					a.start()
				else:
					Upload_file(s,t_port,t_username,t_password)
		elif option.excute_type == "download":
			if option.source_file and option.destination_file:
				s_file=option.source_file
				d_file=option.destination_file
			else:
				print "Download File"
				s_file=raw_input("Remote Source Full-Path>>>")
				d_file=raw_input("Local Destination Path>>>")
			if not os.path.isdir(d_file):
				print 'Recv location must be a directory'
				sys.exit(1)
			Global_start_time=time.time()
			for s in Servers.split(","):
				
				try:
					t_password=All_pass["%s_Password" % (s)]
				except:
					t_password=Password
				try:
					t_username=All_user["%s_Username" % (s)]
				except:
					t_username=Username
				try:
					t_port=All_port["%s_Port" % (s)]
				except:
					t_port=Port

				if option.regex:
					a=threading.Thread(target=Download_file,args=(s,t_port,t_username,t_password))
				else:
					a=threading.Thread(target=Download_file_regex,args=(s,t_port,t_username,t_password))
				a.start()
		elif not option.excute_type:
			Excute_cmd()
			sys.exit(0)
		else:
			print "Parameter does not currently support\t(%s)\a" % (option.excute_type)
			Excute_cmd()
	except KeyboardInterrupt:
		print "exit"
	except EOFError:
		print "exit"

def Excute_cmd_root(s,Port,Username,Password,Passwordroot,cmd,UseLocalScript):
	global All_Servers_num_all,All_Servers_num,All_Servers_num_Succ,Done_Status,bufflog
	Done_Status='start'
	bufflog=''
	start_time=time.time()
	ResultSum=''
	Result_status=False
	try:
		t=paramiko.SSHClient()
                if UseKey=='y':
			KeyPath=os.path.expanduser('~/.ssh/id_rsa')
                        key=paramiko.RSAKey.from_private_key_file(KeyPath)
                        t.load_system_host_keys()
			t.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                        t.connect(s,Port,Username,pkey=key) 
                else:
			t.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			t.connect(s,Port,Username,Password)
		ssh=t.invoke_shell()
		ssh.send("LANG=zh_CN.UTF-8\n")
		ssh.send("export LANG\n")
		ssh.send("su - root\n")
		buff=''
		while not re.search("Password:",buff) and not re.search("：", buff):
			resp=ssh.recv(9999)
			buff += resp
		#print buff #show su result
		ssh.send("%s\n" % (Passwordroot))
		buff1=''
		while True:
			resp=ssh.recv(500)
			buff1 += resp
			if  re.search('su:',buff1):
				#print "\033[1;31m-ERR su Failed  %s\033[0m" % (s)
				break
			else:
				if re.search('# *$',buff1):
					Result_status=True
                			All_Servers_num_Succ+=1
					break
		if Result_status:
			ssh.send("%s\n" % (cmd))
			buff=""
			bufflog=''
			while not buff.endswith("# "):
				resp=ssh.recv(9999)
				buff  += resp
				bufflog  += resp.strip('\r\n') + '\\n'
			t.close()
			All_Servers_num += 1
			ResultSum=buff + "\n\033[1m\033[1;32m+OK %s (%0.2f Sec All %d Done %d)\033[1m\033[0m\n" % (s,float(time.time() - start_time),All_Servers_num_all,All_Servers_num)
			
			bufflog_new=''
			for t in bufflog.split():
				if t==cmd:
					continue
				bufflog_new+=t
			bufflog=bufflog_new
		else:
			All_Servers_num += 1
			ResultSum=buff + "\n\033[1m\033[1;31m-ERR Su Failed %s (%0.2f Sec All %d Done %d)\033[1m\033[0m\n" % (s,float(time.time() - start_time),All_Servers_num_all,All_Servers_num)
			
	except Exception,e:
		All_Servers_num += 1
		Result_status=False
		ResultSum="\n\033[1m\033[1;31m-ERR %s %s (%0.2f Sec All %d Done %d)\033[1m\033[0m\a"   % (e,s,float(time.time() - start_time),All_Servers_num_all,All_Servers_num)
		bufflog=str(e)
	if Result_status:
		Write_Log(s,'NULL',bufflog.strip('\\n') + '\n',cmd,LogFile,'Y',Username,UseLocalScript,'N','N')
		Format_Char_Show.Show_Char(ResultSum,0)
	else:
		Write_Log(s,bufflog.strip('\\n'),'NULL\n',cmd,LogFile,'Y',Username,UseLocalScript,'N','N')
		Format_Char_Show.Show_Char(ResultSum,1)
	if All_Servers_num_all == All_Servers_num:
		print "+Done (Succ:%d,Fail:%d, %0.2fSec GUN/Linux Cheung Kei-Chuen All Right Reserved)" % (All_Servers_num_Succ,All_Servers_num_all-All_Servers_num_Succ,time.time()-Global_start_time)
                All_Servers_num =0
                All_Servers_num_Succ=0
		Done_Status='end'

def Excute_cmd():
	global All_Servers_num_all,All_Servers_num,All_Servers_num_Succ,Done_Status,Logcmd,ListenLog,Global_start_time
	Done_Status='end'
	All_Servers_num_all=len(Servers.split(','))
	All_Servers_num    =0
	All_Servers_num_Succ=0
	UseLocalScript='N' #
	while True:
		if Done_Status=='end':
			if Useroot == "y":
				cmd=raw_input("root CMD>>>>")
			else:
				cmd=raw_input("CMD>>>>")
				
		else:
			time.sleep(0.05)
			continue
		if cmd == "exit":
			sys.exit(0)
		if re.search('^ *[Ff][Ll][Uu][Ss][Hh] *[Ll][Oo][Gg][Ss] *$',cmd):
			try:
				Log_Flag=time.strftime('%Y%m%d%H%M%S',time.localtime())
				shutil.move('/cheung/logs/auto_ssh.log','/cheung/logs/auto_ssh%s.log' % Log_Flag)
				print "+OK"
				continue
			except Exception,e:
				print "Waring : %s Failed (%s)" % (cmd,e)
				continue
		if cmd=="reload":
			Read_config()
			print "+OK"
			continue
			
		
		if not cmd :
			continue
		Global_start_time=time.time()
		for s in Servers.split(","):
			
			try:
				t_password=All_pass["%s_Password" % (s)]
			except:
				t_password=Password
			try:
				if UseKey=="y":
					t_username=Username
				else:
					t_username=All_user["%s_Username" % (s)]
			except:
				t_username=Username
			try:
				t_port=All_port["%s_Port" % (s)]
			except:
				t_port=Port
			if LocalScript.lower() == 'y':
				if not os.path.isfile(cmd):
					print "Eroor: %s ScriptFile is not fond " % cmd
					#continue
					break
				else:
					ScriptFlag=str(random.randint(999999999,999999999999))
					d_file='/tmp/' + os.path.basename(cmd) + ScriptFlag
					LocalScriptUpload(s,t_port,t_username,t_password,cmd,d_file)
					Newcmd="""chmod a+x %s;%s;rm -f %s""" % (d_file,d_file,d_file)
					Logcmd=cmd
					UseLocalScript='Y'
			else:
				Newcmd=cmd
				Logcmd=cmd
			
			Done_Status='start'
			if RunMode.upper()=='M':
				if Useroot=='y':
					a=threading.Thread(target=Excute_cmd_root,args=(s,Port,t_username,t_password,Passwordroot,Newcmd,UseLocalScript))
					a.start()
				else:
					
					a=threading.Thread(target=SSH_cmd,args=(s,t_username,t_password,t_port,Newcmd,UseLocalScript))
					a.start()
					
			else:
				if Useroot=='y':
					Excute_cmd_root(s,Port,t_username,t_password,Passwordroot,Newcmd,UseLocalScript)
				else:
					if Deployment=='y':
						ListenLog="""if [ ! -r %s ] ; then echo -e '\033[1m\033[1;31m-ERR ListenFile %s  not exists,so do not excute commands !\033[1m\033[0m\a ' 1>&2 ;exit;else nohup tail -n 0 -f  %s  2&>%s &   fi;""" % (ListenFile,ListenFile,ListenFile,DeploymentFlag)
						SSH_cmd(s,t_username,t_password,t_port,Newcmd,UseLocalScript)
					else:
						SSH_cmd(s,t_username,t_password,t_port,Newcmd,UseLocalScript)
							
			############################################################################################
if  __name__=='__main__':
	InitInstall()
	Read_config()
	Main_p(Servers,Port,Username,Password)
