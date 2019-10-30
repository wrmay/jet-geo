FROM adoptopenjdk/openjdk8:alpine
ADD https://download.hazelcast.com/hazelcast-jet-management-center/hazelcast-jet-management-center-3.2.tar.gz /tmp
ADD hazelcast-client.xml /etc/hazelcast/
WORKDIR /opt
RUN tar -xzf /tmp/hazelcast-jet-management-center-3.2.tar.gz
CMD java -jar /opt/hazelcast-jet-management-center-3.2/hazelcast-jet-management-center-3.2.jar -c /etc/hazelcast/hazelcast-client.xml
