from struct import pack
from sys import flags
import unittest
from gradescope_utils.autograder_utils.decorators import weight
from gradescope_utils.autograder_utils.files import check_submitted_files
import concurrent.futures
import binascii, time, traceback
import random, socket, struct
from CRCTestManager import CRCTestManager

class TestMessages(unittest.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass


    @weight(1)
    def test_message_zero_hops(self):
        test_manager = CRCTestManager()
    
        CRC_connection_tests = {
            # Tests the chat messaging
            '4_1_Message_Zero_Hops':1,
            #'4_2_Message_One_Hop':1,
            #'4_3_Message_Three_Hops':1,
        }

        result = test_manager.run_tests(CRC_connection_tests)
        self.assertTrue(result[1][0]['passed'], result[1][0]['errors'])


    @weight(1)
    def test_message_one_hop(self):
        test_manager = CRCTestManager()
    
        CRC_connection_tests = {
            # Tests the chat messaging
            #'4_1_Message_Zero_Hops':1,
            '4_2_Message_One_Hop':1,
            #'4_3_Message_Three_Hops':1,
        }

        result = test_manager.run_tests(CRC_connection_tests)
        self.assertTrue(result[1][0]['passed'], result[1][0]['errors'])


    @weight(1)
    def test_message_three_hops(self):
        test_manager = CRCTestManager()
    
        CRC_connection_tests = {
            # Tests the chat messaging
            #'4_1_Message_Zero_Hops':1,
            #'4_2_Message_One_Hop':1,
            '4_3_Message_Three_Hops':1,
        }

        result = test_manager.run_tests(CRC_connection_tests)
        self.assertTrue(result[1][0]['passed'], result[1][0]['errors'])