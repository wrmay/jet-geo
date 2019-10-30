package com.hazelcast.sample.jet.geo.server;

import com.hazelcast.core.EntryEvent;
import com.hazelcast.core.HazelcastJsonValue;
import com.hazelcast.logging.ILogger;
import com.hazelcast.logging.Logger;
import com.hazelcast.map.listener.EntryAddedListener;
import com.hazelcast.map.listener.EntryUpdatedListener;

public class PingMapListener implements EntryAddedListener<Integer, HazelcastJsonValue>, EntryUpdatedListener<Integer,HazelcastJsonValue> {
    private ILogger log = Logger.getLogger(PingMapListener.class);

    @Override
    public void entryAdded(EntryEvent<Integer, HazelcastJsonValue> entryEvent) {
        log.info(entryEvent.getValue().toString());
    }

    @Override
    public void entryUpdated(EntryEvent<Integer, HazelcastJsonValue> entryEvent) {
        log.info(entryEvent.getValue().toString());
    }
}
