# BAMOE Migrate Security and Authentication

Migrates v8 security (WildFly JAAS/LDAP) to v9 OIDC-based authentication.

## When to Use

Use this skill to:
- Replace WildFly JAAS with OIDC (Keycloak or any compliant IdP)
- Migrate UserGroupCallback to IdentityProvider
- Replace AssignmentStrategy with UserTaskAssignmentStrategy
- Configure security in application.properties

## Prerequisites

- v9 project structure created (Sub-Task 2)
- OIDC provider (Keycloak or other) available
- Sub-Task 1 (Audit) completed to identify security classes

## What This Skill Does

1. Removes v8 security classes (if present):
   - UserGroupCallback implementations
   - JAASUserGroupCallbackImpl, DBUserGroupCallbackImpl, LDAPUserGroupCallbackImpl
   - PropsUserGroupCallbackImpl
2. Migrates to IdentityProvider:
   - Implements IdentityProvider interface or uses QuarkusIdentityProvider (injected automatically)
   - Replaces user/group resolution with IdP token claims
3. Configures OIDC in `application.properties`:
   - For Quarkus: adds `quarkus-oidc` dependency, sets `quarkus.oidc.auth-server-url`, `client-id`, `credentials.secret`
   - For Spring Boot: adds `spring-boot-starter-oauth2-resource-server`, configures `spring.security.oauth2.*`
4. For non-secured dev mode: sets `kogito.security.auth.enabled=false` and query params for task endpoints
5. Migrates custom AssignmentStrategy:
   - Implements UserTaskAssignmentStrategy
   - Overrides `computeAssignment(UserTaskInstance, IdentityProvider)`
6. If Management Console used: adds OIDC proxy dependencies

## Expected Output

- No UserGroupCallback implementations remain
- OIDC configured in application.properties
- Custom AssignmentStrategy replaced with UserTaskAssignmentStrategy
- Security working with OIDC provider (or disabled for dev mode)

## Notes

- Direct LDAP integration is replaced by IdP group membership via OIDC token claims
- For dev/testing, security can be disabled: `kogito.security.auth.enabled=false`
- Use query params for task endpoints in non-secured mode: `?user=admin&group=Manager`
- v8 service APIs (`org.jbpm.services.api.*`) are not available in v9 - use auto-generated REST endpoints
