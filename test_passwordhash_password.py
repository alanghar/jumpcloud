import logging
import os
import subprocess
import requests
import socket
import datetime
import json
from baseservertest import BaseServerTest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

MAX_JOBID_WAIT_SEC = 2
HASH_WAIT_TIME_SEC = 5


class TestPasswordHash_Password(BaseServerTest):       

    def test_empty_pw(self):
        self.verify_pw("")

    def test_spaces_pw(self):
        self.verify_pw("      ")

    def test_sqlinject_pw(self):
        self.verify_pw("0 OR 1=1; --")
        self.verify_pw("' OR 1=1; --")

    def test_regex_pw(self):
        self.verify_pw(".")
        self.verify_pw(".*")
        self.verify_pw("*")

    def test_normal_pw(self):
        self.verify_pw("password 0123456789 ~!@#$%^&*()_[]{}?/.,<>;':")

    def test_numeric_pw(self):
        self.verify_pw("0123456789")

    def test_alpha_pw(self):
        self.verify_pw("abcdefghijklmnopqrstuvwxyz")

    def test_specialchar_pw(self):
        self.verify_pw(r'!@#$%^&*()_`~[]{}\|+=,./?' + "'")

    def test_reused_pw(self):
        self.verify_pw("some password")
        self.verify_pw("some password")

    def test_long_pw(self):
        self.verify_pw("a REALLY long password "*500)

    def test_leading_spaces_pw(self):
        self.verify_pw("     this has leading spaces")

    def test_trailing_spaces_pw(self):
        self.verify_pw("this has trailing spaces     ")

    def test_tabs_pw(self):
        self.verify_pw("\t\tthis\thas\ttabs\t\t")

    def test_newlines_pw(self):
        self.verify_pw("\nthis\nhas\nnewlines\n")

    def test_carriage_pw(self):
        self.verify_pw("\rthis\rhas\rcarriage\rreturns\r")

    def test_crnl_pw(self):
        self.verify_pw("\r\nthis\r\nhas\r\ncarriage\r\nreturn\r\nnewlines\r\n")

    def test_unicode_pw(self):
        self.verify_pw(u'some password in unicode')

    def test_extended_pw(self):
        self.verify_pw("someprefix")
        self.verify_pw("someprefix extended")

    def test_jobid_as_pw(self):
        jobid = self.verify_pw("0123456789")
        self.verify_pw(jobid)

    # def test_concurrent_requests(self):
    #     """
    #     Do the stats update at the right time?
    #     """
    #     self.seed_random(0)
    #     rand_pws = self.generate_n_random_passwords(50, 20)
    #     for pw in rand_pws:
            

    def test_jobid_returned_immediately(self): 
        start = datetime.datetime.now()       
        self.try_pw("sample password")    
        end = datetime.datetime.now()    
        jobid_time = end - start
        if(jobid_time > datetime.timedelta(seconds=MAX_JOBID_WAIT_SEC)):
            self.fail("Took too long to return the jobid (should be 'immediate'): %s" % jobid_time)

    def test_hash_delayed(self):        
        jobid = self.try_pw("sample password")    
        jobid_returned_time = datetime.datetime.now()    
        resp = self.try_jobid(jobid)
        hash_time = datetime.datetime.now()
        if(hash_time - jobid_returned_time < datetime.timedelta(seconds=HASH_WAIT_TIME_SEC)):
            self.fail("Hashing occurred too quickly (should be greater than %s sec): %s" % (HASH_WAIT_TIME_SEC, hash_time - jobid_returned_time))

