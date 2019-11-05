package com.hazelcast.sample.jet.geo.server;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.hazelcast.core.HazelcastJsonValue;
import com.hazelcast.map.MapInterceptor;

public class InputInterceptor implements MapInterceptor {

    private ObjectMapper mapper;

    public InputInterceptor(){
        mapper = new ObjectMapper();
    }

    @Override
    public Object interceptGet(Object o) {
        return o;
    }

    @Override
    public void afterGet(Object o) {

    }

    @Override
    public Object interceptPut(Object oldValue, Object newValue) {
        if  (newValue instanceof HazelcastJsonValue){
            try {
                ObjectNode objectNode = (ObjectNode) mapper.readTree(newValue.toString());
                return objectNode;
            } catch (JsonProcessingException x) {
                throw new RuntimeException("Could not parse entry as JSON: \"" + newValue.toString() + "\"");
            }
        } else {
            return newValue;
        }
    }

    @Override
    public void afterPut(Object o) {

    }

    @Override
    public Object interceptRemove(Object o) {
        return o;
    }

    @Override
    public void afterRemove(Object o) {

    }
}
