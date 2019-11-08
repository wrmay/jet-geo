package com.hazelcast.sample.jet.geo.server;

import com.hazelcast.core.HazelcastInstance;
import com.hazelcast.jet.Jet;
import com.hazelcast.jet.JetInstance;

public class Server
{
    public static void main( String[] args ) {
        JetInstance jet = Jet.newJetInstance();
        HazelcastInstance hz = jet.getHazelcastInstance();
    }
}