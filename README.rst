django-profiler
===============

django-profiler is util for profiling python code mainly in django projects
but can be used also on ordinary python code. It counts sql queries a measures
time of code execution. It logs its output via standard
python logging library and uses logger `profiling`. If your profiler name
doesn't contain any empty spaces e.g. Profiler('Profiler1') django-profiler will
log all the output to the `profiling.Profiler` logger.
`@profilehook` decorator uses `profilehooks` python package to gather
code execution stats. Except it logs via standard python logging it also
outputs code execution stats directly to `sys.stdout`.


Requirements
------------

- python 2.7+
- *profilehooks* python package
- *python-profiler* linux package

For more information see *debian_requirements.txt* and *requirements.txt* files.

**Important:** *profilehooks*, *python-profiler* are not required to be installed. Without installing them
you won't be able to use `@profilehook` decorator.


Installation
-----------

Install via *pip* or copy this module into your project or into your PYTHON_PATH.


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
`profilehooks` stats are outputted directly into `sys.stdout`.

::

 from profiling import profilehook

 @profilehook
 def complex_computations():
     #some complex computations

**Example 8**

Using decorator approach. Output will be logged to *profiling.ComplexClass.complex_computations* logger.
`profilehooks` stats are outputted directly into `sys.stdout`.

::

 from profiling import profilehook

 class ComplexClass(object)
    @profilehook
    def complex_computations():
        #some complex computations


Tests
-----

**Tested on evnironment**

- Xubuntu Linux 11.04 natty 64-bit
- python 2.7.1+
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
- http://www.codescale.net/en/community#django-profiler