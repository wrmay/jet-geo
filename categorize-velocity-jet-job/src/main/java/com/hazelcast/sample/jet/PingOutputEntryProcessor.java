package com.hazelcast.sample.jet;

import com.hazelcast.map.EntryBackupProcessor;
import com.hazelcast.map.EntryProcessor;

import java.io.Serializable;
import java.util.Map;

public class PingOutputEntryProcessor implements EntryProcessor<Integer,String> , EntryBackupProcessor<Integer,String>, Serializable {

    private String newCategory;

    public PingOutputEntryProcessor(String cat){
        newCategory= cat;
    }

    @Override
    public void processBackup(Map.Entry<Integer, String> entry) {
        process(entry);
    }

    @Override
    public Object process(Map.Entry<Integer, String> entry) {
        String val = entry.getValue();
        if ( val == null || !val.equals(newCategory)) entry.setValue(newCategory);
        return newCategory;
    }

    @Override
    public EntryBackupProcessor<Integer, String> getBackupProcessor() {
        return this;
    }
}
