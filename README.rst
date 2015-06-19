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


Look at the testing code
========================

The actual code required to run the tests can be found under the tests/ folder.
