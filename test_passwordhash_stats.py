import grequests
import json
import pprint
import datetime
from baseservertest import BaseServerTest, PORT
from test_passwordhash_password import HASH_WAIT_TIME_SEC

MILLIS = 1000

class TestPasswordHash_Stats(BaseServerTest):
    def test_initial_stats(self):
        stats = self.get_stats()
        assert stats['AverageTime'] == 0, "AverageTime not initialized correctly"
        assert stats['TotalRequests'] == 0, "TotalRequests not initialized correctly"

    def test_simple_request_increment(self):
        initial_stats = self.get_stats()
        pw = self.generate_random_password(20)
        start_time = datetime.datetime.now()
        self.try_pw(pw)
        end_time = datetime.datetime.now()
        new_stats = self.get_stats()
        assert new_stats['TotalRequests'] == initial_stats['TotalRequests'] + 1, "TotalRequests does not increment as expected"
        assert new_stats['AverageTime'] >= HASH_WAIT_TIME_SEC * MILLIS, "Average hash time failed to be greater than %s seconds" % HASH_WAIT_TIME_SEC
        assert new_stats['AverageTime'] <= (end_time - start_time).total_seconds() * MILLIS, "Average hash time statistic too high"

    def test_concurrent_increment(self):
        initial_stats = self.get_stats()
        rand_pws = self.generate_n_random_passwords(50, 20)
        url = self.get_pw_url()
        async_requests = (grequests.post(url, data=json.dumps({"password": str(pw)})) for pw in rand_pws)
        start_time = datetime.datetime.now()
        async_results = [int(x.content) for x in grequests.map(async_requests)]
        end_time = datetime.datetime.now()
        new_stats = self.get_stats()
        assert new_stats['TotalRequests'] == initial_stats['TotalRequests'] + 50, "TotalRequests does not increment as expected"
        assert new_stats['AverageTime'] >= HASH_WAIT_TIME_SEC * MILLIS, "Average hash time statistic failed to be greater than %s seconds" % HASH_WAIT_TIME_SEC
        assert new_stats['AverageTime'] <= (end_time - start_time).total_seconds() * MILLIS, "Average hash time statistic too high"
