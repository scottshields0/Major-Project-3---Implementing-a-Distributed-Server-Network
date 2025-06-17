from struct import pack
from sys import flags
import unittest
from gradescope_utils.autograder_utils.decorators import weight
from gradescope_utils.autograder_utils.files import check_submitted_files
import concurrent.futures
import binascii, time, traceback
import random, socket, struct
from CRCTestManager import CRCTestManager

class TestServers(unittest.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    # Fields

    @weight(1)
    def test_two_servers(self):
        test_manager = CRCTestManager()
    
        CRC_connection_tests = {
            # Tests the server registration messages
            '2_1_TwoServers':1,
            #'2_2_FourServers':3,
            #'2_3_ElevenServers':3,
        }

        result = test_manager.run_tests(CRC_connection_tests)
        self.assertTrue(result[1][0]['passed'], result[1][0]['errors'])


    @weight(1)
    def test_four_servers(self):
        test_manager = CRCTestManager()
    
        CRC_connection_tests = {
            # Tests the server registration messages
            #'2_1_TwoServers':1,
            '2_2_FourServers':3,
            #'2_3_ElevenServers':3,
        }

        result = test_manager.run_tests(CRC_connection_tests)
        self.assertTrue(result[1][0]['passed'], result[1][0]['errors'])



    @weight(1)
    def test_eleven_servers(self):
        test_manager = CRCTestManager()
    
        CRC_connection_tests = {
            # Tests the server registration messages
            #'2_1_TwoServers':1,
            #'2_2_FourServers':3,
            '2_3_ElevenServers':3,
        }

        result = test_manager.run_tests(CRC_connection_tests)
        self.assertTrue(result[1][0]['passed'], result[1][0]['errors'])