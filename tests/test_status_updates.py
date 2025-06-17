from struct import pack
from sys import flags
import unittest
from gradescope_utils.autograder_utils.decorators import weight
from gradescope_utils.autograder_utils.files import check_submitted_files
import concurrent.futures
import binascii, time, traceback
import random, socket, struct
from CRCTestManager import CRCTestManager

class TestStatusUpdates(unittest.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass


    @weight(1)
    def test_welcome_status(self):
        test_manager = CRCTestManager()
    
        CRC_connection_tests = {
            # Tests status messages
            '5_1_WelcomeStatus':1,
            #'5_2_DuplicateID_Server':1,
            #'5_3_DuplicateID_Client':1,
            #'5_4_UnknownID_Client':1,
        }

        result = test_manager.run_tests(CRC_connection_tests)
        self.assertTrue(result[1][0]['passed'], result[1][0]['errors'])


    def test_duplicate_id_server(self):
        test_manager = CRCTestManager()
    
        CRC_connection_tests = {
            # Tests status messages
            #'5_1_WelcomeStatus':1,
            '5_2_DuplicateID_Server':1,
            #'5_3_DuplicateID_Client':1,
            #'5_4_UnknownID_Client':1,
        }

        result = test_manager.run_tests(CRC_connection_tests)
        self.assertTrue(result[1][0]['passed'], result[1][0]['errors'])


    def test_duplicate_id_client(self):
        test_manager = CRCTestManager()
    
        CRC_connection_tests = {
            # Tests status messages
            #'5_1_WelcomeStatus':1,
            #'5_2_DuplicateID_Server':1,
            '5_3_DuplicateID_Client':1,
            #'5_4_UnknownID_Client':1,
        }

        result = test_manager.run_tests(CRC_connection_tests)
        self.assertTrue(result[1][0]['passed'], result[1][0]['errors'])


    def test_unknown_id_client(self):
        test_manager = CRCTestManager()
    
        CRC_connection_tests = {
            # Tests status messages
            #'5_1_WelcomeStatus':1,
            #'5_2_DuplicateID_Server':1,
            #'5_3_DuplicateID_Client':1,
            '5_4_UnknownID_Client':1,
        }

        result = test_manager.run_tests(CRC_connection_tests)
        self.assertTrue(result[1][0]['passed'], result[1][0]['errors'])