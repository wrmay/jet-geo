#!/bin/bash
here=`dirname $0`

java -cp $here/jet-server/target/jet-server-1.0-SNAPSHOT.jar \
  -Dhazelcast.config=$here/hazelcast-config/local/hazelcast.xml \
  com.hazelcast.sample.jet.geo.server.Server
