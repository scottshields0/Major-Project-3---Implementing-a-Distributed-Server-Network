from struct import pack
from sys import flags
import unittest
from gradescope_utils.autograder_utils.decorators import weight
from gradescope_utils.autograder_utils.files import check_submitted_files
import concurrent.futures
import binascii, time, traceback
import random, socket, struct
from CRCTestManager import CRCTestManager

class TestServersAndClients(unittest.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass


    @weight(1)
    def test_one_server_one_client(self):
        test_manager = CRCTestManager()
    
        CRC_connection_tests = {
            # Tests the user registration messages
            '3_1_OneServer_OneClient':4,
            #'3_2_OneServer_TwoClients':1,
            #'3_3_ThreeServers_FourClients':1,
            #'3_4_ElevenServers_EightClients':1,
        }

        result = test_manager.run_tests(CRC_connection_tests)
        self.assertTrue(result[1][0]['passed'], result[1][0]['errors'])


    @weight(1)
    def test_one_server_two_clients(self):
        test_manager = CRCTestManager()
    
        CRC_connection_tests = {
            # Tests the user registration messages
            #'3_1_OneServer_OneClient':4,
            '3_2_OneServer_TwoClients':1,
            #'3_3_ThreeServers_FourClients':1,
            #'3_4_ElevenServers_EightClients':1,
        }

        result = test_manager.run_tests(CRC_connection_tests)
        self.assertTrue(result[1][0]['passed'], result[1][0]['errors'])


    @weight(1)
    def test_three_servers_four_clients(self):
        test_manager = CRCTestManager()
    
        CRC_connection_tests = {
            # Tests the user registration messages
            #'3_1_OneServer_OneClient':4,
            #'3_2_OneServer_TwoClients':1,
            '3_3_ThreeServers_FourClients':1,
            #'3_4_ElevenServers_EightClients':1,
        }

        result = test_manager.run_tests(CRC_connection_tests)
        self.assertTrue(result[1][0]['passed'], result[1][0]['errors'])


    @weight(1)
    def test_eleven_servers_eight_clients(self):
        test_manager = CRCTestManager()
    
        CRC_connection_tests = {
            # Tests the user registration messages
            #'3_1_OneServer_OneClient':4,
            #'3_2_OneServer_TwoClients':1,
            #'3_3_ThreeServers_FourClients':1,
            '3_4_ElevenServers_EightClients':1,
        }

        result = test_manager.run_tests(CRC_connection_tests)
        self.assertTrue(result[1][0]['passed'], result[1][0]['errors'])