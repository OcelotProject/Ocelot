Installation
------------

Ocelot is designed for Python 3.4 or higher.

Most Ocelot dependencies are pure Python, and this easy to install, but Ocelot uses `lxml <http://lxml.de/>`__. (`cytoolz <https://pypi.python.org/pypi/cytoolz>`__, another compiled library, is optional but highly recommended). Therefore, the easiest way to install Ocelot is using `Anaconda <https://www.continuum.io/downloads>`__. Other installation pathways (e.g. `macports <https://www.macports.org/>`__, `homebrew <http://brew.sh/>`__, Christoph Gohlke's `unofficial binaries <http://www.lfd.uci.edu/~gohlke/pythonlibs/>`__ should also work as well.

To install using ``Anaconda``, download `the relevant Miniconda installer <http://conda.pydata.org/miniconda.html>`__. Be sure to get Python 3.5, and the 64 bit version.

.. note:: On OS X, you may have to make the downloaded script executable using something like ``chmod +x ~/Downloads/Miniconda3-latest-MacOSX-x86_64.sh``.

Run the installation script in the terminal/powershell/command window.

.. warning:: If you have other Python installations on your machine, be sure to **no** to the questions about making this your default Python, and add Miniconda to your path. You will then need to adjust the following commands to the ``bin`` directory of your miniconda installation.

Then, run the following commands to create an Ocelot environment:

.. code-block:: bash

    conda create -y -n ocelot python=3.5 lxml cytoolz

On Windows, then run:

.. code-block:: bash

    activate ocelot
    conda install -y pywin32
    pip install --no-cache-dir https://github.com/OcelotProject/Ocelot/zipball/master

Otherwise, do:

.. code-block:: bash

    source activate ocelot
    pip install --no-cache-dir https://github.com/OcelotProject/Ocelot/zipball/master

.. note:: If you install from pypi, you will have to install the ``ocelot-lca`` package - someone pipped us during development!

If Ocelot is correctly installed, you should be able to run the command line application:

.. code-block:: bash

    ocelot-cli --help

To run Ocelot, you will need an unlinked database in `ecospold2 <http://www.ecoinvent.org/data-provider/data-provider-toolkit/ecospold2/ecospold2.html>`__ format.

Running on PyPy3
----------------

Instructions from:

* http://pypy.org/download.html
* http://pypy.readthedocs.io/en/latest/faq.html#module-xyz-does-not-work-with-pypy-importerror
* https://bitbucket.org/pypy/compatibility/wiki/lxml

We are also testing Ocelot on PyPy3. Instructions for OS X, assuming virtualenv is installed already:

#. Download binary from http://pypy.org/download.html; decompress and put somewhere.
#. Put the pypy ``bin`` directory on your path: ``export PATH=/Users/cmutel/Source/pypy3.3-v5.2.0-alpha1-osx64/bin:$PATH``
#. Install pip: ``pypy3 -m ensurepip``. Note that pip3 is now the pypy pip.
#. Install some dependencies: ``pip3 install Cython``.

This doesn't work: ``virtualenv -p /usr/local/bin/pypy3 /Users/cmutel/local-pypy/ocelot``:

.. code-block:: bash

    Running virtualenv with interpreter /usr/local/bin/pypy3
    Using base prefix '/Users/cmutel/Source/pypy3.3-v5.2.0-alpha1-osx64'
    New pypy executable in /Users/cmutel/local-pypy/ocelot/bin/pypy3
    Also creating executable in /Users/cmutel/local-pypy/ocelot/bin/pypy
    Installing setuptools, pip, wheel...
      Complete output from command /Users/cmutel/local-pypy/ocelot/bin/pypy3 -c "import sys, pip; sys...d\"] + sys.argv[1:]))" setuptools pip wheel:
      Ignoring indexes: https://pypi.python.org/simple
    Collecting setuptools
    Exception:
    Traceback (most recent call last):
      File "/opt/local/Library/Frameworks/Python.framework/Versions/3.5/lib/python3.5/site-packages/virtualenv_support/pip-7.1.2-py2.py3-none-any.whl/pip/basecommand.py", line 211, in main
        status = self.run(options, args)
      File "/opt/local/Library/Frameworks/Python.framework/Versions/3.5/lib/python3.5/site-packages/virtualenv_support/pip-7.1.2-py2.py3-none-any.whl/pip/commands/install.py", line 294, in run
        requirement_set.prepare_files(finder)
      File "/opt/local/Library/Frameworks/Python.framework/Versions/3.5/lib/python3.5/site-packages/virtualenv_support/pip-7.1.2-py2.py3-none-any.whl/pip/req/req_set.py", line 334, in prepare_files
        functools.partial(self._prepare_file, finder))
      File "/opt/local/Library/Frameworks/Python.framework/Versions/3.5/lib/python3.5/site-packages/virtualenv_support/pip-7.1.2-py2.py3-none-any.whl/pip/req/req_set.py", line 321, in _walk_req_to_install
        more_reqs = handler(req_to_install)
      File "/Users/cmutel/Source/pypy3.3-v5.2.0-alpha1-osx64/lib_pypy/_functools.py", line 66, in __call__
        return self._func(*(self._args + fargs), **fkeywords)
      File "/opt/local/Library/Frameworks/Python.framework/Versions/3.5/lib/python3.5/site-packages/virtualenv_support/pip-7.1.2-py2.py3-none-any.whl/pip/req/req_set.py", line 535, in _prepare_file
        dist = abstract_dist.dist(finder)
      File "/opt/local/Library/Frameworks/Python.framework/Versions/3.5/lib/python3.5/site-packages/virtualenv_support/pip-7.1.2-py2.py3-none-any.whl/pip/req/req_set.py", line 104, in dist
        self.req_to_install.source_dir))[0]
    IndexError: list index out of range
    ----------------------------------------
    ...Installing setuptools, pip, wheel...done.
    Traceback (most recent call last):
      File "/opt/local/Library/Frameworks/Python.framework/Versions/3.5/lib/python3.5/site-packages/virtualenv.py", line 2363, in <module>
        main()
      File "/opt/local/Library/Frameworks/Python.framework/Versions/3.5/lib/python3.5/site-packages/virtualenv.py", line 832, in main
        symlink=options.symlink)
      File "/opt/local/Library/Frameworks/Python.framework/Versions/3.5/lib/python3.5/site-packages/virtualenv.py", line 1004, in create_environment
        install_wheel(to_install, py_executable, search_dirs)
      File "/opt/local/Library/Frameworks/Python.framework/Versions/3.5/lib/python3.5/site-packages/virtualenv.py", line 969, in install_wheel
        'PIP_NO_INDEX': '1'
      File "/opt/local/Library/Frameworks/Python.framework/Versions/3.5/lib/python3.5/site-packages/virtualenv.py", line 910, in call_subprocess
        % (cmd_desc, proc.returncode))
    OSError: Command /Users/cmutel/local-pypy/ocelot/bin/pypy3 -c "import sys, pip; sys...d\"] + sys.argv[1:]))" setuptools pip wheel failed with error

Also, pip3 can't build lxml:

.. code-block:: bash

    Command "/Users/cmutel/Source/pypy3.3-v5.2.0-alpha1-osx64/bin/pypy3 -u -c "import setuptools, tokenize;__file__='/private/var/folders/1r/qbs5ybm90j5b6443gqcczddm0000gn/T/pip-build-tifstl/lxml/setup.py';exec(compile(getattr(tokenize, 'open', open)(__file__).read().replace('\r\n', '\n'), __file__, 'exec'))" install --record /var/folders/1r/qbs5ybm90j5b6443gqcczddm0000gn/T/pip-6wl27e-record/install-record.txt --single-version-externally-managed --compile" failed with error code 1 in /private/var/folders/1r/qbs5ybm90j5b6443gqcczddm0000gn/T/pip-build-tifstl/lxml/
    dhcp-10-24-137-123:~ cmutel$ pip3 install -e git+git@github.com:lxml/lxml.git#egg=lxml
    Obtaining lxml from git+git@github.com:lxml/lxml.git#egg=lxml
      Cloning git@github.com:lxml/lxml.git to ./src/lxml
    Installing collected packages: lxml
      Running setup.py develop for lxml
        Complete output from command /Users/cmutel/Source/pypy3.3-v5.2.0-alpha1-osx64/bin/pypy3 -c "import setuptools, tokenize;__file__='/Users/cmutel/src/lxml/setup.py';exec(compile(getattr(tokenize, 'open', open)(__file__).read().replace('\r\n', '\n'), __file__, 'exec'))" develop --no-deps:
        Building lxml version 3.6.0.
        Building without Cython.
        Using build configuration of libxslt 1.1.28
        Building against libxml2/libxslt in the following directory: /opt/local/lib
        running develop
        running egg_info
        writing src/lxml.egg-info/PKG-INFO
        writing dependency_links to src/lxml.egg-info/dependency_links.txt
        writing requirements to src/lxml.egg-info/requires.txt
        writing top-level names to src/lxml.egg-info/top_level.txt
        warning: manifest_maker: standard file '-c' not found

        reading manifest file 'src/lxml.egg-info/SOURCES.txt'
        reading manifest template 'MANIFEST.in'
        warning: no files found matching '*.html' under directory 'doc'
        writing manifest file 'src/lxml.egg-info/SOURCES.txt'
        running build_ext
        building 'lxml.etree' extension
        creating build
        creating build/temp.macosx-10.11-x86_64-3.3
        creating build/temp.macosx-10.11-x86_64-3.3/src
        creating build/temp.macosx-10.11-x86_64-3.3/src/lxml
        cc -arch x86_64 -O2 -fPIC -Wimplicit -I/opt/local/include -I/opt/local/include/libxml2 -Isrc/lxml/includes -I/Users/cmutel/Source/pypy3.3-v5.2.0-alpha1-osx64/include -c src/lxml/lxml.etree.c -o build/temp.macosx-10.11-x86_64-3.3/src/lxml/lxml.etree.o -w -flat_namespace
        src/lxml/lxml.etree.c:222291:46: error: expected expression
                    value = ((PyStopIterationObject *)ev)->value;
                                                     ^
        src/lxml/lxml.etree.c:222291:23: error: use of undeclared identifier 'PyStopIterationObject'
                    value = ((PyStopIterationObject *)ev)->value;
                              ^
        src/lxml/lxml.etree.c:222338:38: error: expected expression
            value = ((PyStopIterationObject *)ev)->value;
                                             ^
        src/lxml/lxml.etree.c:222338:15: error: use of undeclared identifier 'PyStopIterationObject'
            value = ((PyStopIterationObject *)ev)->value;
                      ^
        4 errors generated.
        Compile failed: command 'cc' failed with exit status 1
        creating var
        creating var/folders
        creating var/folders/1r
        creating var/folders/1r/qbs5ybm90j5b6443gqcczddm0000gn
        creating var/folders/1r/qbs5ybm90j5b6443gqcczddm0000gn/T
        cc -arch x86_64 -O2 -fPIC -Wimplicit -I/opt/local/include -I/opt/local/include/libxml2 -I/usr/include/libxml2 -c /var/folders/1r/qbs5ybm90j5b6443gqcczddm0000gn/T/xmlXPathInitxb6btg.c -o var/folders/1r/qbs5ybm90j5b6443gqcczddm0000gn/T/xmlXPathInitxb6btg.o
        /var/folders/1r/qbs5ybm90j5b6443gqcczddm0000gn/T/xmlXPathInitxb6btg.c:2:1: warning: type specifier missing, defaults to 'int' [-Wimplicit-int]
        main (int argc, char **argv) {
        ^
        1 warning generated.
        cc -arch x86_64 var/folders/1r/qbs5ybm90j5b6443gqcczddm0000gn/T/xmlXPathInitxb6btg.o -L/opt/local/lib -lxml2 -o a.out
        error: command 'cc' failed with exit status 1

        ----------------------------------------
    Command "/Users/cmutel/Source/pypy3.3-v5.2.0-alpha1-osx64/bin/pypy3 -c "import setuptools, tokenize;__file__='/Users/cmutel/src/lxml/setup.py';exec(compile(getattr(tokenize, 'open', open)(__file__).read().replace('\r\n', '\n'), __file__, 'exec'))" develop --no-deps" failed with error code 1 in /Users/cmutel/src/lxml/
