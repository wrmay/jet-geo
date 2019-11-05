package com.hazelcast.sample.jet.geo.server;

import com.hazelcast.core.*;
import com.hazelcast.jet.Jet;
import com.hazelcast.jet.JetInstance;
import com.hazelcast.sample.jet.CategorizeVelocity;

public class Server
{
    public static void main( String[] args ) {
        JetInstance jet = Jet.newJetInstance();
        HazelcastInstance hz = jet.getHazelcastInstance();

        Member localMember = hz.getCluster().getLocalMember();
        Member firstMember = hz.getCluster().getMembers().iterator().next();
        if (localMember.getUuid().equals(firstMember.getUuid())){
            jet.newJob(CategorizeVelocity.buildPipeline());
        }

    }
}