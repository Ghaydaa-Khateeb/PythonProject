import argparse
import optparse
import pathlib
import os.path
import os,shutil
import json
from pathlib import Path
from os import path
import logging
from random import seed
from random import randint
from optparse import OptionParser
import sys
# result dictionary
result = {"Grep" : [] , "categorize" : [] , "Mv_last" : []}

# ---------------------- Grep Class 
# we implement the commands as classes in case of factory design pattern concept
class Grep:
	# allF : all files in the gived dirictory and its sub directories
	def __init__(self , idx , fileName , Dir , allF ):
		super().__init__()
		self.checkExistance(idx , fileName , allF , Dir)	
    # check if the file exist in the list of all files
	def checkExistance(self ,idx ,  fileName  , allF , Dir):
		if fileName in allF:
			result["Grep"].append("True")
		else:
			result["Grep"].append("False")
#--------------------------- Categorization class
class Categorize:
	def __init__(self ,idx ,  Dir , Threshold_size):
		super().__init__()
		self.splitF(idx , Dir , Threshold_size)
	def splitF(self ,idx ,  Dir , Threshold_size):
		wholeList = os.listdir(Dir)
		listOfFiles = list()
		for f in wholeList:
			if f.find('.') != -1:
				listOfFiles.append(f)
		lessPath = Dir + "\\" + "less"
		morePath = Dir + "\\" + "more"		
		if not os.path.isdir(lessPath):
			os.makedirs(lessPath)
		if not os.path.isdir(morePath):
			os.makedirs(morePath)
		for f in listOfFiles:
			fileStatus = os.stat(Dir + '\\' + f)
			fileSize = round(fileStatus.st_size / 1024) # converting to KB
			ThVal = int(Threshold_size[0 : len(Threshold_size) - 2])
			if Threshold_size[len(Threshold_size) - 2 : ] == "MB":
				ThVal = ThVal * 1024
			elif Threshold_size[len(Threshold_size) - 2 : ] == "GB":
				ThVal = ThVal * 1024 * 1024
			if fileSize >= ThVal :
				shutil.move(Dir + "\\" + f , morePath)
			else:
				shutil.move(Dir + "\\" + f , lessPath)
		if len(listOfFiles) == 0:
			result["categorize"].append("False")
		else:
			result["categorize"].append("True")		

# ---------------------- Mv_lastn class
class MoveDir:
	# move the most recent files to a specified directory
	# we assume that the most recent may be the most recent modified or created or updated and so on
	# if you want to specify such folder add a \ after its name
	# for example if you want to move the most recent file in the folder linuxLab
	# make the source directory as the following C:\ ...\linuxLab\
	# and the same with destination
	def __init__(self ,idx , srcDir , desDir):
		super().__init__()
		self.makeMove(idx , srcDir , desDir)
	def makeMove(self , idx , srcDir , desDir):
		res = list()
		try:
			paths = sorted(Path(srcDir).iterdir(), key=os.path.getmtime)
			for k in paths:
				fi = path.split(k)
				if fi[1].find('.') != -1:
					res.append(fi[1])
			mostRecent = res[len(res) - 1]
			shutil.move(srcDir + "\\" + mostRecent , desDir)
			result["Mv_last"].append("True")
			for i in res:
				print(i)
		except:
			result["Mv_last"].append("False")	


def Factory(command):
	commands = {
      "Grep" : Grep,
      "Categorize":Categorize,
      "Mv_last":MoveDir
	}
	return commands[command]()

# recurcive function to fiind all files in the directory and its sub directory				
def allFiles(Dir):
	LOF = os.listdir(Dir)
	files = list()
	for f in LOF:
		path1 = os.path.join(Dir , f)
		if os.path.isdir(path1):
			files += allFiles(path1)
		else:
			files.append(path1)
	return files	

# parser function
def Parser():
	usage = "usage: %prog [options] arg"
	parser = OptionParser(usage)
	parser.add_option("-s", dest="script", help="script input file", metavar="FILE")
	parser.add_option("-o", action="store", dest="verbose", default=True,help="log or csv output file")
	(options, args) = parser.parse_args()
	parsing = list()
	parsing.append(options.script)
	parsing.append(options.verbose)
	return parsing


def main():
	jsonFile = open("configuration.json","r")
	data = json.loads((jsonFile.read()))
	jsonFile.close()	
	Threshold_size = data["Threshold_size"]
	scripts = []
	allF = list()
	listInOut = []
	parsingList = Parser()
	if len(parsingList) == 2 and parsingList[0] != None and parsingList[1] != None:
		try:
			inputF = parsingList[0]
			if ".txt" in inputF:
				inp = path.split(inputF)
				inputF = inp[0]
			outputF= parsingList[1]
			with open(inputF + "\\"+"script.txt","r") as f:
				temp = f.readlines()
				scripts = temp
			maxCommands = data["Max_commands"]
			idx = 0
			for i in scripts:
				if(idx < int(maxCommands)):
					temp = i.split(' ')
					if temp[0] == "Grep":
						finalPath = path.split(temp[2])
						pth = finalPath[0]
						res = list()
						allF = allFiles(pth)
						for k in allF:
							p = path.split(k)
							res .append(str(p[1]))
						GrepO = Grep(idx , str(temp[1]) , pth,res)
					elif temp[0] == "Mv_last" :
						source = path.split(temp[1])
						destination = path.split(temp[2])
						MvO = MoveDir(idx , source[0]+"\\" , destination[0]+"\\")
					elif temp[0] == "Categorize":
						Dir = path.split(temp[1])
						CaO = Categorize(idx , Dir[0] , Threshold_size)
					idx = idx + 1	
				else:
					print("STOP")
			if data["output"] == ("log".lower()) :
				Logging(result , outputF)
				DealingWithMaxLogFiles(int(data["Max_log_files"]) , outputF)
			else:
				CSVoutput(result , outputF)

			if data["Same_dir"] == "True":				
				PassPath = outputF + "\\" + "PASS"
				print(PassPath)
				print(outputF)
				if not os.path.isdir(PassPath):
					os.makedirs(PassPath)				
				

		except Exception as e:
			print("ERROR , Enter a correct input path .. ")		
	else:
		print()
		print("-- > Enter the required inputs correctly in format of <The name of the main project> -s <input path> -o <output path>")		


def Logging(dict , outputF):
	try:
		PASS = "PASS"
		for key , value in dict.items():
			for j in value:
				if j == "False":
					PASS = "FAILED"
		files = os.listdir(outputF)
		logF = list()
		for i in files:
			if ".log" in i:
				logF.append(i)
		temp = ""
		mx = 0
		for i in logF:
			if int(''.join(filter(str.isdigit, i))) >= mx:
				temp = i
				mx = int(''.join(filter(str.isdigit, i)))
		if temp == "":
			temp = "0"
		idx = int(''.join(filter(str.isdigit, temp)))
		idx = idx + 1	
		logging.basicConfig(filename=outputF+"\\"+PASS+"output"+str(idx)+".log" , filemode="w" , level=logging.INFO)
		for key , value in dict.items():
			for j in value:
				logging.info(key + " : " + j)
	except:
		print("ERROR , Enter a correct output path ..")			


def DealingWithMaxLogFiles(maxLogFiles , outputF):
	files = os.listdir(outputF)
	logF = list()
	for i in files:
		if ".log" in i:
			logF.append(i)
	idx = 1		
	Flag = False
	if len(logF) > maxLogFiles :
		while True:
			for i in logF:
				if idx == int(''.join(filter(str.isdigit, str(i)))):
					os.remove(outputF + "\\" + i)
					Flag = True
					break
			if Flag == True:
				break		
			idx = idx + 1


def CSVoutput(dict , outputF):
	try:
		PASS = "PASS"
		for key , value in dict.items():
			for j in value:
				if j == "False":
					PASS = "FAILED"
		original_stdout = sys.stdout
		with open(outputF+"\\"+PASS+'output.csv','w') as f:
			sys.stdout = f
			for key , value in dict.items():
				for j in value:
					print(key + " : " + j)
			sys.stdout = original_stdout	
	except:
		print("Enter a correct path")			

	
if __name__ == '__main__':
	main()