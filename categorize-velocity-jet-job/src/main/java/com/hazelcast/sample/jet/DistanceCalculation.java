package com.hazelcast.sample.jet;


public class DistanceCalculation {
    public static void main(String []args){
        double lat1 = 33.0 + 43.0/60.0 + 26.99/3600.0;
        double lon1 = 84.0 + 20.0/60.0 + 57.94 / 3600.0;

        double lat2 = 33.0 + 43.0/60.0 + 26.67 / 3600.0;
        double lon2 = 84.0 + 20.0/60.0 + 38.85 / 3600.0;

        double R = 6371000;

        double phi1 = Math.toRadians(lat1);
        double phi2 = Math.toRadians(lat2);
        double deltaPhi = phi2- phi1;
        double deltaLambda = Math.toRadians(lon2) - Math.toRadians(lon1);

        double a = Math.pow(Math.sin(deltaPhi / 2.0), 2.0) + Math.cos(phi1) * Math.cos(phi2) * Math.pow(Math.sin(deltaLambda / 2.0), 2.0);
        double c = 2.0 * Math.atan2(Math.sqrt(a), Math.sqrt(1.0 - a));
        double d = R*c;

        System.out.println(String.format("D=%fM", d));
    }
}
