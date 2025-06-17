from struct import pack
from sys import flags
import unittest
from gradescope_utils.autograder_utils.decorators import weight
from gradescope_utils.autograder_utils.files import check_submitted_files
import concurrent.futures
import binascii, time, traceback
import random, socket, struct
from CRCTestManager import CRCTestManager

class TestConnections(unittest.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    # Fields

    @weight(1)
    def test_two_connections(self):
        test_manager = CRCTestManager()
    
        CRC_connection_tests = {
            # Tests basic connection setup, doesn't involve processing messages
            '1_1_TwoConnections':3,
            #'1_2_FourConnections':4,
            #'1_3_EightConnections':5
        }

        result = test_manager.run_tests(CRC_connection_tests)
        self.assertTrue(result[1][0]['passed'], result[1][0]['errors'])


    @weight(1)
    def test_four_connections(self):
        test_manager = CRCTestManager()
    
        CRC_connection_tests = {
            # Tests basic connection setup, doesn't involve processing messages
            #'1_1_TwoConnections':3,
            '1_2_FourConnections':4,
            #'1_3_EightConnections':5
        }

        result = test_manager.run_tests(CRC_connection_tests)
        self.assertTrue(result[1][0]['passed'], "Failed the test")



    @weight(1)
    def test_eleven_connections(self):
        test_manager = CRCTestManager()
    
        CRC_connection_tests = {
            # Tests basic connection setup, doesn't involve processing messages
            #'1_1_TwoConnections':3,
            #'1_2_FourConnections':4,
            '1_3_EightConnections':5
        }

        result = test_manager.run_tests(CRC_connection_tests)
        self.assertTrue(result[1][0]['passed'], "Failed the test")