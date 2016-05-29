Tests
*****

Continuous Integration tests
============================

Windows:

.. image:: https://ci.appveyor.com/api/projects/status/ahjg5spf83lsu2vn/branch/master?svg=true
   :target: https://ci.appveyor.com/project/cmutel/ocelot/branch/master
   :alt: Ocelot Windows build status

Linux:

.. image:: https://travis-ci.org/OcelotProject/Ocelot.svg?branch=master
   :target: https://travis-ci.org/OcelotProject/Ocelot
   :alt: Ocelot Linux build status

Running the tests yourself
==========================

.. note:: Running the Ocelot tests requires a `source checkout from Github <https://github.com/OcelotProject/Ocelot>`__.

Run tests with `py.test <http://pytest.org/latest/>`__ using the command ``py.test`` in the source directory. You can install `pytest-xdist <https://pytest.org/latest/xdist.html>`__ to run tests in parallel.

Writing tests
=============

New transformation functions should be tested, and pull requests without tests will not be accepted. Note that for testing you should use the built-in mocks to avoid writing actual HTML reports or parsing directories full of ``.spold`` files. This means that any tests that which execute a system model should look like this:

.. code-block:: python

    from ocelot.tests.mocks import fake_report

    def test_something(fake_report):
        report, data = system_model(some_data, some_functions)

``fake_report`` is a ``py.test`` fixture that does two things. First, it write report data to a temporary directory and prevents HTML report generation. Second, the function ``extract_directory`` is short-circuited; Instead of passing a directory path as the first argument to ``system_model``, you can just pass in data in the correct format.

Writing mocks makes tests better in a number of ways, but can sometimes be frustrating if things don't work as expected. The following may be helpful:

* `unittest.mock documentation <https://docs.python.org/3/library/unittest.mock.html#module-unittest.mock>`__
* `Where to patch <https://docs.python.org/3/library/unittest.mock.html#where-to-patch>`__
* `Mock gotchas <http://alexmarandon.com/articles/python_mock_gotchas/>`__
