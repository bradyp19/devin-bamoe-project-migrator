package com.fictionalbank.security;

import java.util.Arrays;
import java.util.List;

import org.kie.api.task.UserGroupCallback;

/** Fictional static group mapping (synthetic pilot fixture; no directory server). */
public class BranchUserGroupCallback0028 implements UserGroupCallback {
    private static final List<String> GROUPS = Arrays.asList("loan-officers", "card-ops", "kyc-analysts", "payments-desk", "risk-managers");
    @Override public boolean existsUser(String userId) { return userId != null; }
    @Override public boolean existsGroup(String groupId) { return GROUPS.contains(groupId); }
    @Override public List<String> getGroupsForUser(String userId) { return GROUPS; }
}
