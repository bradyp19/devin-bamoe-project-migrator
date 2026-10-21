"""Regression suite for the BAMOE scalability pilot harness (standard library only).

Run: python3 -m unittest discover -s pilots -p 'test_*.py'
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import generate_fixtures as gen  # noqa: E402

BUSINESS_KINDS = ("bpmn", "dmn", "drl")


def _tmp(testcase, name="run"):
    d = Path(tempfile.mkdtemp(prefix="pilot-test-"))
    testcase.addCleanup(shutil.rmtree, d, ignore_errors=True)
    return d / name


class GeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tiers = gen.load_tiers()
        cls.base = Path(tempfile.mkdtemp(prefix="pilot-gen-"))
        cls.small_a = gen.generate("small", cls.base / "a")
        cls.small_b = gen.generate("small", cls.base / "b")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.base, ignore_errors=True)

    def test_tier_definitions_match_plan(self):
        expected = {
            "small": {"bpmn": 15, "dmn": 5, "drl": 10},
            "medium": {"bpmn": 150, "dmn": 50, "drl": 100},
            "large": {"bpmn": 750, "dmn": 250, "drl": 500},
        }
        for tier, counts in expected.items():
            self.assertEqual(self.tiers["tiers"][tier]["business"], counts)
        self.assertIsInstance(self.tiers["seed"], int)

    def test_generation_is_deterministic(self):
        a, b = self.small_a, self.small_b
        self.assertEqual(a["manifest_sha256"], b["manifest_sha256"])
        self.assertEqual(
            [(x["path"], x["sha256"]) for x in a["assets"]],
            [(x["path"], x["sha256"]) for x in b["assets"]],
        )

    def test_exact_business_counts_all_tiers(self):
        for tier in ("small", "medium", "large"):
            with self.subTest(tier=tier):
                if tier == "small":
                    m = self.small_a
                    root = self.base / "a"
                else:
                    root = self.base / tier
                    m = gen.generate(tier, root)
                want = self.tiers["tiers"][tier]["business"]
                self.assertEqual(m["summary"]["business"], want)
                project = root / "v8-projects" / f"v8-bank-{tier}"
                for kind in BUSINESS_KINDS:
                    on_disk = len(list(project.rglob(f"*.{kind}")))
                    self.assertEqual(on_disk, want[kind], kind)

    def test_summary_reports_support_and_size_separately(self):
        s = self.small_a["summary"]
        for key in ("business", "support", "total_files", "total_bytes",
                    "process_nodes", "dependency_edges", "exceptions", "max_call_chain_depth"):
            self.assertIn(key, s)
        self.assertGreater(s["process_nodes"], 0)
        self.assertGreater(s["dependency_edges"], 0)
        self.assertEqual(s["total_files"], len(self.small_a["assets"]))
        self.assertEqual(s["total_bytes"], sum(a["bytes"] for a in self.small_a["assets"]))
        for k in ("java_model", "java_handler", "java_listener", "java_security", "wid", "form", "config"):
            self.assertIn(k, s["support"])
            self.assertGreater(s["support"][k], 0, k)

    def test_archetype_mix_comparable_across_tiers(self):
        def mix(m):
            out = {}
            for a in m["assets"]:
                if a["business"]:
                    key = (a["kind"], a["scenario"]["archetype"])
                    out[key] = out.get(key, 0) + 1
            return out
        small = mix(self.small_a)
        medium = mix(gen.generate("medium", self.base / "mix-medium"))
        self.assertEqual(set(small), set(medium))
        for key, n in small.items():
            self.assertEqual(medium[key], n * 10, key)
        archetypes = {k[1] for k in small if k[0] == "bpmn"}
        for required in ("human-task", "gateway", "subprocess", "script",
                         "rule-task", "decision-task", "service-handler"):
            self.assertIn(required, archetypes)

    def test_exception_cases_identifiable_and_scaled(self):
        exc = [a for a in self.small_a["assets"] if a["scenario"].get("exception")]
        names = {a["scenario"]["exception"] for a in exc}
        for required in ("javascript-script", "dotted-hyphenated-process-id",
                         "drools-gateway-dialect", "shared-session-insert"):
            self.assertIn(required, names)
        for a in exc:
            self.assertNotEqual(a["expected_disposition"], "migrate", a["path"])
        self.assertEqual(self.small_a["summary"]["exceptions"], len(exc))

    def test_every_dependency_resolves_to_a_manifest_identity(self):
        for m in (self.small_a,):
            ids = {a["identity"] for a in m["assets"]}
            for a in m["assets"]:
                for dep in a["dependencies"]:
                    self.assertIn(dep, ids, f"{a['identity']} -> {dep}")

    def test_identities_are_unique(self):
        ids = [a["identity"] for a in self.small_a["assets"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_call_chains_are_bounded(self):
        limit = self.tiers["max_call_chain_depth"]
        self.assertLessEqual(self.small_a["summary"]["max_call_chain_depth"], limit)
        self.assertGreaterEqual(self.small_a["summary"]["max_call_chain_depth"], 2)

    def test_all_xml_parses(self):
        project = self.base / "a" / "v8-projects" / "v8-bank-small"
        for p in project.rglob("*"):
            if p.suffix in (".bpmn", ".dmn", ".xml"):
                ET.parse(p)

    def test_manifest_records_required_fields(self):
        for a in self.small_a["assets"]:
            for f in ("path", "kind", "identity", "sha256", "bytes", "scenario",
                      "dependencies", "expected_disposition", "business"):
                self.assertIn(f, a)

    def test_written_manifest_and_preflight(self):
        root = self.base / "a"
        on_disk = json.loads((root / "source-manifest.json").read_text())
        self.assertEqual(on_disk["manifest_sha256"], self.small_a["manifest_sha256"])
        pre = json.loads((root / "preflight.json").read_text())
        self.assertEqual(pre["status"], "pass", pre)
        self.assertEqual(pre["manifest_sha256"], self.small_a["manifest_sha256"])
        self.assertEqual(pre["summary"]["total_bytes"], self.small_a["summary"]["total_bytes"])

    def test_verify_manifest_clean(self):
        root = self.base / "a"
        self.assertEqual(gen.verify_manifest(root / "source-manifest.json"), [])

    def test_refuses_to_overwrite_existing_inputs(self):
        with self.assertRaises(FileExistsError):
            gen.generate("small", self.base / "a")

    def test_no_reserved_or_ignored_names(self):
        for a in self.small_a["assets"]:
            parts = Path(a["path"]).parts
            self.assertFalse({"status", "auth", "target", "index.html"} & set(parts), a["path"])


class ManifestTamperTests(unittest.TestCase):
    def setUp(self):
        self.root = _tmp(self)
        self.manifest = gen.generate("small", self.root)
        self.project = self.root / "v8-projects" / "v8-bank-small"
        self.mpath = self.root / "source-manifest.json"

    def test_detects_modified_byte(self):
        a = next(x for x in self.manifest["assets"] if x["kind"] == "dmn")
        p = self.project / a["path"]
        p.write_bytes(p.read_bytes() + b" ")
        problems = gen.verify_manifest(self.mpath)
        self.assertTrue(any(a["path"] in x and "sha256" in x for x in problems), problems)

    def test_detects_missing_and_extra_files(self):
        a = next(x for x in self.manifest["assets"] if x["kind"] == "drl")
        (self.project / a["path"]).unlink()
        (self.project / "src" / "main" / "resources" / "Extra.drl").write_text("package x;\n")
        problems = gen.verify_manifest(self.mpath)
        self.assertTrue(any("missing" in x and a["path"] in x for x in problems), problems)
        self.assertTrue(any("unexpected" in x and "Extra.drl" in x for x in problems), problems)

    def test_detects_same_count_substitution(self):
        bpmns = [x for x in self.manifest["assets"] if x["kind"] == "bpmn"]
        victim, donor = bpmns[0], bpmns[1]
        before = len(list(self.project.rglob("*.bpmn")))
        (self.project / victim["path"]).write_bytes((self.project / donor["path"]).read_bytes())
        self.assertEqual(before, len(list(self.project.rglob("*.bpmn"))))
        problems = gen.verify_manifest(self.mpath)
        self.assertTrue(any(victim["path"] in x for x in problems), problems)

    def test_tampered_manifest_body_detected(self):
        data = json.loads(self.mpath.read_text())
        data["assets"][0]["expected_disposition"] = "tampered"
        self.mpath.write_text(json.dumps(data))
        problems = gen.verify_manifest(self.mpath)
        self.assertTrue(any("manifest_sha256" in x for x in problems), problems)


class CliPathTests(unittest.TestCase):
    def test_cli_handles_paths_with_spaces(self):
        root = _tmp(self, "run dir with spaces")
        r = subprocess.run(
            [sys.executable, str(HERE / "generate_fixtures.py"), "--tier", "small",
             "--run-dir", str(root)],
            capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((root / "v8-projects" / "v8-bank-small" / "pom.xml").is_file())
        r2 = subprocess.run(
            [sys.executable, str(HERE / "generate_fixtures.py"), "--verify",
             str(root / "source-manifest.json")],
            capture_output=True, text=True)
        self.assertEqual(r2.returncode, 0, r2.stdout + r2.stderr)



import check_coverage as cov  # noqa: E402


def _faithful_v9(run_root, v9):
    """Build a mechanically faithful v9 tree from generated inputs (test fixture only)."""
    m = json.loads((run_root / "source-manifest.json").read_text())
    v8 = run_root / m["project_dir"]
    mappings, manual = {}, []
    for a in m["assets"]:
        if a["kind"] == "bpmn" and a["scenario"].get("exception") == "dotted-hyphenated-process-id":
            old = a["details"]["process_id"]
            tail = old.rsplit(".", 1)[-1]
            mappings[old] = "".join(w if i == 0 else w.capitalize() for i, w in enumerate(tail.split("-")))
    for a in m["assets"]:
        disp = a["expected_disposition"]
        if disp in ("migrate", "migrate-with-update"):
            text = (v8 / a["path"]).read_text()
            for old, new in mappings.items():
                text = text.replace(f'"{old}"', f'"{new}"')
            dest = v9 / a["path"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(text)
        elif disp in ("replace", "regenerate"):
            manual.append({"identity": a["identity"], "disposition": disp,
                           "reason": "tooling unavailable in convert-only test",
                           "reference": "migration-status.md#manual-follow-ups--known-gaps"})
    disp_path = run_root / "dispositions.json"
    disp_path.write_text(json.dumps({"process_id_mappings": mappings, "manual": manual}, indent=2))
    return m, disp_path


class CoverageTests(unittest.TestCase):
    def setUp(self):
        self.root = _tmp(self, "cov run")
        self.manifest = gen.generate("small", self.root)
        self.v9 = self.root / "v9-projects" / "v9-bank-small"
        _, self.disp = _faithful_v9(self.root, self.v9)
        self.mpath = self.root / "source-manifest.json"

    def report(self):
        return cov.reconcile(self.mpath, self.v9, self.disp)

    def asset(self, kind, pred=lambda a: True):
        return next(a for a in self.manifest["assets"] if a["kind"] == kind and pred(a))

    def test_source_references_resolve(self):
        idx = cov.index_project(self.root / "v8-projects" / "v8-bank-small")
        self.assertEqual(idx["parse_errors"], [])
        self.assertEqual(cov.check_references(idx), [])
        self.assertEqual(len(idx["processes"]), 15)
        self.assertEqual(len(idx["dmns"]), 5)

    def test_preflight_includes_reference_check(self):
        pre = json.loads((self.root / "preflight.json").read_text())
        self.assertEqual(pre["checks"]["broken_source_references"], [])
        self.assertEqual(pre["checks"]["indexed_counts"]["bpmn"], 15)

    def test_faithful_output_passes(self):
        r = self.report()
        self.assertEqual(r["status"], "pass", json.dumps(r["problems"], indent=1))
        c = r["counts"]
        self.assertEqual(c["missing"], 0)
        self.assertEqual(c["violation"], 0)
        self.assertGreater(c["manual"], 0)
        self.assertFalse(r["complete_conversion"])
        self.assertEqual(c["converted"] + c["manual"] + c["removed"], len(self.manifest["assets"]))

    def test_every_asset_has_traceable_status(self):
        r = self.report()
        self.assertEqual({x["identity"] for x in r["assets"]},
                         {a["identity"] for a in self.manifest["assets"]})
        for x in r["assets"]:
            self.assertIn(x["status"], ("converted", "manual", "removed", "missing", "violation"))

    def test_missing_asset_detected(self):
        a = self.asset("drl")
        (self.v9 / a["path"]).unlink()
        r = self.report()
        self.assertEqual(r["status"], "fail")
        self.assertIn(a["identity"], [x["identity"] for x in r["assets"] if x["status"] == "missing"])

    def test_same_count_substitution_in_output_detected(self):
        dmns = [a for a in self.manifest["assets"] if a["kind"] == "dmn"]
        victim, donor = dmns[0], dmns[1]
        (self.v9 / victim["path"]).write_bytes((self.v9 / donor["path"]).read_bytes())
        self.assertEqual(len(list(self.v9.rglob("*.dmn"))), len(dmns))
        r = self.report()
        self.assertEqual(r["status"], "fail")
        self.assertIn(victim["identity"], [x["identity"] for x in r["assets"] if x["status"] == "missing"])

    def test_partial_rule_loss_detected(self):
        a = self.asset("drl")
        p = self.v9 / a["path"]
        name = a["details"]["rule_names"][1]
        p.write_text(p.read_text().replace(f'rule "{name}"', 'rule "Something Else"'))
        r = self.report()
        self.assertIn(a["identity"], [x["identity"] for x in r["assets"] if x["status"] == "missing"])

    def test_removed_file_left_behind_is_violation(self):
        dest = self.v9 / "src" / "main" / "resources" / "META-INF" / "kmodule.xml"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text("<kmodule/>")
        r = self.report()
        self.assertEqual(r["status"], "fail")
        self.assertTrue(any(x["status"] == "violation" and x["identity"].endswith("kmodule.xml") for x in r["assets"]))

    def test_documentation_alone_is_not_conversion(self):
        a = self.asset("dmn")
        (self.v9 / a["path"]).unlink()
        d = json.loads(self.disp.read_text())
        d["manual"].append({"identity": a["identity"], "disposition": "migrate",
                            "reason": "documented only", "reference": "migration-status.md"})
        self.disp.write_text(json.dumps(d))
        r = self.report()
        st = next(x for x in r["assets"] if x["identity"] == a["identity"])
        self.assertEqual(st["status"], "manual")
        self.assertFalse(r["complete_conversion"])

    def test_manual_entry_requires_reason_and_reference(self):
        d = json.loads(self.disp.read_text())
        d["manual"][0]["reason"] = ""
        d["manual"].append({"identity": "bpmn:doesNotExist", "disposition": "x", "reason": "r", "reference": "r"})
        self.disp.write_text(json.dumps(d))
        r = self.report()
        self.assertEqual(r["status"], "fail")
        self.assertEqual(len(r["problems"]["invalid_dispositions"]), 2)

    def test_unmapped_rename_detected_as_missing_and_stale_reference(self):
        d = json.loads(self.disp.read_text())
        d["process_id_mappings"] = {}
        self.disp.write_text(json.dumps(d))
        r = self.report()
        self.assertEqual(r["status"], "fail")
        dotted = self.asset("bpmn", lambda a: a["scenario"].get("exception") == "dotted-hyphenated-process-id")
        self.assertIn(dotted["identity"], [x["identity"] for x in r["assets"] if x["status"] == "missing"])

    def test_broken_call_reference_detected(self):
        a = self.asset("bpmn", lambda a: a["scenario"]["archetype"] == "subprocess")
        p = self.v9 / a["path"]
        p.write_text(p.read_text().replace('calledElement="', 'calledElement="ghost', 1))
        r = self.report()
        self.assertEqual(r["status"], "fail")
        self.assertTrue(any("ghost" in b for b in r["problems"]["broken_references"]), r["problems"])

    def test_broken_rule_group_and_flow_detected(self):
        a = self.asset("bpmn", lambda a: a["scenario"]["archetype"] == "rule-task")
        p = self.v9 / a["path"]
        t = p.read_text().replace('drools:ruleFlowGroup="', 'drools:ruleFlowGroup="nope-', 1)
        t = t.replace('targetRef="End"', 'targetRef="Nowhere"', 1)
        p.write_text(t)
        broken = self.report()["problems"]["broken_references"]
        self.assertTrue(any("nope-" in b for b in broken), broken)
        self.assertTrue(any("Nowhere" in b for b in broken), broken)

    def test_malformed_xml_negative_control(self):
        a = self.asset("bpmn")
        p = self.v9 / a["path"]
        p.write_text(p.read_text()[:-40])
        r = self.report()
        self.assertEqual(r["status"], "fail")
        self.assertTrue(any(a["path"] in e for e in r["problems"]["parse_errors"]))

    def test_wrong_namespace_root_detected(self):
        a = self.asset("dmn")
        p = self.v9 / a["path"]
        p.write_text(re.sub(r'xmlns:dmn="[^"]+"', 'xmlns:dmn="urn:not-dmn"', p.read_text()))
        r = self.report()
        self.assertTrue(any(a["path"] in e for e in r["problems"]["parse_errors"]), r["problems"])

    def test_source_tamper_reported(self):
        a = self.asset("drl")
        p = self.root / "v8-projects" / "v8-bank-small" / a["path"]
        p.write_text(p.read_text() + "\n")
        r = self.report()
        self.assertEqual(r["status"], "fail")
        self.assertTrue(r["problems"]["source_integrity"])

    def test_target_dirs_ignored(self):
        junk = self.v9 / "target" / "classes" / "Broken.bpmn"
        junk.parent.mkdir(parents=True)
        junk.write_text("<not xml")
        self.assertEqual(self.report()["status"], "pass")

    def test_cli_writes_report_with_spaces(self):
        out = self.root / "evidence dir" / "coverage.json"
        out.parent.mkdir()
        args = [sys.executable, str(HERE / "check_coverage.py"), "--manifest", str(self.mpath),
                "--v9", str(self.v9), "--dispositions", str(self.disp), "--out", str(out)]
        r = subprocess.run(args, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(json.loads(out.read_text())["status"], "pass")
        (self.v9 / self.asset("dmn")["path"]).unlink()
        args[-1] = str(out.parent / "coverage-attempt-2.json")
        r = subprocess.run(args, capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        self.assertEqual(json.loads(Path(args[-1]).read_text())["status"], "fail")

    def test_cli_refuses_to_overwrite_report(self):
        out = self.root / "coverage.json"
        out.write_text("{}")
        r = subprocess.run([sys.executable, str(HERE / "check_coverage.py"), "--manifest", str(self.mpath),
                            "--v9", str(self.v9), "--out", str(out)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)
        self.assertEqual(out.read_text(), "{}")



import measure_run as mr  # noqa: E402


class FakeClock:
    def __init__(self, boot="boot-a"):
        self.utc = 1_800_000_000.0
        self.mono = 5_000_000_000
        self.boot = boot

    def advance(self, seconds, mono_seconds=None):
        self.utc += seconds
        self.mono += int((seconds if mono_seconds is None else mono_seconds) * 1e9)

    def __call__(self):
        return {"utc_epoch": self.utc, "monotonic_ns": self.mono, "boot_id": self.boot}


class MeasureTests(unittest.TestCase):
    def setUp(self):
        self.run = _tmp(self, "measure run")
        self.run.mkdir(parents=True)
        self.clock = FakeClock()

    def ev(self, kind, **kw):
        return mr.record(self.run, kind, clock=self.clock, **kw)

    def test_state_machine_rejects_invalid_transitions(self):
        with self.assertRaises(mr.StateError):
            self.ev("pause")
        self.ev("start", run_id="t-001")
        with self.assertRaises(mr.StateError):
            self.ev("start", run_id="t-001")
        with self.assertRaises(mr.StateError):
            self.ev("resume")
        self.ev("pause")
        with self.assertRaises(mr.StateError):
            self.ev("checkpoint", phase="x")
        with self.assertRaises(mr.StateError):
            self.ev("pause")
        self.ev("resume")
        self.ev("finish", outcome="partial")
        for kind in ("checkpoint", "pause", "resume", "finish"):
            with self.assertRaises(mr.StateError):
                self.ev(kind, phase="x", outcome="partial")
        events = mr.read_events(self.run)
        self.assertEqual([e["type"] for e in events], ["start", "pause", "resume", "finish"])
        self.assertEqual([e["seq"] for e in events], [1, 2, 3, 4])

    def test_active_and_paused_time(self):
        self.ev("start", run_id="t-001")
        self.clock.advance(10)
        self.ev("checkpoint", phase="sub-task-1")
        self.clock.advance(10)
        self.ev("pause", note="boundary after sub-task 1")
        self.clock.advance(60)
        self.ev("resume")
        self.clock.advance(20)
        self.ev("finish", outcome="partial")
        m = mr.compute_metrics(self.run)
        self.assertEqual(m["clock_continuity"], "continuous")
        self.assertAlmostEqual(m["active_seconds"], 40)
        self.assertAlmostEqual(m["paused_seconds"], 60)
        self.assertAlmostEqual(m["wall_seconds"], 100)
        self.assertEqual(m["pauses"], 1)
        self.assertEqual(m["checkpoints"][0]["phase"], "sub-task-1")
        self.assertAlmostEqual(m["checkpoints"][0]["active_elapsed_seconds"], 10)
        self.assertEqual(m["outcome"], "partial")

    def test_reboot_during_pause_not_subtracted(self):
        self.ev("start", run_id="t-001")
        self.clock.advance(30)
        self.ev("pause")
        self.clock.advance(600)
        self.clock.boot = "boot-b"
        self.clock.mono = 1_000
        self.ev("resume")
        self.clock.advance(15)
        self.ev("finish", outcome="complete")
        m = mr.compute_metrics(self.run)
        self.assertEqual(m["clock_continuity"], "discontinuous")
        self.assertAlmostEqual(m["active_seconds"], 45)
        self.assertIsNone(m["paused_seconds"])
        self.assertAlmostEqual(m["paused_seconds_wallclock"], 600)
        self.assertTrue(m["clock_notes"])

    def test_reboot_while_running_makes_active_unavailable(self):
        self.ev("start", run_id="t-001")
        self.clock.advance(30)
        self.clock.boot = "boot-b"
        self.clock.mono = 1_000
        self.ev("checkpoint", phase="after-reboot")
        self.clock.advance(5)
        self.ev("finish", outcome="blocked")
        m = mr.compute_metrics(self.run)
        self.assertIsNone(m["active_seconds"])
        self.assertAlmostEqual(m["active_seconds_wallclock"], 35)

    def test_unsupported_boot_id(self):
        self.clock.boot = None
        self.ev("start", run_id="t-001")
        self.clock.advance(5)
        self.ev("finish", outcome="complete")
        m = mr.compute_metrics(self.run)
        self.assertEqual(m["clock_continuity"], "unsupported")
        self.assertIsNone(m["active_seconds"])
        self.assertAlmostEqual(m["active_seconds_wallclock"], 5)

    def test_clock_divergence_flagged(self):
        self.ev("start", run_id="t-001")
        self.clock.advance(300, mono_seconds=10)
        self.ev("finish", outcome="complete")
        m = mr.compute_metrics(self.run)
        self.assertEqual(m["clock_continuity"], "divergent")
        self.assertAlmostEqual(m["active_seconds"], 10)
        self.assertAlmostEqual(m["active_seconds_wallclock"], 300)

    def test_errors_and_unavailable_metrics(self):
        self.ev("start", run_id="t-001")
        self.ev("error", message="DMN tooling unavailable", exit_code=3)
        self.ev("finish", outcome="partial")
        m = mr.compute_metrics(self.run)
        self.assertEqual(m["errors"][0]["message"], "DMN tooling unavailable")
        self.assertEqual(m["errors"][0]["exit_code"], 3)
        for k in ("tokens", "cost", "peak_memory", "model"):
            self.assertIsNone(m["unavailable"][k])

    def test_validation_attempts_retained(self):
        self.ev("start", run_id="t-001")
        a1 = mr.run_validation(self.run, "validator", [sys.executable, "-c", "import sys; print('bad'); sys.exit(1)"],
                               clock=self.clock)
        a2 = mr.run_validation(self.run, "validator", [sys.executable, "-c", "print('ok')"], clock=self.clock)
        self.assertEqual((a1["exit_code"], a2["exit_code"]), (1, 0))
        self.assertNotEqual(a1["stdout_path"], a2["stdout_path"])
        self.assertIn("bad", (self.run / a1["stdout_path"]).read_text())
        self.assertIn("ok", (self.run / a2["stdout_path"]).read_text())
        self.ev("finish", outcome="partial")
        m = mr.compute_metrics(self.run)
        self.assertEqual([v["exit_code"] for v in m["validation_attempts"]], [1, 0])

    def test_start_records_environment_and_inputs(self):
        gen.generate("small", self.run)
        e = self.ev("start", run_id="small-001", branch="pilot/x", base_revision="abc", harness_revision="def")
        self.assertEqual(e["run_id"], "small-001")
        self.assertEqual(e["inputs"]["seed"], gen.load_tiers()["seed"])
        self.assertEqual(e["inputs"]["business"]["bpmn"], 15)
        self.assertGreater(e["inputs"]["total_bytes"], 0)
        self.assertIn("python", e["environment"])
        self.assertEqual(e["branch"], "pilot/x")

    def test_cli_round_trip_with_spaces(self):
        def cli(*args):
            return subprocess.run([sys.executable, str(HERE / "measure_run.py"), *args, "--run-dir", str(self.run)],
                                  capture_output=True, text=True)
        self.assertEqual(cli("start", "--run-id", "cli-001").returncode, 0)
        self.assertEqual(cli("checkpoint", "--phase", "sub-task-1").returncode, 0)
        self.assertEqual(cli("resume").returncode, 2)
        r = subprocess.run([sys.executable, str(HERE / "measure_run.py"), "validate", "--run-dir", str(self.run),
                            "--label", "probe", "--", sys.executable, "-c", "print(42)"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(cli("finish", "--outcome", "partial").returncode, 0)
        m = json.loads((self.run / "metrics.json").read_text())
        self.assertEqual(m["run_id"], "cli-001")
        self.assertEqual(m["validation_attempts"][0]["exit_code"], 0)
        self.assertEqual(cli("finish", "--outcome", "partial").returncode, 2)


if __name__ == "__main__":
    unittest.main()
