package com.fictionalbank.handler;

import java.util.HashMap;
import java.util.Map;

import org.kie.api.runtime.process.WorkItem;
import org.kie.api.runtime.process.WorkItemHandler;
import org.kie.api.runtime.process.WorkItemManager;
import org.jbpm.process.workitem.core.util.Wid;

/** Fictional cards integration stub (synthetic pilot fixture; no external system). */
@Wid(widfile = "WorkDefinitions.wid", name = "LedgerPosting0017", displayName = "LedgerPosting0017")
public class LedgerPosting0017WorkItemHandler implements WorkItemHandler {

    @Override
    public void executeWorkItem(WorkItem workItem, WorkItemManager manager) {
        Object reference = workItem.getParameter("Reference");
        Map<String, Object> results = new HashMap<>();
        results.put("Result", "LedgerPosting0017:" + reference);
        manager.completeWorkItem(workItem.getId(), results);
    }

    @Override
    public void abortWorkItem(WorkItem workItem, WorkItemManager manager) {
        manager.abortWorkItem(workItem.getId());
    }
}
