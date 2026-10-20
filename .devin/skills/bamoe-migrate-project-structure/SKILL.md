---
name: bamoe-migrate-project-structure
description: Migrates the v8 project structure and POM to v9, replacing KJAR packaging with standard Maven JAR and updating dependencies.
---

# BAMOE Migrate Project Structure and POM

Migrates the v8 project structure and POM to v9, replacing KJAR packaging with standard Maven JAR and updating dependencies.

## When to Use

Use this skill to:
- Create the v9 project structure from v8
- Replace v8 POM with v9-compatible POM
- Delete v8 configuration files
- Create application.properties skeleton
- Verify the build succeeds

## Prerequisites

- v8 project must be in `v8-projects/<project-name>/`
- Java 21+ installed
- Maven 3.9.11+ installed
- BAMOE Maven Repository configured in `~/.m2/settings.xml`
- Sub-Task 1 (Audit) must be completed first

## What This Skill Does

1. Creates v9 output directory: `v9-projects/<v9-name>/` (replaces `v8-` prefix with `v9-`)
2. Copies BPMN and SVG files from v8 to v9
3. Creates new `pom.xml` with:
   - Packaging changed from `kjar` to `jar`
   - BAMOE Quarkus BOM imported
   - Quarkus BOM imported
   - Kogito workflow dependencies added
   - v8 dependencies removed (kie-api, kie-internal, kie-maven-plugin)
   - JUnit upgraded to JUnit 5
4. Deletes v8 configuration files (not copied to v9):
   - kmodule.xml
   - kie-deployment-descriptor.xml
   - persistence.xml
   - project.imports
   - project.repositories
5. Creates `application.properties` with:
   - Server configuration (port, log level)
   - H2 database for development
   - Kogito persistence configuration
   - Security disabled for development
   - OpenAPI/Swagger enabled
6. Runs `mvn clean package -DskipTests` to verify build

## Expected Output

- v9 project structure created at `v9-projects/<v9-name>/`
- Build succeeds with `mvn clean package -DskipTests`
- All v8 configuration files removed
- application.properties created with v9 skeleton

## Notes

- This skill follows the reference template from BAMOE Canvas Quarkus Accelerator
- The project groupId, artifactId, and version are preserved from v8 pom.xml
- For production, you'll need to:
  - Configure PostgreSQL/Oracle/SQL Server database
  - Enable OIDC security
  - Add additional Quarkus profiles (prod, container)
