#!/usr/bin/python
VERSION=1.3
import os,sys,commands
def Get_Char(Char,i):
	Char=Char
	New_Char=[]
	for m in Char.split('\n'):
		New_Char.append('|' + m )
	b=Char.split('\n')
	Char_Len=[]
	for t in b:
		Char_Len.append(len(t))
	Max_Char_Len=sorted(Char_Len)[-1]
	return Max_Char_Len,New_Char
	
def Show_Line(Max_Char_Len,i=0,Flag='end'):
	while i<=Max_Char_Len+2:
		if i<=5 and Flag=='start':
			sys.stdout.write('+')
			i+=1
			continue
		
		sys.stdout.write('-')
		i+=1
def Show_Char(New_Char,Color_Status):
	if Color_Status==0:
		Color_Start="\033[1;32m"
		Color_End="\033[0m"
	else:
		Color_Start="\033[1;31m"
		Color_End="\033[0m"
	New_Char=New_Char
	print '\n\n'
	Len_and_Char=Get_Char(New_Char,i=0)
	print Color_Start
	Show_Line(Len_and_Char[0],i=0,Flag='start')
	print
	for t in Len_and_Char[1]:
		print t
	Show_Line(Len_and_Char[0],i=0)
	print Color_End
	print

if __name__=='__main__':
	Show_Char(sys.argv[1],0)

