#!/usr/bin/env bash
# validate-migration.sh — mechanical validation of a BAMOE v9.5 migration output.
#
# Usage: tools/validate-migration.sh <v9-project-dir> [v8-project-dir]
#
# Prints PASS / FAIL / WARN / SKIP per check and a summary. Exit code is 1 if any
# check FAILs, 0 otherwise (WARN and SKIP do not fail the run). This script is
# report-only: it never writes or modifies any file. Honest status recording in
# migration-status.md remains a deliberate human/agent step.
#
# Contract reference: docs/migration-output-contract.md
set -u

V9="${1:-}"
V8="${2:-}"

if [[ -z "$V9" || ! -d "$V9" ]]; then
  echo "usage: $0 <v9-project-dir> [v8-project-dir]" >&2
  exit 2
fi

PASS=0; FAIL=0; WARN=0; SKIP=0
pass() { PASS=$((PASS+1)); echo "PASS  $1"; }
fail() { FAIL=$((FAIL+1)); echo "FAIL  $1"; }
warn() { WARN=$((WARN+1)); echo "WARN  $1"; }
skip() { SKIP=$((SKIP+1)); echo "SKIP  $1"; }

# Collect matching files, excluding build output.
# Convention: find predicates first, start dir LAST.
find_files() {
  local args=("$@") dir="${!#}"
  unset 'args[${#args[@]}-1]'
  find "$dir" -type f -not -path '*/target/*' -not -path '*/.git/*' "${args[@]}"
}

# Populate array $2 with results of find_files (bash 3.2 compatible — no mapfile).
collect_files() { # $1 = array name; rest = find_files args
  local arr_name="$1"; shift
  eval "$arr_name=()"
  local f
  while IFS= read -r f; do
    eval "$arr_name+=(\"\$f\")"
  done < <(find_files "$@")
}

echo "== Validating v9 project: $V9"
[[ -n "$V8" ]] && echo "== v8 source (for conditional checks): $V8"
echo

POM="$V9/pom.xml"
PROPS="$V9/src/main/resources/application.properties"

###########
# Required files
###########

if [[ -f "$POM" ]]; then
  pass "pom.xml exists"
else
  fail "pom.xml missing"
fi

if [[ -f "$PROPS" ]]; then
  pass "src/main/resources/application.properties exists"
else
  fail "src/main/resources/application.properties missing"
fi

if [[ -f "$V9/migration-status.md" ]]; then
  pass "migration-status.md exists"
else
  fail "migration-status.md missing"
fi

###########
# POM structure
###########

if [[ -f "$POM" ]]; then
  if grep -q '<packaging>kjar</packaging>' "$POM"; then
    fail "pom.xml still uses kjar packaging"
  else
    pass "pom.xml packaging is not kjar"
  fi

  boms=$(grep -oE '<artifactId>bamoe-(quarkus|spring-boot|embedded)-bom</artifactId>' "$POM" | wc -l | tr -d ' ')
  if [[ "$boms" -eq 1 ]]; then
    pass "pom.xml imports exactly one com.ibm.bamoe BOM"
  elif [[ "$boms" -eq 0 ]]; then
    if grep -q '<artifactId>bamoe-bom</artifactId>' "$POM"; then
      warn "pom.xml imports legacy 'bamoe-bom' — 9.5.x docs specify bamoe-quarkus-bom / bamoe-spring-boot-bom / bamoe-embedded-bom (reference-guide/maven-repository-libraries.adoc)"
    else
      fail "pom.xml imports no com.ibm.bamoe BOM (expected bamoe-quarkus-bom, bamoe-spring-boot-bom, or bamoe-embedded-bom)"
    fi
  else
    fail "pom.xml imports $boms BAMOE BOMs — exactly one must match the target framework"
  fi

  if grep -q 'kie-maven-plugin' "$POM"; then
    fail "pom.xml still references kie-maven-plugin"
  else
    pass "no kie-maven-plugin in pom.xml"
  fi

  if grep -qE 'org\.kie\.server|rhpam|redhat\.ba' "$POM"; then
    fail "pom.xml references KIE Server / RHPAM artifacts"
  else
    pass "no KIE Server / RHPAM artifacts in pom.xml"
  fi

  if grep -qE 'quarkus-maven-plugin|kogito-maven-plugin' "$POM"; then
    pass "codegen build plugin present (quarkus-maven-plugin or kogito-maven-plugin)"
  else
    warn "no quarkus-maven-plugin / kogito-maven-plugin found — verify Kogito code generation is wired"
  fi
fi

###########
# application.properties
###########

if [[ -f "$PROPS" ]]; then
  bad_props=$(grep -nE '^\s*(%[a-z]+\.)?(kieserver|drools|jbpm)\.' "$PROPS" || true)
  if [[ -n "$bad_props" ]]; then
    fail "application.properties contains deprecated v8 property namespaces:"$'\n'"$bad_props"
  else
    pass "no kieserver.* / drools.* / jbpm.* keys in application.properties"
  fi
fi

###########
# Forbidden v8 files
###########

forbidden_names=(
  kmodule.xml kie-deployment-descriptor.xml persistence.xml
  project.repositories project.imports package-names-white-list
  patterns.json themes.json workitem.conf
)
found_forbidden=""
for n in "${forbidden_names[@]}"; do
  m=$(find "$V9" -type f -name "$n" -not -path '*/target/*' | head -5)
  [[ -n "$m" ]] && found_forbidden+="$m"$'\n'
done
# extension-based forbidden types
m=$(find_files -name '*.frm' -o -name '*.gdst' -o -name '*.rdrl' -o -name '*.dsl' -o -name '*.dslr' -o -name '*.pmml' "$V9" | head -10)
[[ -n "$m" ]] && found_forbidden+="$m"$'\n'
# global/ directory
if find "$V9" -type d -name global -not -path '*/target/*' | grep -q .; then
  found_forbidden+="$(find "$V9" -type d -name global -not -path '*/target/*' | head -5)"$'\n'
fi
if [[ -n "$found_forbidden" ]]; then
  fail "forbidden v8 files/dirs still present:"$'\n'"$found_forbidden"
else
  pass "no forbidden v8 files (kmodule.xml, deployment descriptors, .frm, guided rules, DSL, PMML, etc.)"
fi

###########
# Java code checks
###########

if find_files -name '*.java' "$V9" | grep -q .; then
  if grep -rln --include='*.java' 'javax\.' "$V9/src" 2>/dev/null | grep -q .; then
    fail "javax.* imports remain:"$'\n'"$(grep -rln --include='*.java' 'javax\.' "$V9/src" | head -10)"
  else
    pass "no javax.* imports (jakarta.* only)"
  fi

  if grep -rln --include='*.java' -E 'implements +WorkItemHandler' "$V9/src" | grep -q .; then
    fail "implements WorkItemHandler remains (must extend DefaultKogitoWorkItemHandler):"$'\n'"$(grep -rln --include='*.java' -E 'implements +WorkItemHandler' "$V9/src")"
  else
    pass "no 'implements WorkItemHandler'"
  fi

  if grep -rln --include='*.java' -E 'executeWorkItem\(|abortWorkItem\(' "$V9/src" | grep -q .; then
    fail "v8 WIH lifecycle methods remain (executeWorkItem/abortWorkItem):"$'\n'"$(grep -rln --include='*.java' -E 'executeWorkItem\(|abortWorkItem\(' "$V9/src")"
  else
    pass "no executeWorkItem/abortWorkItem methods"
  fi

  if grep -rln --include='*.java' '@Wid' "$V9/src" | grep -q .; then
    fail "@Wid annotations remain (annotation unsupported in v9):"$'\n'"$(grep -rln --include='*.java' '@Wid' "$V9/src")"
  else
    pass "no @Wid annotations"
  fi

  if grep -rln --include='*.java' 'UserGroupCallback' "$V9/src" | grep -q .; then
    warn "UserGroupCallback references remain — v9 uses IdentityProvider/OIDC:"$'\n'"$(grep -rln --include='*.java' 'UserGroupCallback' "$V9/src")"
  fi

  if grep -rln --include='*.java' 'TaskLifeCycleEventListener' "$V9/src" | grep -q .; then
    warn "TaskLifeCycleEventListener remains — v9 uses UserTaskEventListener.onUserTaskState:"$'\n'"$(grep -rln --include='*.java' 'TaskLifeCycleEventListener' "$V9/src")"
  fi
else
  skip "no .java sources — Java checks skipped (dummy classes are NOT required; Kogito codegen produces runtime classes)"
fi

###########
# BPMN checks
###########

collect_files bpmn_files -name '*.bpmn' "$V9"
if [[ ${#bpmn_files[@]} -gt 0 ]]; then
  # JavaScript dialect
  js=$(grep -l 'dialect="javascript"' "${bpmn_files[@]}" 2>/dev/null || true)
  if [[ -n "$js" ]]; then
    fail "Script Tasks using JavaScript dialect (must be Java):"$'\n'"$js"
  else
    pass "no JavaScript Script Task dialect"
  fi

  # DROOLS / mvel expression languages on sequence flows
  drools_expr=$(grep -lE 'language="[^"]*(drools|mvel)[^"]*"' "${bpmn_files[@]}" 2>/dev/null || true)
  if [[ -n "$drools_expr" ]]; then
    fail "gateway/sequence-flow expressions using DROOLS/MVEL dialect (must be Java):"$'\n'"$drools_expr"
  else
    pass "no DROOLS/MVEL expression dialects in BPMN"
  fi

  # Process IDs must be camelCase-compatible (no hyphens or dots)
  bad_ids=$(grep -hoE 'bpmn2?:process[^>]* id="[^"]*[-.][^"]*"' "${bpmn_files[@]}" 2>/dev/null || true)
  if [[ -n "$bad_ids" ]]; then
    fail "process IDs contain hyphens/dots (break v9 code generation):"$'\n'"$bad_ids"
  else
    pass "all BPMN process IDs are hyphen/dot free"
  fi
else
  skip "no .bpmn files in v9 output"
fi

# Shared KIE-session pattern — heuristic WARN only (intent can't be proven mechanically)
if [[ ${#bpmn_files[@]} -gt 0 ]] && find_files -name '*.drl' "$V9" | grep -q .; then
  if grep -lE '\b(insert|retract|update)\s*\(' $(find_files -name '*.drl' "$V9") 2>/dev/null | grep -q .; then
    warn "DRL files contain insert()/retract()/update() — verify no shared KIE-session dependency with BPMN (v9 requires explicit Input/Output data mapping)"
  fi
fi

###########
# Conditional checks (triggered by what's actually in the output)
###########

# .wid → handler config bean + handler base class
collect_files wid_files -name '*.wid' "$V9"
if [[ ${#wid_files[@]} -gt 0 ]]; then
  if grep -rln 'DefaultWorkItemHandlerConfig' "$V9/src" 2>/dev/null | grep -q .; then
    pass ".wid files present and a DefaultWorkItemHandlerConfig registration class exists"
  else
    fail ".wid files present but no DefaultWorkItemHandlerConfig registration class found in src/"
  fi
  if grep -rln 'DefaultKogitoWorkItemHandler' "$V9/src" 2>/dev/null | grep -q .; then
    pass "handler classes extend DefaultKogitoWorkItemHandler"
  else
    fail ".wid files present but no class extends DefaultKogitoWorkItemHandler"
  fi
fi

# .scesim → activator + dependency
collect_files scesim_files -name '*.scesim' "$V9"
if [[ ${#scesim_files[@]} -gt 0 ]]; then
  misplaced=$(printf '%s\n' "${scesim_files[@]}" | grep -v 'src/test/resources/' || true)
  [[ -n "$misplaced" ]] && warn ".scesim files outside src/test/resources:"$'\n'"$misplaced"
  if grep -rln '@TestScenarioActivator' "$V9/src/test" 2>/dev/null | grep -q .; then
    pass ".scesim present and @TestScenarioActivator activator exists"
  else
    fail ".scesim present but no @TestScenarioActivator class in src/test"
  fi
  if [[ -f "$POM" ]] && grep -q 'kogito-scenario-simulation' "$POM"; then
    pass "kogito-scenario-simulation dependency present"
  else
    fail ".scesim present but kogito-scenario-simulation missing from pom.xml"
  fi
fi

# XLS/XLSX decision tables → drools-decisiontables
if find_files \( -name '*.xls' -o -name '*.xlsx' \) "$V9" | grep -q .; then
  if [[ -f "$POM" ]] && grep -q 'drools-decisiontables' "$POM"; then
    pass "XLS/XLSX decision tables present and drools-decisiontables dependency declared"
  else
    fail "XLS/XLSX decision tables present but drools-decisiontables missing from pom.xml"
  fi
fi

# JDBC persistence → datasource keys + new-DB reminder
if [[ -f "$PROPS" ]] && grep -q 'kogito.persistence.type=jdbc' "$PROPS"; then
  if grep -qE 'datasource' "$PROPS"; then
    pass "jdbc persistence configured with datasource keys"
  else
    fail "kogito.persistence.type=jdbc but no datasource configuration found"
  fi
  warn "persistence enabled — confirm a NEW database is used; v8 DB schemas are incompatible (upgrade/07-live-data-considerations.adoc)"
fi

# Security signal
if [[ -f "$PROPS" ]]; then
  if grep -q 'quarkus.oidc' "$PROPS" || grep -q 'spring.security.oauth2' "$PROPS"; then
    pass "OIDC configuration present in application.properties"
  elif grep -qE 'kogito\.(security\.)?auth\.enabled=false' "$PROPS"; then
    pass "non-secured dev mode configured (kogito auth disabled) — confirm prod OIDC is a recorded follow-up"
  else
    warn "no OIDC or explicit non-secured-mode keys found — security approach unclear; record intent in migration-status.md"
  fi
fi

###########
# v8 ↔ v9 asset comparison (only when v8 source given)
###########

if [[ -n "$V8" && -d "$V8" ]]; then
  for ext in bpmn dmn drl wid scesim; do
    c8=$(find "$V8" -type f -name "*.$ext" -not -path '*/target/*' | wc -l | tr -d ' ')
    c9=$(find "$V9" -type f -name "*.$ext" -not -path '*/target/*' | wc -l | tr -d ' ')
    if [[ "$c8" -eq 0 && "$c9" -eq 0 ]]; then
      :
    elif [[ "$c9" -eq "$c8" ]]; then
      pass "asset count .$ext: v8=$c8 → v9=$c9"
    elif [[ "$c9" -gt 0 ]]; then
      warn "asset count .$ext: v8=$c8 → v9=$c9 (renames/splits/merges? verify manually)"
    else
      fail "v8 has $c8 .$ext file(s) but v9 has none — assets not migrated or conversion not recorded"
    fi
  done
fi

###########
# Summary
###########

echo
echo "== Summary: $PASS passed, $FAIL failed, $WARN warnings, $SKIP skipped"
echo "== Report-only: update migration-status.md manually (partial + known gaps for any FAIL/WARN)."
[[ $FAIL -gt 0 ]] && exit 1
exit 0
