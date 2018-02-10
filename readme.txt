Submitted by Alex Langhart
2/10/2018

*** Summary ***

I developed and tested these tests on a 64 bit Windows 10 machine, which resulted in 5 failures.
That aligned with the 5 bugs mentioned in the project description, but I later tried running
the tests on an Ubuntu 16.04 machine and had different results: only 2 failures. The two 
executables appeared to behave differently. For example, with the Windows version, the AverageTime
statistic was never updated (it was always 0), but with the Linux version, it did - even though
it was too high. Both were failures in this case. However, the handling of in-flight requests
appeared to fail only on Windows and not Linux.

The bugs I found were:
1. It takes about 5 seconds to return a job ID when submitting a password to /hash. The 
   specification says it should return immediately.

2. The server hashes the password immediately after returning the job ID. The specification
   says it should wait 5 seconds after returning the job ID.
   * Note that I wasn't sure if these two bugs should be considered a single bug, but I
     assumed they were separate.

3. Nondeterministic behavior when handling concurrent requests - either the wrong job IDs
   were being returned or the hashes were simply being generated incorrectly. I say this
   was nondeterministic because it was not perfectly repeatable. Sometimes it would happen
   and other times it wouldn't. By using enough concurrent requests, I could get a failure
   to happen nearly every run. I did not see this failure on the Linux machine.

4. Average time statistic not being updated on Windows. On Linux, it was being updated but
   was far higher than it should have been (exceeding the time of the longest-running request).

5. On Windows, some connections were forcibly closed when the shutdown command was issued. 
   The specification says the server should allow any in-flight password hashing to complete.
   I did not see this failure on the Linux machine.



*** Running the Tests ***

The tests assume the server executables are in a "server" directory outside of the repo's directory.
Here's how I had it layed out:
.
├── repo
│   ├── baseservertest.py
│   ├── helpers.py
│   ├── __init__.py
│   ├── readme.txt
│   ├── requirements.txt
│   ├── sample_test_output.txt
│   ├── test_passwordhash_jobid.py
│   ├── test_passwordhash_password.py
│   ├── test_passwordhash_ports.py
│   ├── test_passwordhash_shutdown.py
│   └── test_passwordhash_stats.py
└── server
    ├── broken-hashserve_darwin
    ├── broken-hashserve_linux
    ├── broken-hashserve_win.exe
    └── version.txt

I used python 2.7. To run the tests, cd into the repo directory, install any needed packages 
(pip install -r requirements.txt), and run: pytest

Pytest should find the tests and execute them, then display their results. A sample console output is provided
in sample_test_output_win10.txt. Actual console output will normally have syntax coloring, making it much
easier to read.



*** Test Design ***

The tests are grouped into 5 categories and defined in respective classes/files:
- JobID behavior 
    Makes requests with various types of job ID strings. Because the server generates its own 
    job IDs, these variations aren't as extensive as the passwords themselves. These tests
    are mostly ensuring the server gracefully rejects invalid Job IDs.

- Password behavior
    Tests with various types of passwords. Also verifies that multiple concurrent requests can be processed
    correctly, the job ID is immediately returned, and the hash is then calculated 5 seconds after the job ID
    is returned.

- Port behavior
    Verifies that the specified port is being listened to and that multiple simultaneous socket connections
    can be made to the port. This does not attempt to test anything HTTP related.

- Shutdown behavior
    Verifies that in-flight requests are gracefully processed and new requests are rejected when the server
    is directed to shut down.

- Statistics behavior
    Verifies that the statistics are initialized correctly and adjusted according to processed requests.

Additional future tests/improvements:
- Staggered concurrent requests
- HTTP conformity
- Compare incorrect hashes to other password hashes, to detect mix ups.
