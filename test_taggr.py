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
		'''sets up a testing environment for all other tests to use'''
		print("\n\n\nSetting up testing environment...")
		self.tag = taggr()
		if args != []:
			if args.debug == True:	#command-line debug print instead of in-code
				self.tag.__VERBOSE_DEBUG__ = True #will require refactoring to work
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
		'''verifies setUpClass changed the database'''
		#changed to this due to not being 100% sure of how to order tests
		#so switched to the database in the setUpClass classmethod
		self.assertEqual(self.tag.db_name(), "testRegimen.db")

	def test_associate(self):
		'''verifies that associate() works'''
		self.tag.associate('test',"C:\\test")	#will fail if DB not created
		self.assertEqual([('C:\\test',)],self.tag.output_association('test', 'tag'))
		self.assertEqual([('test',)],self.tag.output_association('C:\\test', 'file'))

	def test_associations(self):
		'''verifies that multiple associations work'''
		#create multiple cross-associations for verification
		associations = {\
			'Polyurathane': ['F:\\Plastics',],
			'PETG': ['F:\\Plastics',],
			'PLA': ['F:\\Plastics','G:\\Biodegradeable'],
			'ABS': ['F:\\Plastics',],
			'Jimmy': ['G:\\Biodegradeable', 'H:\\Human'],
		}
		#turn above dict into DB associations
		for key in associations:
			for val in associations[key]:
				print("associating",key,"to",val)
				self.tag.associate(key,val)
		print("output of Polyurathane:", \
			self.tag.output_association('polyurathane', 'tag'))
		self.assertEqual( [('F:\\Plastics',)], \
			self.tag.output_association('polyurathane', 'tag') )
		print("output after associations of PLA:", \
			self.tag.output_association('pla', 'tag'))
		self.assertEqual( [('F:\\Plastics',),('G:\\Biodegradeable',)], \
			self.tag.output_association('pla', 'tag') )


	def testSelf(self):
		'''verifies that python is working properly'''
		self.assertEqual(self,self)

	def test_version(self):
		'''verifies that the version is a string'''
		self.assertEqual(type(self.tag.__VERSION__),type(""))

	@classmethod
	def tearDownClass(self): #decorator makes this called only once for all tests
		'''tears down the testing enviroment, restoring back to pre-test state'''
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
			os.remove("testRegimen.db")
		print("class torn down")


if __name__=="__main__":
	parser = argparse.ArgumentParser(description="Unit test taggr.py", add_help=False)
	parser.add_argument("-dg","--debug", action="store_true", help="display debug readout")	#would be deleted in release code?
	args=parser.parse_args()	#nothing happens without parse_args()


	suite = unittest.TestLoader().loadTestsFromTestCase(TestTaggr)
	unittest.TextTestRunner(verbosity=2).run(suite)
