---
name: bamoe-configure-maven-repository
description: Configures Maven to use the BAMOE Maven Repository for dependency resolution.
---

# BAMOE Configure Maven Repository

Configures Maven to use the BAMOE Maven Repository for dependency resolution.

## Where things live

- `<plugin-root>` — the folder containing `.devin-plugin/plugin.json`, i.e. two levels above this `SKILL.md`. Holds `bamoe-v8-to-v9-migration-plan.md`, `templates/`, `v8-to-v9-migration-samples/`, and `docs/tutorial-index.md`. Resolve these with the skill's source path; never assume they are in the current directory.
- `<work-dir>` — the user's current working directory. Input is `<work-dir>/v8-projects/<name>/`, or a path the user named explicitly; output is always `<work-dir>/v9-projects/<name>/`.
- When this plugin repo itself is the working directory, the two are the same folder.

## When to Use

Use this skill to:
- Set up BAMOE Maven Repository access for the first time
- Switch between container-based and local file-based repository
- Verify Maven repository configuration

## Prerequisites

- BAMOE Maven Repository downloaded (ZIP file or container image)
- Maven 3.9.11+ installed
- Rancher Desktop or Docker (if using container-based approach)

## What This Skill Does

### Option 1: Local File-Based Repository (Recommended)

1. Checks if BAMOE Maven Repository ZIP is downloaded and extracted
2. Creates/updates `~/.m2/settings.xml` with:
   - Repository pointing to local file path (e.g., `file:///Users/<user>/Downloads/bamoe-maven-repository-zip-<version>/`)
   - PluginRepository pointing to same path
   - Profile activated
3. Tests configuration with `mvn dependency:resolve`

### Option 2: Container-Based Repository

1. Pulls BAMOE Maven Repository container image:
   ```bash
   docker pull quay.io/bamoe/maven-repository:<version>
   ```
2. Runs container on Apple Silicon:
   ```bash
   docker run -d --platform linux/amd64 -p 9999:8080 quay.io/bamoe/maven-repository:<version>
   ```
3. Creates/updates `~/.m2/settings.xml` with:
   - Repository pointing to `http://localhost:9999/`
   - PluginRepository pointing to same URL
   - Profile activated
4. Tests configuration with `mvn dependency:resolve`

## Expected Output

- `~/.m2/settings.xml` configured with BAMOE Maven Repository
- `mvn dependency:resolve` succeeds against a test POM
- BAMOE dependencies can be resolved from the configured repository

## Notes

- Local file-based repository is faster and more reliable (no container dependency)
- Container-based approach is useful if you want to share the repository across a team
- Common BAMOE versions: 9.3.1-ibm-0006, 9.5.2-ibm-0002, 9.6.0-ibm-0004
- The repository is private and not available in Maven Central
