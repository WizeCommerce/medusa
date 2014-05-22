#!/bin/bash
which nosetests >& /dev/null

if [ "$?" -ne 0 ]; then
    echo "nosetests is not installed, please install python-nose and try again."
    exit 2
fi

nosetests


if [ "$?" -ne 0 ]; then
    echo "Tests failed"
    exit 1
fi

$(pwd)/publishClients.py  $@
