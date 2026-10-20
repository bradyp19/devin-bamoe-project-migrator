# Appendix for engineers building locally: BAMOE Maven Repository Access

> **CRITICAL:** The BAMOE Maven repository is **not on the public internet**. It is a private IBM artifact registry distributed as either:
>
> 1. **A container image** (`quay.io/bamoe/maven-repository`) — you run it locally, it exposes a web server, and `settings.xml` points to `http://localhost:<PORT>`
> 2. **A ZIP file** (`bamoe-{VERSION}-maven-repository.zip`) — downloaded from IBM Passport Advantage, extracted locally, and `settings.xml` points to `file:///path/to/extracted/repo`
>
> **Devin cannot access either of these on its own** — the container image requires Docker running on the build machine, and the ZIP requires an IBM Passport Advantage login. This is a hard blocker for any cloud-hosted agent, including Devin, because there is no public URL for the artifacts.
>
> You must configure one of the three options below before any sub-task can proceed.

## Option A — Run the Maven repo container locally and expose it (best for demos)

On the machine where Devin will build:
```bash
docker run -d --platform linux/amd64 -p 9999:8080 quay.io/bamoe/maven-repository:9.5.2-ibm-0002
```

Then add a `settings.xml` to the repo pointing at your machine's IP:
```xml
<profile>
  <id>ibm-bamoe-enterprise-maven-repository</id>
  <repositories>
    <repository>
      <id>ibm-bamoe-enterprise-maven-repository</id>
      <url>http://localhost:9999/</url>
      <releases>
        <enabled>true</enabled>
      </releases>
      <snapshots>
        <enabled>false</enabled>
      </snapshots>
    </repository>
  </repositories>
  <pluginRepositories>
    <pluginRepository>
      <id>ibm-bamoe-enterprise-maven-repository</id>
      <url>http://localhost:9999/</url>
      <releases>
        <enabled>true</enabled>
      </releases>
      <snapshots>
        <enabled>false</enabled>
      </snapshots>
    </pluginRepository>
  </pluginRepositories>
</profile>
```

Activate the profile:
```xml
<activeProfiles>
  <activeProfile>ibm-bamoe-enterprise-maven-repository</activeProfile>
</activeProfiles>
```

Devin's machine needs network access to that IP. This only works if Devin runs builds on your machine or a VM you control.

## Option B — Deploy the Maven repo to a stable URL (best for customers)

Use the Helm chart to deploy `quay.io/bamoe/maven-repository` to an OpenShift/Kubernetes cluster. It exposes a persistent HTTPS URL. Customers configure `settings.xml` to point to that URL. Devin can then reach it.

```bash
helm pull oci://quay.io/bamoe/dmoe-dev-environment-helm-chart --version=9.5.2-ibm-0002 --untar
helm install my-bamoe-dev-env ./dmoe-dev-environment-helm-chart ...
# Maven repo becomes available at https://maven-repository.<YOUR_DOMAIN>
```

If the repo is reachable at a stable URL, you can also store that URL as the `BAMOE_MAVEN_REPO_URL` Devin secret — Devin will then use the "Convert + verify" build mode automatically (see `templates/settings.xml`).

## Option C — Pre-populate the local Maven cache (workaround)

Extract the ZIP from IBM Passport Advantage into `~/.m2/repository` on the Devin build machine. No running container needed — Maven finds the JARs locally. This is the path if you don't have a cluster.

## Verification

Before starting any sub-task, verify Maven can resolve BAMOE dependencies:
```bash
mvn dependency:resolve
```

All dependencies must resolve without error before proceeding with Sub-Task 1.
