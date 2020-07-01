FROM hazelcast/hazelcast-jet 

RUN apt-get install -y netcat

COPY hazelcast.xml /opt/hazelcast-jet/config/hazelcast.xml 
COPY jmx_prometheus_javaagent-0.12.0.jar /opt/hazelcast-jet/lib/jmx_prometheus_javaagent.jar

ENV JAVA_OPTS "-Dhazelcast.config=/opt/hazelcast-jet/config/hazelcast.xml -Dnetworkaddress.cache.ttl=0 -Dnetworkaddress.cache.negative.ttl=0 -Xmx2g -Dhazelcast.jmx=true"
ENV PROMETHEUS_PORT 8080 