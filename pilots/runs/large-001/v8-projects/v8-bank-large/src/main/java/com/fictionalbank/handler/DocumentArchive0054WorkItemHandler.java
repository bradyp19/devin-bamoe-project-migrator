package com.fictionalbank.handler;

import java.util.HashMap;
import java.util.Map;

import org.kie.api.runtime.process.WorkItem;
import org.kie.api.runtime.process.WorkItemHandler;
import org.kie.api.runtime.process.WorkItemManager;

/** Fictional deposits integration stub (synthetic pilot fixture; no external system). */
public class DocumentArchive0054WorkItemHandler implements WorkItemHandler {

    @Override
    public void executeWorkItem(WorkItem workItem, WorkItemManager manager) {
        Object reference = workItem.getParameter("Reference");
        Map<String, Object> results = new HashMap<>();
        results.put("Result", "DocumentArchive0054:" + reference);
        manager.completeWorkItem(workItem.getId(), results);
    }

    @Override
    public void abortWorkItem(WorkItem workItem, WorkItemManager manager) {
        manager.abortWorkItem(workItem.getId());
    }
}
