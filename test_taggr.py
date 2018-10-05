#global imports
import os
import stat
import unittest

#local imports
from taggr import taggr

class TestTaggr(unittest.TestCase):
	'''tests taggr to ensure nothing broke'''

	#static vars
	__cleanup__ = False	#allows destruction of testing directory & db
	tag = None
	current_directory=""
	testing_directory=""

	@classmethod
	def setUpClass(self):	#decorator makes this called only once for all tests
		print("\n\n\nSetting up testing environment...")
		self.tag = taggr()
		print("finished setting up")
	
	def test_associate(self):
		self.tag.associate('test',"C:\\test")	#will fail if DB not created
		self.assertEqual('C:\\test',self.tag.output_association('test', 'tag'))
		self.assertEqual('test',self.tag.output_association('C:\\test', 'file'))

	def testSelf(self):
		self.assertEqual(self,self)

	def test_version(self):
		self.assertEqual(type(self.tag.__VERSION__),type(""))

	@unittest.expectedFailure
	def test_switch_db(self):
		self.tag.switch_db("switched.db")
		assertEqual(self.tag.db_name(), "switched.db")

	@classmethod
	def tearDownClass(self): #decorator makes this called only once for all tests
		if self.__cleanup__:
			print("cleaning out testing directory")
			for root, dirs, files in os.walk(self.testing_directory):
				for name in files:
					os.remove(os.path.join(root,name))
				# for name in dirs:
				# 	os.rmdir(os.path.join(root,name))
				# above commented out for safe execution when not needed
			os.chdir(self.current_directory)	
			os.rmdir(self.testing_directory)
			print("testing directory removed")
		print("class torn down")


if __name__=="__main__":
	suite = unittest.TestLoader().loadTestsFromTestCase(TestTaggr)
	unittest.TextTestRunner(verbosity=2).run(suite)
