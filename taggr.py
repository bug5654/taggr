#imports in near-alphabetical orders
import argparse
import datetime
import json
import sqlite3
import sys


__VERBOSE_DEBUG__= False		#flag to turn on debug printing, True = MASSIVE OUTPUT, turn on scrollback

def dprint(*args):
	'''debug printing'''
	if __VERBOSE_DEBUG__ == True:
		print(*list(args))	#have to unpack args list to use same arguments as print



#TOdo: IMPLEMENT: TAG-8 admin log system instead of just printing to screen
class taggr():
	__VERSION__ = "0.1.4"		# Public version tag, made a string for being able to adhere to 1.0.3rc12 et al
	outputFn = print 			# function to send output to for display to user
	outputFnArgs = 1			# whether to send additional message details to outputFn valid values = {1,2}
	dbName = None 				# temp storage to prevent requiring constant lookup
	logDict = None 				# dictonary of filenames to place logs at
	logConn = None 				# dictionary of current connections by log type
	logTimeStamp = False		# log the timestamp

	# Separate output into it's own function
	def output(self, msg, type="inform"):
		'''Generalized output function for multi-interface'''
		# current types = {inform[ation], warn[ing], err[or]}
		# logType = {[None], admin}
		# outputFn = function to send the output [print]
		# outputFnArgs = what details to sent to the outputFn {[1],2}
		# 	1= outputFn(message) alone, 2 = outputFn(message, type)
		# logDict = filenames to store logs of different types
		# 	e.g. logDict = {"admin":"admin.txt", "error":"errs.txt"}
		# 	While running, filenames should be replaced with open() references to ensure proper closing
		#	But serialized should contain only filenames, due to lValues changing with every run
		# TODO: TAG-18 admin log include regular expressions for copying to relevant files
		typeDict = {"a":"admin","admin":"admin","adminstration":"admin",\
			"i":"inform", "inform":"inform", "information":"inform",\
			"d":"debug", "debug":"debug",\
			"e":"error", "error":"error",\
			"w":"warn", "warn":"warn", "warning":"warn"}

		# logic for which log to put things in
		msgType = typeDict[type.lower()] if type.lower() in typeDict else msgType
		timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S') \
			if logTimeStamp == True else ""	# log the system time...or don't
		if msgType in logDict.keys():		# Do we want to log this somewhere?
			if msgType in logConn.keys():	# Is file already opened?
				f = logConn[msgType]		# utilize open connection
			else:							# file not actively open
				f = open(logDict[msgType],"a")	#open in append mode
				logConn[msgType] = f 		# store the connection for multiple r/w use
											# rely on GC to f.close() due to lack of destructors
			try:							
				f.write(msg+"\n")
			except:							# lost connection?
				f = open(logDict[msgType],"a")	# new connection
				f.write(msg+"\n")			# try again without exception handling
				logConn[msgType] = f

		# now to actually output, whether logged or no
		if outputFnArgs == 1:
			outputFn(msg)
		elif outputFnArgs == 2:
			outputFn(msg, type)




	#TODO: IMPLEMENT: TAG-9 create this as a class which keeps db, cursor, et al as members
	def db_name(self):		#returns the location of the current database
		'''Returns location of active DB'''
		try:
			f=open('.taggrprefs',"r")	#open pref file
		except IOError:
			self.switch_db("taggr.db")	#or set default
			f=open('.taggrprefs',"r")	#readonly fail possible, but should not be caught if cannot handle
		ans = json.load(f)
		try:
			f.close()
		except:
			dprint("could not close",f)
		return ans["Database"]


	def switch_db(self,db_filename):		#changes which DB reading/writing to
		'''Switches active database file'''
		try:
			f=open('.taggrprefs',"r")	#see if creates on open
		except IOError:
			dprint(".taggrprefs did not exist")
			x = {}
		else:
			x = json.load(f)	#get everything from existing file
			dprint("x:",x)
			f.close()
		x["Database"] = db_filename
		# x={"Database":db_filename,}
		f=open('.taggrprefs','w')
		dprint(".taggrprefs opened")
		json.dump(x,f)
		f.close()
		dprint("switch_db success")


	def check_and_create_tables(self,db,cursor):
		'''Creates sqlite tables if they do not exist, changing defaults not currently supported'''
		c = cursor	#compromise between clarity and line length
		# dprint("check_and_create_tables:\nself:",self,"\ndb:",db,"\ncursor:",cursor)
		try:	#tag table
			c.execute('CREATE TABLE tag (name TEXT UNIQUE NOT NULL)')	#"?" substitution not allowed for table names
			db.commit()
			dprint('tag created if needed')
		except:
			print("EXCEPTION RAISED TRYING TO CREATE tag IN",db,\
				"TABLE WAS NOT CREATED")
		try:	#tagxfile table
			c.execute(\
			'CREATE TABLE IF NOT EXISTS tagging (tagName TEXT,filePath TEXT)')
			db.commit()
			dprint('tagging created if needed')
		except:
			print("EXCEPTION RAISED TRYING TO CREATE",tagxfile_table,"IN",db,\
				"TABLE WAS NOT CREATED")
		try:	#file table
			c.execute(\
			'CREATE TABLE IF NOT EXISTS file (path TEXT NOT NULL UNIQUE,name TEXT)')
			db.commit()
			dprint('file created if needed')
		except:
			print("EXCEPTION RAISED TRYING TO CREATE",file_table,"IN",db,\
				"TABLE WAS NOT CREATED")


	def add_association(self,db,cursor,file,tag):
		'''adds the association to the database, helper fn'''
		#TODO: TAG-11 allow flexibility in table names?  Ed: seems like unnecessary complexity
		dprint("add_association: db:",db,"\tcursor:",cursor,"\n\tfile:",file,"\ttag:",tag)
		c = cursor	#line length
		c.execute("SELECT COUNT(name) FROM tag WHERE name = ?;",(tag,))	#check tag exists
		#if tag not present, create
		(tagNum,)=c.fetchone()
		dprint("\ttagNum:",tagNum)
		if tagNum==0:
			dprint("attempting insert tag")
			c.execute('INSERT INTO tag (name) VALUES (?)',(tag,))
		#check filepath in file table
		c.execute('SELECT COUNT(path) FROM file WHERE path = ?;',(file,))
		#if not present, create
		(fileNum,)=c.fetchone()
		dprint("\tfileNum:", fileNum)
		if fileNum==0:
			dprint("attempting insert file")
			c.execute('INSERT INTO file (path,name) VALUES (?,?)',(file,file))	#verify works
			#TODO: IMPLEMENT: TAG-12 name will be filename only not entire path
		#check association in association table
		c.execute('SELECT COUNT(filePath) FROM tagging WHERE filePath = ? AND tagName = ?;',(file,tag))
		(assocNum,)=c.fetchone()
		dprint("\tassocNum:",assocNum)
		#if not present add entry in tagxfile many:many table
		if assocNum==0:
			dprint("attempting insert association")
			c.execute('INSERT INTO tagging (filePath,tagName) VALUES (?,?)',(file,tag))	#verify works
		else:
			print("Association already exists!")
		#commit to ensure everything actually written
		dprint("\tcommitting to db")
		db.commit()
		if assocNum==0:
			print("The tag",tag,"was applied to file",file)		#non-silent success AFTER db.commit()


	def associate(self,tag,file):
		'''oversees process of associating file and tag'''
		dprint("file:",file,"tag:",tag,"db_name:", self.db_name())
		db = sqlite3.connect(self.db_name())		#open the db file, will create db if DNE
		cursor = db.cursor()
		self.check_and_create_tables(db, cursor)	#create the tables if needed
		self.add_association(db,cursor,file,tag.lower())	#associate the file and tag
		#tags forced lowercase to prevent multiple case of same tag in db
		#file left alone due to case-sensitive filesystems
		db.close()	#ensure everything written to db


	def output_association(self,lookup,half='tag'):
		'''writes out all the files/tags associated with specified tag/file respectively'''
		if half == 'tag':
			dprint("output_files: looking up all files associated with tag:",lookup)
			query = 'SELECT filePath FROM tagging WHERE tagName=?'
		elif half == 'file':
			dprint("output_files: looking up all files associated with tag:",lookup)
			query = 'SELECT tagName FROM tagging WHERE filePath=?'
		dprint("\tconnecting to:",self.db_name())
		db=sqlite3.connect(self.db_name())
		c = db.cursor()
		dprint("\tquery:",query)
		c.execute(query,(lookup,))		#becuase tags made lower() in storage to prevent confusion
		names=c.fetchall()
		if half == 'tag':
			dprint("names:",names)
			print("Files associated with tag",lookup,":")
		if half == 'file':
			dprint("names:",names)
			print("Tags associated with file",lookup,":")

		for f in names:
			print("\t",f[0])
		db.close()	#ensure no dangling pointers
		return names	#primarily for testing, but should be decoupled soon

	def output_version(self):
		'''outputs versioning string'''
		print('Taggr',self.__VERSION__)

#TODO: IMPLEMENT: TAG-13 getopt version
if __name__ == "__main__":		#if this is the script directly called to run, not as a library include
	parser = argparse.ArgumentParser(description="tag files with user-defined tags", add_help=False)
	#flag
	parser.add_argument("-h", "-?", "--help", action="store_true", help="show this help message and exit")	#help first, then alpha order
	parser.add_argument("-d", "--switchdb",metavar="DATABASE", help="use database specified (Not Yet Implemeted!)")
	parser.add_argument("-f", "--file", help="display all the tags associated with the file specified")
	parser.add_argument("-t", "--tagged",metavar="TAG", action="store", help="display files associated with the tag specified")
	#can't use --tag due to tag being an optional argument below, duplication BAD
	parser.add_argument("-v", "--version", action="store_true", help="display the taggr version number")
	parser.add_argument("-dg","--debug", action="store_true", help="display debug readout")	#would be deleted in release code?
	#positional args
	parser.add_argument("tag", type=str, help="tag to add to file, requires file to be specified", nargs="?")
	parser.add_argument("fileName", metavar="FILE", type=str, help="file to tag, requires tag to be specified", nargs="?")
	args=parser.parse_args()	#nothing happens without parse_args()
	dprint("CLI args after processing:",args,"\n")
	#process arguments
	tag = taggr()
	if args.debug == True:	#command-line debug print instead of in-code
		__VERBOSE_DEBUG__ = True

	if len(sys.argv) == 1 or args.help:		#user specified no arguments or -h
		parser.print_help()		#necessary for -? to be a valid help request
	elif (args.tag != None and args.fileName == None) or (args.tag == None and args.fileName != None):
		#need both or neither, but argparse can't handle this
		parser.print_usage()
		print(sys.argv[0],": error: both TAG and FILE arugments must be specified",sep="")
	elif args.switchdb != None:	#-d
		tag.switch_db(args.switchdb)
	elif args.file != None:		#-f
		tag.output_association(args.file,'file')
	elif args.tagged != None:	#-t
		tag.output_association(args.tagged,'tag')
	elif args.version:			#-v
		tag.output_version()
	else:						#only legal option left is <tag> <fileName>
		tag.associate(args.tag, args.fileName)