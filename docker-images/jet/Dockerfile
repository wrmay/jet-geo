FROM hazelcast/hazelcast-jet 

COPY hazelcast.xml /opt/hazelcast-jet/config/hazelcast.xml 
COPY jmx_prometheus_javaagent-0.12.0.jar /opt/hazelcast-jet/lib/jmx_prometheus_javaagent.jar

ENV JAVA_OPTS "-Dhazelcast.config=/opt/hazelcast-jet/config/hazelcast.xml -Xmx2g -Dhazelcast.jmx=true"
ENV PROMETHEUS_PORT 8080 