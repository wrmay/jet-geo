package com.hazelcast.sample.jet;

import com.hazelcast.jet.datamodel.Tuple4;
import com.hazelcast.logging.ILogger;
import com.hazelcast.logging.Logger;

import java.io.Serializable;

public class VelocityAccumulator  implements Serializable {
    private static ILogger log = Logger.getLogger(VelocityAccumulator.class);

    private int id;
    private double earliestLat;
    private double earliestLon;
    private double latestLat;
    private double latestLon;
    private long earliestTime;
    private long latestTime;
    private int count;

    /*
     * Tuple4 is id, lat, lon, time
     */
    public void accumulate(Tuple4<Integer, Double,Double,Long> ping){
        id = ping.f0();

        ++count;
        if (earliestTime == 0 || ping.f3() < earliestTime){
            earliestTime = ping.f3();
            earliestLat = ping.f1();
            earliestLon = ping.f2();
        }

        if (latestTime == 0 || ping.f3() > latestTime){
            latestTime = ping.f3();
            latestLat = ping.f1();
            latestLon = ping.f2();
        }
    }

    public void combine(VelocityAccumulator va){
        //log.warning("UNEXPECTED: VelocityAccumulator.combine was called.");
        count += va.count;

        // do nothing if both are uninitialized
        if (earliestTime != 0 || va.earliestTime != 0){
            if (earliestTime == 0 ){
                // if this one is uninitialized take the other one
                copyEarliestFrom(va);
            } else if (va.earliestTime != 0){
                // if va is initialized, compare and take the earliest, otherwise keep this one
                if (va.earliestTime < earliestTime) copyEarliestFrom(va);
            }
        }
        
        // do nothing if both are uninitialized
        if (latestTime != 0 || va.latestTime != 0){
            if (latestTime == 0 ){
                // if this one is uninitialized take the other one
                copyLatestFrom(va);
            } else if (va.latestTime != 0){
                // if va is initialized, compare and take the latest, otherwise keep this one
                if (va.latestTime > latestTime) copyLatestFrom(va);
            }
        }
    }

    // returns the velocity in meters per second
    public Double getResult(){
        double R = 6371000;

        double phi1 = Math.toRadians(earliestLat);
        double phi2 = Math.toRadians(latestLat);
        double deltaPhi = phi2- phi1;
        double deltaLambda = Math.toRadians(latestLon) - Math.toRadians(earliestLon);

        double a = Math.pow(Math.sin(deltaPhi / 2.0), 2.0) + Math.cos(phi1) * Math.cos(phi2) * Math.pow(Math.sin(deltaLambda / 2.0), 2.0);
        double c = 2.0 * Math.atan2(Math.sqrt(a), Math.sqrt(1.0 - a));
        double distance = R*c;

        double time = latestTime - earliestTime;
//        log.info(String.format("%d traveling at %f m/s as of %d", id, distance / time, latestTime));
        return distance / time;
    }

    private void copyEarliestFrom(VelocityAccumulator va){
        this.earliestTime = va.earliestTime;
        this.earliestLat = va.earliestLat;
        this.earliestLon = va.earliestLon;
    }
    
    private void copyLatestFrom(VelocityAccumulator va){
        this.latestTime = va.latestTime;
        this.latestLat = va.latestLat;
        this.latestLon = va.latestLon;
    }
}
