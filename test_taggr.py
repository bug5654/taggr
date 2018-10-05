#global imports
import argparse
import json
import os
import stat
import sys
import unittest

#local imports
from taggr import taggr

__PRINT_DEBUG__=False
args = []

class TestTaggr(unittest.TestCase):
	'''tests taggr to ensure nothing broke'''

	#static vars
	__cleanup__ = True	#allows destruction of testing directory & db
	tag = None
	current_database="taggr.db"

	@classmethod
	def setUpClass(self):	#decorator makes this called only once for all tests
		print("\n\n\nSetting up testing environment...")
		self.tag = taggr()
		if args != []:
			if args.debug == True:	#command-line debug print instead of in-code
				__VERBOSE_DEBUG__ = True
				print("in debug mode")
		try:
			f=open('.taggrprefs',"r")
			x = json.load(f)
			self.current_database = x["Database"]
			f.close()
			print("\tprior database stored")
		except:
			print("\ttrouble opening .taggrprefs during initial setup (ignore if fresh install)")
		self.tag.switch_db("testRegimen.db")
		print("\tswitched to testingRegimen.db")
		print("finished setting up")
	

	def test_switch_db(self):
		self.assertEqual(self.tag.db_name(), "testRegimen.db")

	def test_associate(self):
		self.tag.associate('test',"C:\\test")	#will fail if DB not created
		self.assertEqual([('C:\\test',)],self.tag.output_association('test', 'tag'))
		self.assertEqual([('test',)],self.tag.output_association('C:\\test', 'file'))

	def testSelf(self):
		self.assertEqual(self,self)

	def test_version(self):
		self.assertEqual(type(self.tag.__VERSION__),type(""))

	@classmethod
	def tearDownClass(self): #decorator makes this called only once for all tests
		if self.__cleanup__:
			# print("cleaning out testing directory")
			# for root, dirs, files in os.walk(self.testing_directory):
			# 	for name in files:
			# 		os.remove(os.path.join(root,name))
			# 	# for name in dirs:
			# 	# 	os.rmdir(os.path.join(root,name))
			# 	# above commented out for safe execution when not needed
			# os.chdir(self.current_directory)	
			# os.rmdir(self.testing_directory)
			# print("testing directory removed")
			self.tag.switch_db(self.current_database)
			# print("cleanup: actual:",self.tag.db_name(),"expected:",self.current_database)
			# print("cleanup: type(actual):",type(self.tag.db_name()),"type(expected):",type(self.current_database))
			# equality = self.tag.db_name() == self.current_database
			# print("checking equality:", equality)
			# self.assertEqual(self.tag.db_name(), self.current_database)	#not sure why this is giving errors
			# verify if allowed to assert*() in classmethods?
		print("class torn down")


if __name__=="__main__":
	parser = argparse.ArgumentParser(description="Unit test taggr.py", add_help=False)
	parser.add_argument("-dg","--debug", action="store_true", help="display debug readout")	#would be deleted in release code?
	args=parser.parse_args()	#nothing happens without parse_args()


	suite = unittest.TestLoader().loadTestsFromTestCase(TestTaggr)
	unittest.TextTestRunner(verbosity=2).run(suite)
