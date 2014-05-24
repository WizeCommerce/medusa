#!/bin/bash
mkdir thrift_work
wget "http://mirror.olnevhost.net/pub/apache/thrift/0.9.1/thrift-0.9.1.tar.gz" -O thrift_work/thrift-0.9.1.tar.gz
cd thrift_work
tar xvfz thrift-0.9.1.tar.gz
cd thrift-0.9.1
./configure --with-java --with-ruby --without-cpp --without-python --without-php --without-c_glib --without-go --without-erlang --without-ruby  && make && sudo make install 
