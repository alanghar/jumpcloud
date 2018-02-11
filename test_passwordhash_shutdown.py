import requests
import grequests
import json
import time
import traceback
import threading
from helpers import restart_server
from baseservertest import BaseServerTest, PORT


class TestPasswordHash_Shutdown(BaseServerTest):
    def setUp(self):
        restart_server(PORT)
        self.seed_random(0)

    def test_shutdown_request(self):
        self.try_shutdown()

    def test_inflight_allowed(self):
        """
        This test attempts to issue the shutdown command after submitting
        a number of passwords to the server. The specification says any in-flight requests
        should continue processing until finished.

        Here, a separate thread attempts the password submissions, and 4 seconds
        after starting the thread, the shutdown command is given. This is technically a race
        condition but I think unlikely to be a problem.
        """
        thread_results = {"error": None, "failed": False}
        pwds = self.generate_n_random_passwords(50, 20)

        def submitter_thread_routine(pwds, output):
            def handle_exception(request, exception):
                if(isinstance(exception.args[0], requests.packages.urllib3.exceptions.ProtocolError)):
                    # We may want to control access to the output dict with a lock, but it's not critical here.
                    output['error'] = exception
                    output['failed'] = True

            try:
                url = self.get_pw_url()
                async_requests = (grequests.post(url, data=json.dumps({"password": str(pw)})) for pw in pwds)
                async_results = grequests.map(async_requests, exception_handler=handle_exception)
                if(not all(map(lambda x:x is not None and x.status_code == 200, async_results))):
                    output["failed"] = True
            except Exception as e:
                traceback.print_exc()
                output['error'] = e
                output["failed"] = True

        thread = threading.Thread(target=submitter_thread_routine, args=(pwds, thread_results))
        thread.start()
        time.sleep(4)
        self.try_shutdown()
        thread.join()
        assert thread_results["failed"] == False, "Server mishandled in-flight requests while shutting down.: %s" % thread_results["error"]


    def test_new_requests_denied(self):
        self.try_pw("sample password")
        self.try_shutdown()
        try:
            self.try_pw("sample password")
        except:
            return
        self.fail("Password request was accepted after shutdown")


    def test_new_concurrent_requests_denied(self):
        thread_results = {"complete": False}
        def submitter_thread_routine(thread_results):
            self.try_pw("sample password")
            thread_results["complete"] = True

        thread = threading.Thread(target=submitter_thread_routine, args=(thread_results,))
        thread.start()
        time.sleep(2)
        self.try_shutdown()
        was_rejected = False
        try:
            self.try_pw("sample password")
        except:
            was_rejected = True
        thread.join()

        if(was_rejected is False):
            self.fail("Password request was accepted after shutdown")
