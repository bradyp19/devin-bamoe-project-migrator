package com.fictionalbank.handler;

import java.util.HashMap;
import java.util.Map;

import org.kie.api.runtime.process.WorkItem;
import org.kie.api.runtime.process.WorkItemHandler;
import org.kie.api.runtime.process.WorkItemManager;
import org.jbpm.process.workitem.core.util.Wid;

/** Fictional fraud integration stub (synthetic pilot fixture; no external system). */
@Wid(widfile = "WorkDefinitions.wid", name = "CreditBureauLookup0035", displayName = "CreditBureauLookup0035")
public class CreditBureauLookup0035WorkItemHandler implements WorkItemHandler {

    @Override
    public void executeWorkItem(WorkItem workItem, WorkItemManager manager) {
        Object reference = workItem.getParameter("Reference");
        Map<String, Object> results = new HashMap<>();
        results.put("Result", "CreditBureauLookup0035:" + reference);
        manager.completeWorkItem(workItem.getId(), results);
    }

    @Override
    public void abortWorkItem(WorkItem workItem, WorkItemManager manager) {
        manager.abortWorkItem(workItem.getId());
    }
}
