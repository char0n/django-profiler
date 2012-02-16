django-profiler
===============

django-profiler is util for profiling python code mainly in django projects
but can be used also on ordinary python code. It counts sql queries a measures
time of code execution. It logs its output via standard
python logging library and uses logger `profiling`. If your profiler name
doesn't contain any empty spaces e.g. Profiler('Profiler1') django-profiler will
log all the output to the `profiling.Profiler` logger.


Requirements
------------

- python 2.7+


Installation
------------

Install via *pip* or copy this module into your project or into your PYTHON_PATH.


Configuration
-------------

**django settings.py constants**

::

 PROFILING_LOGGER_NAME
 PROFILING_SQL_QUERIES

It is possible to change default django-profiler logger name by defining
PROFILING_LOGGER_NAME = 'logger_name' in your django *settings.py*.

To log also sql queries into profiler logger set PROFILING_SQL_QUERIES to True
in your django *settings.py* module.


Examples
--------

**Example 1**

Using context manager approach. Output will be logged to *profiling* logger.

::

 from profiling import Profiler
 with Profiler('Complex Computation'):
     # code with some complex computations

**Example 2**

Using context manager approach. Output will be logged to *profiling.Computation* logger.

::

 from profiling import Profiler
 with Profiler('Computation'):
     # code with some complex computations

**Example 3**

Using standard approach. Output will be logged to *profiling* logger.

::

 from profiling import Profiler
 profiler =  Profiler('Complex Computation')
 profiler.start()
 # code with some complex computations
 profiler.stop()

**Example 4**

Using standard approach and starting directly in constructor. Output will be logged to *profiling* logger.

::

 from profiling import Profiler
 profiler =  Profiler('Complex Computation', start=True)
 # code with some complex computations
 profiler.stop()

**Example 5**

Using decorator approach. Output will be logged to *profiling.complex_computations* logger.

::

 from profiling import profile

 @profile
 def complex_computations():
     #some complex computations

**Example 6**

Using decorator approach. Output will be logged to *profiling.ComplexClass.complex_computations* logger.

::

 from profiling import profile

 class ComplexClass(object):
     @profile
     def complex_computations():
         #some complex computations

**Example 7**

Using decorator approach. Output will be logged to *profiling.complex_computations* logger.
`profile` execution stats are logged to *profiling.complex_computations* logger.

::

 from profiling import profile

 @profile(stats=True)
 def complex_computations():
     #some complex computations

**Example 8**

Using decorator approach. Output will be logged to *profiling.complex_computations* logger.
`profile` execution stats are printed to sys.stdout.

::

 import sys

 from profiling import profile

 @profile(stats=True, stats_buffer=sys.stdout)
 def complex_computations():
     #some complex computations


**Example 9**

Using decorator approach. Output will be logged to *profiling.ComplexClass.complex_computations* logger.
`profile` stats will be logged to *profiling.ComplexClass.complex_computations*.

::

 from profiling import profile

 class ComplexClass(object)
    @profile(stats=True)
    def complex_computations():
        #some complex computations


Tests
-----

**Tested on evnironment**

- Xubuntu Linux 11.10 oneiric 64-bit
- python 2.7.2+
- python unittest

**Running tests**

To run the test run command: ::

 $ python test.py
 $ python setup.py test


Author
------

| char0n (Vladimír Gorej, CodeScale s.r.o.)
| email: gorej@codescale.net
| web: http://www.codescale.net


References
----------

- http://github.com/char0n/django-profiler
- http://pypi.python.org/pypi/django-profiler/
- http://www.codescale.net/en/community#django-profiler