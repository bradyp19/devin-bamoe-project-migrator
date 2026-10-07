# BAMOE Deploy and Verify

Deploys the migrated v9 service and verifies it works correctly.

## When to Use

Use this skill to:
- Deploy the v9 service locally or to OpenShift
- Verify Swagger UI is accessible
- Test process definitions and REST endpoints
- Smoke-test the migrated application

## Prerequisites

- All migration sub-tasks completed
- PostgreSQL (or SQL Server/Oracle) database provisioned for production
- Quarkus Dev Mode or container image built
- OpenShift CLI (oc) if deploying to OpenShift

## What This Skill Does

### Local Deployment (Dev Mode)

1. Configures persistence in `application.properties`:
   - Sets datasource URL, username, password
   - Sets `kogito.persistence.type=jdbc`
   - Sets `quarkus.hibernate-orm.database.generation=update`
2. Runs `mvn clean quarkus:dev`
3. Verifies at `http://localhost:8080/q/swagger-ui/#/`

### OpenShift Deployment

1. Builds container image:
   ```bash
   mvn clean package -Dquarkus.container-image.build=true
   ```
2. Deploys using Helm chart or `oc` commands
3. Verifies Swagger UI at deployment endpoint

### Verification Steps

1. Access Swagger UI
2. Test process definitions via REST endpoints
3. Verify user tasks are accessible
4. Check database schema created correctly
5. Test security (if enabled)

## Expected Output

- Service deployed and accessible
- Swagger UI reachable at `/q/swagger-ui/#/`
- Process definitions and REST endpoints working
- Database persistence functioning
- No runtime errors

## Notes

- For production, use PostgreSQL, SQL Server, or Oracle (not H2)
- v8 and v9 databases are incompatible - use side-by-side parallel run for live data
- New database is required (binary persistence format changed)
- Parallel run strategy: new instances → v9, existing instances → v8 until completion
