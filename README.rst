django-profiler
===============

django-profiler is util for profiling python code mainly in django projects,
but can be used also on ordinary python code. It logs its output via standard
python logging library and uses logger ``profiling``. If your profiler name
doesn't contain any empty spaces e.g. Profiler('Profiler1') django-profiler will
log all the output to the ``profiling.Profiler`` logger. If you're using ``@profilehook``
decorator, output is either being logged and outputted to ``sys.stdout``.


Requirements
------------

- python 2.7+
- ``profilehooks`` python package
- ``python-profiler`` linux package

For more information see ``debian_requirements.txt`` and ``requirements.txt`` files


Installation
-----------

Install via ``pip` or copy this module into your project or into your PYTHON_PATH.


Example
-------

**Example 1**
::

 from profiling import Profiler
 with Profiler('Complex Computation'):
     # code with some complex computations


Tests
-----

**Tested on evnironment**

- Xubuntu Linux 11.04 natty 64-bit
- python 2.7.1+
- python unittest

**Running tests**

To run the test run command: ::

 $ python test.py


Author
------

| char0n (Vladimír Gorej, CodeScale s.r.o.)
| email: gorej@codescale.net
| web: http://www.codescale.net


References
----------

- http://github.com/char0n/django-profiler
- http://www.codescale.net/en/community#django-profiler