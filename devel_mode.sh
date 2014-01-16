#!/bin/bash
#TEST_BIN=py.test
#OPTIONS="--cov-report  html --cov thrift_medusa tests"
##TEST_BIN=nosetests
#which ${TEST_BIN} >& /dev/null
#
#if [ "$?" -ne 0 ]; then
#    echo "$TEST_BIN is not installed, please install python-nose and try again."
#    exit 2
#fi
#
#exec ${TEST_BIN} ${OPTIONS} 
#
#
#if [ "$?" -ne 0 ]; then
#    echo "Tests failed"
#    exit 1
#fi

$(pwd)/publishClients.py  $@
