pynium
======

Some testing around py.test and python selenium integration. For now,
just to see what I could do with that.


.. image:: https://travis-ci.org/parkouss/pynium.svg?branch=master
    :target: https://travis-ci.org/parkouss/pynium


playing with pynium
===================

.. code-block:: bash

  # clone the repo
  git clone https://github.com/parkouss/pynium
  cd pynium

  # install pynium in a clean virtualenv
  virtualenv venv
  . venv/bin/activate
  pip install -e .

  # run the tests (this will use firefox)
  py.test tests/


Samples of testing code
=======================

You can look at some sample test code, provided in the test-samples/ folder.
