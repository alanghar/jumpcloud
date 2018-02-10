import grequests
import datetime
import json
import requests
from baseservertest import BaseServerTest

MAX_JOBID_WAIT_SEC = 2
HASH_WAIT_TIME_SEC = 5


class TestPasswordHash_Password(BaseServerTest):
    def setUp(self):
        self.seed_random(0)      

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

    def test_malformed_json(self):
        url = self.get_pw_url()
        r = requests.post(url, data="not valid json")
        assert r.status_code == 400, "Malformed json request did not return a 400 status"

    def test_concurrent_requests(self):
        rand_pws = self.generate_n_random_passwords(1000, 20)
        url = self.get_pw_url()
        async_requests = (grequests.post(url, data=json.dumps({"password": str(pw)})) for pw in rand_pws)
        async_results = [int(x.content) for x in grequests.map(async_requests)]
        in_out_pairs = sorted(zip(async_results, rand_pws))
        for result, pw in in_out_pairs:
            self.verify_jobid(result, pw)

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

