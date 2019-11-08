#!/bin/bash
docker-compose run member-1 java -cp  /opt/project/jet-server/target/jet-server-1.0-SNAPSHOT.jar -Dhazelcast.client.config=/opt/project/hazelcast-config/hazelcast-client.xml com.hazelcast.jet.server.JetCommandLine  -v submit /opt/project/categorize-velocity-jet-job/target/categorize-velocity-jet-job-1.0-SNAPSHOT.jar
