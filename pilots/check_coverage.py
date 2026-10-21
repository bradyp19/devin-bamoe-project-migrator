#!/usr/bin/env python3
"""Independent source/output reconciliation for the BAMOE scalability pilot.

Matches every asset in source-manifest.json to a traceable v9 output by identity
(process id, DMN namespace+name, DRL package+rule names, Java FQCN, WID names,
generated form name) or to a documented manual disposition, and runs
namespace-aware XML parsing and generated-reference checks on the v9 tree.

This is mechanical reconciliation. It is NOT semantic validation and says nothing
about whether the output builds, runs, or behaves like the source.

Usage:
  check_coverage.py --manifest <run>/source-manifest.json --v9 <v9-dir>
                    [--dispositions <run>/dispositions.json] [--out <run>/coverage.json]
  check_coverage.py --references-only <project-dir>

dispositions.json (written by the migration session, optional):
  {"process_id_mappings": {"old.id-1": "newId1"},
   "identity_mappings":  {"java:old.Fqcn": "java:new.Fqcn"},
   "manual": [{"identity": "...", "disposition": "...", "reason": "...", "reference": "..."}]}
"""
import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_fixtures as gen  # noqa: E402

NS_BPMN = "http://www.omg.org/spec/BPMN/20100524/MODEL"
NS_BPMNDI = "http://www.omg.org/spec/BPMN/20100524/DI"
NS_DROOLS = "http://www.jboss.org/drools"
DMN_NAMESPACES = {
    "http://www.omg.org/spec/DMN/20151101/dmn.xsd",
    "http://www.omg.org/spec/DMN/20180521/MODEL/",
    "https://www.omg.org/spec/DMN/20191111/MODEL/",
    "https://www.omg.org/spec/DMN/20211108/MODEL/",
    "https://www.omg.org/spec/DMN/20230324/MODEL/",
}
SKIP_DIRS = {"target", ".git", "node_modules"}
FORBIDDEN_NAMES = {"kmodule.xml", "kie-deployment-descriptor.xml", "persistence.xml", "project.repositories",
                   "project.imports", "package-names-white-list", "workitem.conf"}
NON_NODE_TAGS = {"sequenceFlow", "property", "ioSpecification", "dataInput", "dataOutput", "inputSet",
                 "outputSet", "dataInputAssociation", "dataOutputAssociation", "assignment", "documentation",
                 "extensionElements", "laneSet", "lane", "textAnnotation", "association"}


def _local(tag):
    return tag.rsplit("}", 1)[-1]


def _ns(tag):
    return tag[1:].split("}", 1)[0] if tag.startswith("{") else ""


def _walk(project):
    project = Path(project)
    for p in sorted(project.rglob("*")):
        rel = p.relative_to(project)
        if p.is_file() and not (set(rel.parts[:-1]) & SKIP_DIRS):
            yield p, rel.as_posix()


def _index_bpmn(path, rel, idx):
    root = ET.parse(path).getroot()
    if root.tag != f"{{{NS_BPMN}}}definitions":
        raise ValueError(f"unexpected root {root.tag} (expected BPMN 2.0 definitions)")
    items = {}
    for it in root.iter(f"{{{NS_BPMN}}}itemDefinition"):
        items[it.get("id")] = it.get("structureRef")
    file_processes = []
    all_ids = set()
    for proc in root.iter(f"{{{NS_BPMN}}}process"):
        pid = proc.get("id")
        file_processes.append(pid)
        nodes, flows, calls, groups, dmn_refs, tasks = set(), [], [], [], [], []
        for el in proc.iter():
            if el is proc or el.get("id") is None:
                continue
            tag = _local(el.tag)
            all_ids.add(el.get("id"))
            if tag == "sequenceFlow":
                flows.append((el.get("id"), el.get("sourceRef"), el.get("targetRef")))
            elif _ns(el.tag) == NS_BPMN and tag not in NON_NODE_TAGS:
                nodes.add(el.get("id"))
            if tag == "callActivity":
                calls.append(el.get("calledElement"))
            if tag == "businessRuleTask":
                g = el.get(f"{{{NS_DROOLS}}}ruleFlowGroup")
                if g:
                    groups.append(g)
                names = {d.get("id"): d.get("name") for d in el.iter(f"{{{NS_BPMN}}}dataInput")}
                vals = {}
                for a in el.iter(f"{{{NS_BPMN}}}assignment"):
                    f, t = a.find(f"{{{NS_BPMN}}}from"), a.find(f"{{{NS_BPMN}}}to")
                    if f is not None and t is not None and (t.text or "").strip() in names:
                        vals[names[(t.text or "").strip()]] = (f.text or "").strip()
                if "namespace" in vals or "model" in vals:
                    dmn_refs.append((vals.get("namespace"), vals.get("model")))
            if tag == "task":
                tn = el.get(f"{{{NS_DROOLS}}}taskName")
                if tn:
                    tasks.append(tn)
        if pid in idx["processes"]:
            idx["parse_errors"].append(f"{rel}: duplicate process id {pid} (also in {idx['processes'][pid]['path']})")
        idx["processes"][pid] = {"path": rel, "nodes": nodes, "flows": flows, "calls": calls,
                                 "groups": groups, "dmn_refs": dmn_refs, "tasks": tasks,
                                 "types": sorted(v for v in items.values() if v)}
    plane_refs = []
    for el in root.iter():
        if _ns(el.tag) == NS_BPMNDI and el.get("bpmnElement") is not None:
            plane_refs.append((_local(el.tag), el.get("bpmnElement")))
    idx["bpmn_di"].append({"path": rel, "processes": file_processes, "ids": all_ids, "refs": plane_refs})


def _index_dmn(path, rel, idx):
    root = ET.parse(path).getroot()
    if _local(root.tag) != "definitions" or _ns(root.tag) not in DMN_NAMESPACES:
        raise ValueError(f"unexpected root {root.tag} (expected DMN definitions)")
    key = f"{root.get('namespace')}#{root.get('name')}"
    if key in idx["dmns"]:
        idx["parse_errors"].append(f"{rel}: duplicate DMN model {key}")
    idx["dmns"][key] = {"path": rel, "spec": _ns(root.tag)}


RE_PKG = re.compile(r"^\s*package\s+([\w.]+)\s*;?", re.M)
RE_IMPORT = re.compile(r"^\s*import\s+(?:static\s+)?([\w.]+)\s*;?", re.M)
RE_RULE = re.compile(r'^\s*rule\s+"([^"]+)"', re.M)
RE_GROUP = re.compile(r'(?:ruleflow-group|agenda-group)\s+"([^"]+)"')
RE_CLASS = re.compile(r"^\s*(?:public\s+)?(?:abstract\s+|final\s+)*(?:class|interface|enum|record)\s+(\w+)", re.M)
RE_WID_NAME = re.compile(r'"name"\s*:\s*"([^"]+)"')


def _index_drl(path, rel, idx):
    text = path.read_text(errors="replace")
    m = RE_PKG.search(text)
    pkg = m.group(1) if m else ""
    for r in RE_RULE.findall(text):
        idx["drl_rules"].setdefault(f"{pkg}|{r}", rel)
    idx["drl_groups"].update(RE_GROUP.findall(text))
    idx["drl_imports"].append((rel, RE_IMPORT.findall(text)))


def _index_java(path, rel, idx):
    text = path.read_text(errors="replace")
    m = RE_PKG.search(text)
    pkg = m.group(1) if m else ""
    c = RE_CLASS.search(text)
    if c:
        idx["java"][f"{pkg}.{c.group(1)}" if pkg else c.group(1)] = rel


def index_project(project):
    idx = {"files": set(), "by_kind": {}, "parse_errors": [], "processes": {}, "bpmn_di": [], "dmns": {},
           "drl_rules": {}, "drl_groups": set(), "drl_imports": [], "java": {}, "wid_names": set(),
           "generated_forms": set(), "basenames": {}}
    handlers = {".bpmn": ("bpmn", _index_bpmn), ".bpmn2": ("bpmn", _index_bpmn), ".dmn": ("dmn", _index_dmn),
                ".drl": ("drl", _index_drl), ".java": ("java", _index_java)}
    for p, rel in _walk(project):
        idx["files"].add(rel)
        idx["basenames"].setdefault(p.name, []).append(rel)
        kind, fn = handlers.get(p.suffix, (p.suffix.lstrip(".") or p.name, None))
        idx["by_kind"].setdefault(kind, []).append(rel)
        try:
            if fn:
                fn(p, rel, idx)
            elif p.suffix == ".wid":
                idx["wid_names"].update(RE_WID_NAME.findall(p.read_text(errors="replace")))
            elif p.suffix == ".xml":
                ET.parse(p)
        except (ET.ParseError, ValueError, UnicodeDecodeError) as e:
            idx["parse_errors"].append(f"{rel}: {e}")
        if "custom-forms-dev" in rel.split("/")[:-1]:
            idx["generated_forms"].add(p.stem)
    return idx


def check_references(idx):
    broken = []
    procs = idx["processes"]
    dmn_keys = set(idx["dmns"])
    java = idx["java"]
    prefixes = {".".join(f.split(".")[:2]) for f in java}
    for pid, p in sorted(procs.items()):
        where = f"{p['path']} [{pid}]"
        for fid, s, t in p["flows"]:
            for end, ref in (("sourceRef", s), ("targetRef", t)):
                if ref not in p["nodes"]:
                    broken.append(f"{where}: sequenceFlow {fid} {end}={ref} does not resolve to a flow node")
        for c in p["calls"]:
            if c not in procs:
                broken.append(f"{where}: callActivity calledElement={c} does not resolve to a process id")
        for g in p["groups"]:
            if g not in idx["drl_groups"]:
                broken.append(f"{where}: ruleFlowGroup={g} not declared by any DRL")
        for ns, model in p["dmn_refs"]:
            if f"{ns}#{model}" not in dmn_keys:
                broken.append(f"{where}: DMN reference {ns}#{model} does not resolve to a DMN model")
        for tn in p["tasks"]:
            if tn not in idx["wid_names"]:
                broken.append(f"{where}: custom task {tn} not defined in any .wid")
        for t in p["types"]:
            if "." in t and ".".join(t.split(".")[:2]) in prefixes and t not in java:
                broken.append(f"{where}: itemDefinition structureRef={t} does not resolve to a project class")
    for di in idx["bpmn_di"]:
        for tag, ref in di["refs"]:
            if tag == "BPMNPlane":
                if ref not in di["processes"]:
                    broken.append(f"{di['path']}: BPMNPlane bpmnElement={ref} does not match a process in the file")
            elif ref not in di["ids"]:
                broken.append(f"{di['path']}: {tag} bpmnElement={ref} does not resolve to an element in the file")
    for rel, imports in idx["drl_imports"]:
        for imp in imports:
            if ".".join(imp.split(".")[:2]) in prefixes and imp not in java:
                broken.append(f"{rel}: import {imp} does not resolve to a project class")
    return broken


def _load_dispositions(path, manifest_ids):
    if not path:
        return {}, {}, {}, []
    d = json.loads(Path(path).read_text())
    invalid = []
    manual = {}
    for i, e in enumerate(d.get("manual", [])):
        miss = [k for k in ("identity", "disposition", "reason", "reference") if not str(e.get(k, "")).strip()]
        if miss:
            invalid.append(f"manual[{i}] missing/empty {', '.join(miss)}")
        elif e["identity"] not in manifest_ids:
            invalid.append(f"manual[{i}] identity {e['identity']} is not in the source manifest")
        else:
            manual[e["identity"]] = e
    pmap = dict(d.get("process_id_mappings", {}))
    imap = dict(d.get("identity_mappings", {}))
    for k in list(pmap) + list(imap):
        key = k if k in imap else f"bpmn:{k}"
        if key not in manifest_ids:
            invalid.append(f"mapping source {k} is not in the source manifest")
    return pmap, imap, manual, invalid


def _target_present(target, idx, asset):
    kind, _, rest = target.partition(":")
    if kind == "bpmn":
        return rest in idx["processes"]
    if kind == "dmn":
        return rest in idx["dmns"]
    if kind == "java":
        return rest in idx["java"]
    if kind == "drl":
        pkg = rest.split("/", 1)[0]
        names = asset.get("details", {}).get("rule_names", [])
        return bool(names) and all(f"{pkg}|{n}" in idx["drl_rules"] for n in names)
    if kind == "wid":
        names = asset.get("details", {}).get("names", [])
        return bool(names) and set(names) <= idx["wid_names"]
    return False


def _match(asset, idx, pmap, imap):
    """Return (present, evidence) for an asset that should appear in the output."""
    ident = asset["identity"]
    kind = asset["kind"]
    target = imap.get(ident)
    if kind == "bpmn" and not target:
        pid = asset["details"]["process_id"]
        target = f"bpmn:{pmap.get(pid, pid)}"
    if kind == "form":
        pid, task = asset["details"]["process_id"], asset["details"]["task_name"]
        for cand in {pid, pmap.get(pid, pid)}:
            if f"{cand}_{task}" in idx["generated_forms"]:
                return True, f"custom-forms-dev/{cand}_{task}.*"
        return False, None
    if kind == "config":
        if ident == "config:pom.xml":
            return "pom.xml" in idx["files"], "pom.xml"
        return False, None
    target = target or ident
    if _target_present(target, idx, asset):
        return True, target
    return False, None


def reconcile(manifest_path, v9_dir, dispositions_path=None):
    manifest_path = Path(manifest_path)
    m = json.loads(manifest_path.read_text())
    ids = {a["identity"] for a in m["assets"]}
    integrity = gen.verify_manifest(manifest_path)
    pmap, imap, manual, invalid = _load_dispositions(dispositions_path, ids)
    v9_dir = Path(v9_dir)
    idx = index_project(v9_dir) if v9_dir.is_dir() else None
    results = []
    if idx is None:
        problems = {"source_integrity": integrity, "invalid_dispositions": invalid,
                    "parse_errors": [f"v9 directory not found: {v9_dir}"], "broken_references": []}
        idx = index_project(manifest_path.parent / "__absent__")
    else:
        problems = {"source_integrity": integrity, "invalid_dispositions": invalid,
                    "parse_errors": list(idx["parse_errors"]), "broken_references": check_references(idx)}
    matched_outputs = set()
    for a in m["assets"]:
        ident, disp = a["identity"], a["expected_disposition"]
        entry = {"identity": ident, "kind": a["kind"], "source_path": a["path"], "expected": disp}
        if disp == "remove":
            name = Path(a["path"]).name
            left = [r for r in idx["basenames"].get(name, []) if name in FORBIDDEN_NAMES or r == a["path"]]
            entry["status"] = "violation" if left else "removed"
            if left:
                entry["evidence"] = left
        else:
            present, evidence = _match(a, idx, pmap, imap)
            if present:
                entry["status"] = "converted"
                entry["evidence"] = evidence
                matched_outputs.add(evidence)
            elif ident in manual:
                entry["status"] = "manual"
                entry["evidence"] = {k: manual[ident][k] for k in ("disposition", "reason", "reference")}
            else:
                entry["status"] = "missing"
            if ident in manual and present:
                entry["manual_note"] = manual[ident]["reason"]
        results.append(entry)
    counts = {s: sum(1 for r in results if r["status"] == s)
              for s in ("converted", "manual", "removed", "missing", "violation")}
    untraced = sorted(f"bpmn:{p}" for p in idx["processes"] if f"bpmn:{p}" not in matched_outputs) + \
        sorted(f"dmn:{k}" for k in idx["dmns"] if f"dmn:{k}" not in matched_outputs)
    failed = any(problems.values()) or counts["missing"] or counts["violation"]
    return {
        "status": "fail" if failed else "pass",
        "complete_conversion": not failed and counts["manual"] == 0,
        "tier": m["tier"],
        "manifest_sha256": m["manifest_sha256"],
        "v9_dir": str(v9_dir),
        "counts": counts,
        "by_kind": _by_kind(results),
        "problems": problems,
        "untraced_v9_models": untraced,
        "assets": results,
        "disclaimer": ("Mechanical identity/reference reconciliation only. A pass does not establish semantic "
                       "equivalence, a successful build, working OIDC, database connectivity, or regenerated forms. "
                       "'manual' means documented, not converted."),
    }


def _by_kind(results):
    out = {}
    for r in results:
        k = out.setdefault(r["kind"], {})
        k[r["status"]] = k.get(r["status"], 0) + 1
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest")
    ap.add_argument("--v9")
    ap.add_argument("--dispositions")
    ap.add_argument("--out")
    ap.add_argument("--references-only", metavar="PROJECT")
    args = ap.parse_args(argv)
    if args.references_only:
        idx = index_project(args.references_only)
        problems = [f"PARSE {e}" for e in idx["parse_errors"]] + [f"REF   {b}" for b in check_references(idx)]
        print("\n".join(problems) if problems else "PASS  all references resolve")
        return 1 if problems else 0
    if not (args.manifest and args.v9):
        ap.error("--manifest and --v9 are required")
    if args.out and Path(args.out).exists():
        print(f"error: refusing to overwrite existing report {args.out}; use a new attempt-specific path",
              file=sys.stderr)
        return 2
    r = reconcile(args.manifest, args.v9, args.dispositions)
    text = json.dumps(r, indent=2, sort_keys=True) + "\n"
    if args.out:
        Path(args.out).write_text(text)
    print(f"== coverage {r['status'].upper()} (complete_conversion={r['complete_conversion']})")
    print("== counts: " + ", ".join(f"{k}={v}" for k, v in r["counts"].items()))
    for k, v in r["problems"].items():
        for item in v[:20]:
            print(f"FAIL  {k}: {item}")
        if len(v) > 20:
            print(f"FAIL  {k}: ... {len(v) - 20} more")
    for a in r["assets"]:
        if a["status"] in ("missing", "violation"):
            print(f"FAIL  {a['status']}: {a['identity']} ({a['source_path']})")
    print("== " + r["disclaimer"])
    return 0 if r["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
