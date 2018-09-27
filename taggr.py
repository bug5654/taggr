#imports in near-alphabetical orders
import argparse
import sqlite3
import sys


#TODO: TAG-7 replace all concatenations in c.execute lines to c.execute(string,substitutions)


#TODO: TAG-13 check the if __name__ == "__main__": drive() instead of executing
#automatically to allow for library use


#TOdo: IMPLEMENT: TAG-8 admin log system instead of just printing to screen

<<<<<<< HEAD
__VERSION__ = "0.1.3"		#Public version tag, made a string for being able to adhere to 1.0.3rc12 et al
__VERBOSE_DEBUG__= True		#flag to turn on debug printing, True = MASSIVE OUTPUT, turn on scrollback
=======
__VERSION__ = "0.1.2"		#Public version tag, made a string for being able to adhere to 1.0.3rc12 et al
__VERBOSE_DEBUG__= False	#flag to turn on debug printing, True = MASSIVE OUTPUT, turn on scrollback
>>>>>>> parent of 2fca809... TAG-7 all cursor.execute('...%s...'.format(x)) changed to cursor.execute('...?...',(x,)) IAW python.org's DB-API2.0 SQLite documentation 11.13
ARGS_UNDERSTOOD = False		#flag for script being used correctly, without a massive if-else tree

def dprint(*args):
	'''debug printing'''
	if __VERBOSE_DEBUG__ == True:
		print(*list(args))	#have to unpack args list to use same arguments as print


#TODO: IMPLEMENT: TAG-9 create this as a class which keeps db, cursor, et al as members
def db_name():		#returns the location of the current database
	'''Returns location of active DB'''
	return 'taggrdb.db'	#TODO: IMPLEMENT: TAG-10 database file switching

def switch_db(db_filename):		#changes which DB reading/writing to
	'''Switches active database file'''
	print("Unimplemented: DB switch to ",db_filename)		#TODO: IMPLEMENT: TAG-10 after basic functionality useful

def check_and_create_tables(db,cursor,tag_table='tag',\
	tagxfile_table='tagging',file_table="file"):
	'''Creates sqlite tables if they do not exist, changing defaults not currently supported'''
	c = cursor	#compromise between clarity and line length
	try:	#tag table
		c.execute(\
		'CREATE TABLE IF NOT EXISTS {0} (name TEXT NOT NULL UNIQUE)'.format(tag_table))
		db.commit()
		dprint('{0} created if needed'.format(tag_table))
	except:
		print("EXCEPTION RAISED TRYING TO CREATE",tag_table,"IN",db,\
			"TABLE WAS NOT CREATED")
	try:	#tagxfile table
		c.execute(\
		'CREATE TABLE IF NOT EXISTS {0} (tagName TEXT,filePath TEXT)'.format(tagxfile_table))
		db.commit()
		dprint('{0} created if needed'.format(tagxfile_table))
	except:
		print("EXCEPTION RAISED TRYING TO CREATE",tagxfile_table,"IN",db,\
			"TABLE WAS NOT CREATED")
	try:	#file table
		c.execute(\
		'CREATE TABLE IF NOT EXISTS {0} (path TEXT NOT NULL UNIQUE,name TEXT)'.format(file_table))
		db.commit()
		dprint('{0} created if needed'.format(file_table))
	except:
		print("EXCEPTION RAISED TRYING TO CREATE",file_table,"IN",db,\
			"TABLE WAS NOT CREATED")


def add_association(db,cursor,file,tag):
	'''adds the association to the database, helper fn'''
	#TODO: TAG-11 allow flexibility in table names?  Ed: seems like unnecessary complexity
	dprint("add_association: db:",db,"\tcursor:",cursor,"\n\tfile:",file,"\ttag:",tag)
	c = cursor	#line length
	query1='SELECT COUNT(name) FROM tag WHERE name = \'{0}\';'.format(tag)
	dprint("\tquery:",query1)
	c.execute(query1)	#check tag exists
	#if tag not present, create
	(tagNum,)=c.fetchone()
	dprint("\ttagNum:",tagNum)
	if tagNum==0:
		dprint("attempting insert tag")
		c.execute('INSERT INTO tag (name) VALUES (\'{0}\')'.format(tag,))
	#check filepath in file table
	c.execute('SELECT COUNT(path) FROM file WHERE path = \'{0}\';'.format(file))
	#if not present, create
	(fileNum,)=c.fetchone()
	dprint("\tfileNum:", fileNum)
	if fileNum==0:
		dprint("attempting insert file")
		c.execute('INSERT INTO file (path,name) VALUES (\'{0}\',\'{1}\')'.format(file,file))	#verify works
		#TODO: IMPLEMENT: TAG-12 name will be filename only not entire path
	#check association in association table
	c.execute('SELECT COUNT(filePath) FROM tagging WHERE filePath = \'{0}\' AND tagName = \'{1}\';'.format(file,tag))
	(assocNum,)=c.fetchone()
	dprint("\tassocNum:",assocNum)
	#if not present add entry in tagxfile many:many table
	if assocNum==0:
		dprint("attempting insert association")
		c.execute('INSERT INTO tagging (filePath,tagName) VALUES (\'{0}\',\'{1}\')'.format(file,tag))	#verify works
	else:
		print("Association already exists!")
	#commit to ensure everything actually written
	dprint("\tcommitting to db")
	db.commit()
	if assocNum==0:
		print("The tag",tag,"was applied to file",file)		#non-silent success AFTER db.commit()


def associate(tag,file):
	'''oversees process of associating file and tag'''
	dprint("file:",file,"tag:",tag)
	db = sqlite3.connect(db_name())		#open the db file, will create db if DNE
	cursor = db.cursor()
	check_and_create_tables(db, cursor)	#create the tables if needed
	add_association(db,cursor,file,tag.lower())	#associate the file and tag
	#tags forced lowercase to prevent multiple case of same tag in db
	#file left alone due to case-sensitive filesystems
	db.close()	#ensure everything written to db


def output_association(lookup,half='tag'):
	'''writes out all the files/tags associated with specified tag/file respectively'''
	if half == 'tag':
		dprint("output_files: looking up all files associated with tag:",lookup)
		query = 'SELECT filePath FROM tagging WHERE tagName = \'{0}\''.format(lookup)
	elif half == 'file':
		dprint("output_files: looking up all files associated with tag:",lookup)
		query = 'SELECT tagName FROM tagging WHERE filePath = \'{0}\''.format(lookup)
	dprint("\tconnecting to:",db_name)
	db=sqlite3.connect(db_name())
	c = db.cursor()
	dprint("\tquery:",query)
	c.execute(query)
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

#TODO: IMPLEMENT: TAG-13 getopt version
if __name__ == "__main__":		#if this is the script directly called to run, not as a library include
	parser = argparse.ArgumentParser(description="tag files with user-defined tags", add_help=False)
	parser.add_argument("-h", "-?", "--help", action="store_true", help="show this help message and exit")
	parser.add_argument("-t", "--tagged",metavar="TAG", action="store", help="display files associated with the tag specified")
	#can't use --tag due to tag being an optional argument below
	parser.add_argument("-f", "--file", help="display all the tags associated with the file specified")
	parser.add_argument("-d", "--switchdb",metavar="DATABASE", help="use database specified (Not Yet Implemeted!)")
	parser.add_argument("-v", "--version", action="store_true", help="display the taggr version number")
	parser.add_argument("tag", type=str, help="tag to add to file, requires file to be specified", nargs="?")
	parser.add_argument("file", type=str, help="file to tag, requires tag to be specified", nargs="?")
	args=parser.parse_args()	#nothing happens without parse_args()
	dprint("CLI args after processing:",args,"\n")
	#process arguments
	if len(sys.argv) == 1:		#user specified no arguments
		parser.print_help()
	if args.help:
		parser.print_help()		#necessary for -? to be a valid help request
	if args.tag != None and args.file == None:	#need both, but argparse can't handle this
		parser.print_usage()
		print(sys.argv[0],": error: both TAG and FILE arugments must be specified",sep="")


	#note above will not work due to different arguments for different flag settings


	# dprint("Number of args:",len(sys.argv),"\nList of args:",str(sys.argv))
	# if len(sys.argv) == 1:	#run without arguments, print usage
	# 	print_usage()
	# 	ARGS_UNDERSTOOD=True
	# else:
	# 	argument = sys.argv[1]		#used in following code to lower lookups INELEGANT
	# 	#use getopt after initial testing

	# if len(sys.argv) == 2:	#simple args here, ie taggr --help
		
	# 	if argument == "--help" or argument == "-h" or argument == "-?":	
	# 		#detailed general usage instructions
	# 		print_usage()
	# 		ARGS_UNDERSTOOD=True

	# 	if argument == "--version" or argument == "-v":
	# 		print("Taggr", __VERSION__)
	# 		ARGS_UNDERSTOOD=True

	# if len(sys.argv) == 3:
	# 	if argument == "-d" :
	# 		switch_db(sys.argv[2])
	# 		ARGS_UNDERSTOOD=True
	# 	elif argument == "--help" or argument == "-h" or argument == "-?":
	# 		print_usage(sys.argv[2])
	# 	elif argument == "-t":
	# 		output_association(sys.argv[2],'tag')
	# 		ARGS_UNDERSTOOD = True
	# 	elif argument == "-f":
	# 		output_association(sys.argv[2],'file')
	# 		ARGS_UNDERSTOOD = True
	# 	else:
	# 		if sys.argv[1][0] != "-":	#don't interpret a mistaken switch for a tag
	# 			associate(sys.argv[1],sys.argv[2])
	# 			ARGS_UNDERSTOOD=True

	# if ARGS_UNDERSTOOD==False:		#incorrect arguments, inform invalid and print valid usage
	# 	print("\nILLEGAL ARGUMENTS:",*list(sys.argv))
	# 	print_usage()
