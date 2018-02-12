import requests
import grequests
import json
import time
import traceback
import threading
from baseservertest import BaseServerTest, PORT


class TestPasswordHash_Shutdown(BaseServerTest):
    def test_shutdown_request_fresh(self):
        self.try_shutdown()
        self.verify_server_terminated()

    def test_shutdown_request_used(self):
        """
        Shutdown a server that has already processed at least one request.
        """
        self.verify_pw(self.generate_random_password(20))
        self.try_shutdown()
        self.verify_server_terminated()

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

        lock = threading.Lock()

        def submitter_thread_routine(pwds, output):
            def handle_exception(request, exception):
                if(isinstance(exception.args[0], requests.packages.urllib3.exceptions.ProtocolError)):
                    with lock:
                        output['error'] = exception
                        output['failed'] = True

            try:
                url = self.get_pw_url()
                async_requests = (grequests.post(url, data=json.dumps({"password": str(pw)})) for pw in pwds)
                async_results = grequests.map(async_requests, exception_handler=handle_exception)
                if(not all(map(lambda x:x is not None and x.status_code == 200, async_results))):
                    with lock:
                        output["failed"] = True
            except Exception as e:
                traceback.print_exc()
                with lock:
                    output['error'] = e
                    output["failed"] = True

        thread = threading.Thread(target=submitter_thread_routine, args=(pwds, thread_results))
        thread.start()
        time.sleep(4)
        self.try_shutdown()
        thread.join()
        assert thread_results["failed"] == False, "Server mishandled in-flight requests while shutting down.: %s" % thread_results["error"]
        self.verify_server_terminated()


    def test_new_requests_denied(self):
        """
        Attempts to submit multiple new passwords after issuing a shutdown command WHILE a request
        is already in flight. Verifies that the new requests are rejected.
        """
        def submitter_thread_routine(pw, output):
            # Submit password BEFORE server is signaled to shut down
            try:
                self.try_pw(pw)
                output["success"] = True
            except:
                # Don't fail the test if this fails.
                # This test is only interested in whether or not new requests are rejected AFTER the shutdown request
                pass

        initial_submit_result = {"success": False}
        thread = threading.Thread(target=submitter_thread_routine, args=(self.generate_random_password(20), initial_submit_result))
        thread.start()

        time.sleep(1)  # Give the thread some time to start its request

        self.try_shutdown()

        # By this point, a shutdown command has been issued, hopefully while a password request was already in flight.
        # We attempt to submit more requests and expect them to be rejected. If they are accepted, it's a failure.
        # In the event of a failure, we retroactively check that the initial request was successfully submitted.
        # If it was, we raise a real failure. If not, the test result is inconclusive.

        failed = False
        for pw in self.generate_n_random_passwords(5, 20):
            try:
                self.try_pw(pw)
                failed = True
                break
            except:
                pass

        thread.join()

        if(initial_submit_result["success"] is False):
            self.fail("Inconclusive result. Server shut down before initial request was made.")
        elif(failed):
            self.fail("Password request was accepted after shutdown signal. It should have been rejected.")

        self.verify_server_terminated()
