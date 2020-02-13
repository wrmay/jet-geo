package com.hazelcast.sample.jet;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.hazelcast.core.HazelcastJsonValue;
import com.hazelcast.jet.JetInstance;
import com.hazelcast.jet.aggregate.AggregateOperation;
import com.hazelcast.jet.aggregate.AggregateOperation1;
import com.hazelcast.jet.datamodel.KeyedWindowResult;
import com.hazelcast.jet.datamodel.Tuple4;
import com.hazelcast.jet.pipeline.*;
import com.hazelcast.jet.server.JetBootstrap;

import java.util.Map;

public class CategorizeVelocity {
    public static void main(String []args){
        JetInstance jet = JetBootstrap.getInstance();
        jet.newJob(buildPipeline());
    }

    public static Pipeline buildPipeline(){
        Pipeline pipeline = Pipeline.create();

        // draw events from the ping_input Hazelcast map as HazelcastJsonValue
        StreamStage<Map.Entry<Integer, HazelcastJsonValue>> rawStream = pipeline.drawFrom(Sources.<Integer, HazelcastJsonValue>mapJournal("ping_input", JournalInitialPosition.START_FROM_CURRENT))
                .withoutTimestamps()
                .setName("HazelcastJsonValues from Hazelcast Map");

//        rawStream.drainTo(Sinks.logger());


        // convert map event to Tuple4 of Integer (id), Double (latitude), Double (longitude), Long (time)
        StreamStage<Tuple4<Integer, Double, Double, Long>> tupleStream = rawStream.map(entry -> toTuple(entry.getValue()))
                .setName("Convert to 4-tuples");

        StreamStageWithKey<Tuple4<Integer, Double, Double, Long>, Integer> timestampedTupleStream = tupleStream.addTimestamps(item -> item.f3(), 5000)
                .setName("Add timestamps and split by id")
                .groupingKey(item -> item.f0());

        StageWithKeyAndWindow<Tuple4<Integer, Double, Double, Long>, Integer> pingWindows = timestampedTupleStream.window(WindowDefinition.sliding(30000, 2000));

        AggregateOperation1<Tuple4<Integer, Double, Double, Long>, VelocityAccumulator, Double> velocityAggregator =
                AggregateOperation.withCreate(VelocityAccumulator::new)
                        .<Tuple4<Integer, Double, Double, Long>>andAccumulate((va, t) -> va.accumulate(t))
                        .andCombine((l, r) -> l.combine(r))
                        .andExportFinish(acc -> acc.getResult());

        StreamStage<KeyedWindowResult<Integer, Double>> velocities = pingWindows.aggregate(velocityAggregator)
                .setName("Calculate velocity");

        velocities.drainTo(Sinks.logger( item-> String.format("VELOCITY key=%04d velocity=%02.1f m/s",item.getKey(),item.getValue() )));

        velocities.drainTo(Sinks.mapWithEntryProcessor("ping_output", v -> v.getKey(), v -> new PingOutputEntryProcessor(categorizeVelocity(v.getValue())))).setName("Save to output map ");

        return pipeline;
    }

    private static final double conversionFactor = 3600.0/(0.0254 * 12 * 5280);

    // input in meters/second - output is a color code
    private static String categorizeVelocity(Double v){
        if (v.isNaN()) return "gray";

        double mph = v * conversionFactor;

        String result;
        if (mph < 5.0)
            result = "blue";
        else if (mph < 15 )
            result = "green";
        else if (mph < 75)
            result = "yellow";
        else
            result = "orange";

        return result;
    }

    private static ObjectMapper mapper = new ObjectMapper();

    private static Tuple4<Integer, Double, Double, Long>  toTuple(HazelcastJsonValue v){
        try {
            ObjectNode root = (ObjectNode) mapper.readTree(v.toString());
            return Tuple4.tuple4(root.get("id").asInt(), root.get("latitude").asDouble(), root.get("longitude").asDouble(), root.get("time").asLong());
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Could not parse HazelcastJsonValue: " + v.toString());
        }
    }
}
