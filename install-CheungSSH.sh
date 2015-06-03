#!/bin/bash
#Author=Cheung Kei-Chuen  张其川
#QQ=741345015
#如果您在使用过程中，遇到了一点点的问题，我都真诚希望您能告诉我！为了改善这个软件， 方便您的工作！
export LANG=zh_CN.UTF-8
echo  "Installing..."
rpm  -qa|grep gcc -q
if  [ $? -ne 0 ]
then
	echo  "您的系统当前没有gcc环境！"
	echo "现在为您安装GCC..."
	yum  install -y gcc >/dev/null 2>/dev/null
	if [ $? -ne 0 ]
	then
		echo  "安装GCC失败了，请手动安装gcc。"
		exit 1
	else
		echo "GCC安装成功!"
	fi

fi
rpm  -qa|grep python-devel -q
if  [ $? -ne 0 ]
then
	echo  "您的系统没有python-devle包，现在需要安装..."
	yum  install -y python-devel >/dev/null  2>/dev/null
	if  [ $? -ne  0 ]
	then
		echo "无法安装python-devel，请手动安装python-devel"
		exit 1
	else
		echo "安装python-devel成功！"
	fi
fi

wget --no-check-certificate https://pypi.python.org/packages/source/p/pycrypto/pycrypto-2.6.1.tar.gz
if [ $? -ne  0 ]
then
	echo "下载 https://pypi.python.org/packages/source/p/pycrypto/pycrypto-2.6.1.tar.gz 失败，请您使用浏览器下载安装"
	exit 1
else
	tar xf pycrypto-2.6.1.tar.gz;cd pycrypto-2.6.1;python setup.py install  2>/dev/null  >/null
	if  [ $? -ne  0 ]
	then
		echo  "安装pycrypto-2.6.1.tar.gz失败，请您解压这个压缩包后，手动安装"
		exit 1
	else
		echo  "安装pycrypto成功！"
	fi
fi




wget   --no-check-certificate  https://pypi.python.org/packages/source/p/paramiko/paramiko-1.9.0.tar.gz
if [ $? -ne  0 ]
then
	echo "下载https://pypi.python.org/packages/source/p/paramiko/paramiko-1.9.0.tar.gz 失败，请使用浏览器下载"
	exit 1
else
	tar xf paramiko-1.9.0.tar.gz;cd paramiko-1.9.0;python setup.py install  2>/dev/null  >/dev/null
	if  [ $? -ne 0 ]
	then
		echo "安装paramiko-1.9.0.tar.gz失败，请您手动解压后安。"
		exit 1
	else
		echo "安装paramiko成功"
	fi
fi
cd ../../;rm -fr paramiko* pycrypto*
echo "恭喜，您已经安装好了环境，接下来请您使用 ./`ls cheungSSH*` 启动程序"


