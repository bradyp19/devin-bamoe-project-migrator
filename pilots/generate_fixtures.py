#!/usr/bin/env python3
"""Deterministic synthetic BAMOE v8 workload generator for the scalability pilot.

Writes <run-dir>/v8-projects/v8-bank-<tier>/, <run-dir>/source-manifest.json and
<run-dir>/preflight.json. Inputs are fictional banking scenarios; they are not
compiled and are not established as v8-runtime-valid.

Usage:
  generate_fixtures.py --tier small --run-dir <dir>
  generate_fixtures.py --verify <run-dir>/source-manifest.json
"""
import argparse
import hashlib
import json
import random
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

HERE = Path(__file__).resolve().parent
TIERS_PATH = HERE / "tiers.json"

NS_BPMN = "http://www.omg.org/spec/BPMN/20100524/MODEL"
NS_DMN12 = "http://www.omg.org/spec/DMN/20180521/MODEL/"
NS_DMN11 = "http://www.omg.org/spec/DMN/20151101/dmn.xsd"
SCRIPT_JAVA = "http://www.java.com/java"
SCRIPT_JS = "http://www.javascript.com/javascript"
LANG_DROOLS = "http://www.jboss.org/drools/rule"
IMPL_DMN = "http://www.jboss.org/drools/dmn"
IMPL_RULE = "http://www.jboss.org/drools/rule"

RES = "src/main/resources"
JAVA = "src/main/java"
BASE_PKG = "com.fictionalbank"

NOUNS = ["Applicant", "Account", "Payment", "Card", "Case", "Party"]
SERVICES = ["CreditBureauLookup", "SanctionsScreen", "LedgerPosting", "SmsNotify", "DocumentArchive"]
TASKS = ["ReviewApplication", "ApproveLimit", "VerifyIdentity", "ConfirmPayment", "AssessRisk"]
GROUPS = ["loan-officers", "card-ops", "kyc-analysts", "payments-desk", "risk-managers"]


def load_tiers(path=TIERS_PATH):
    return json.loads(Path(path).read_text())


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def _cap(s):
    return s[0].upper() + s[1:]


class _Builder:
    def __init__(self, tier, tiers):
        self.tier = tier
        self.cfg = tiers
        self.units = tiers["tiers"][tier]["units"]
        self.rng = random.Random(f"{tiers['seed']}:{tier}")
        self.domains = tiers["domains"]
        self.files = {}   # relpath -> bytes
        self.assets = []  # manifest entries without hash/bytes
        self.calls = {}   # process id -> callee process id
        self.process_nodes = 0

    # ---------------------------------------------------------------- helpers
    def add(self, path, text, kind, identity, scenario, deps, disposition, business, details=None):
        if path in self.files:
            raise ValueError(f"duplicate path {path}")
        self.files[path] = text.encode("utf-8")
        entry = {
            "path": path, "kind": kind, "identity": identity, "scenario": scenario,
            "dependencies": sorted(set(deps)), "expected_disposition": disposition,
            "business": business,
        }
        if details:
            entry["details"] = details
        self.assets.append(entry)

    def domain(self):
        return self.rng.choice(self.domains)

    # ---------------------------------------------------------------- plan
    def build(self):
        unit = self.cfg["unit"]
        arche = [a for a, w in unit["bpmn_archetypes"].items() for _ in range(w)]
        n_model = unit["support"]["java_model"]
        n_listener = unit["support"]["java_listener"]
        n_security = unit["support"]["java_security"]

        self.models = []
        for i in range(self.units * n_model):
            self.models.append(self._model(i + 1))
        self.handlers = []
        self.listeners = []
        self.securities = []
        wid_by_domain = {}

        for u in range(self.units):
            umodels = self.models[u * n_model:(u + 1) * n_model]
            # DRL first so rule tasks can reference them
            drls = [self._drl(u * unit["drl"] + j + 1, umodels, shared_session=(j == 0))
                    for j in range(unit["drl"])]
            dmns = [self._dmn(u * unit["dmn"] + j + 1, legacy=(j == unit["dmn"] - 1))
                    for j in range(unit["dmn"])]
            # process ids per archetype ordinal
            plan = []
            counters = {}
            for k, a in enumerate(arche):
                ordinal = counters.get(a, 0)
                counters[a] = ordinal + 1
                plan.append((u * len(arche) + k + 1, a, ordinal))
            ids = {}
            for g, a, o in plan:
                dom = self.domain()
                if a == "human-task" and o == 2:
                    pid = f"{BASE_PKG}.{dom}.manual-review-{g:04d}"
                else:
                    pid = f"{dom}{_cap(a.replace('-task', 'Task').replace('-handler', 'Handler').replace('-', ''))}{g:04d}"
                ids[(a, o)] = (pid, dom, g)
            for g, a, o in plan:
                pid, dom, g = ids[(a, o)]
                model = self.rng.choice(umodels)
                exc = None
                deps = [model["identity"]]
                if a == "script" and o == 0:
                    exc = "javascript-script"
                elif a == "gateway" and o == 0:
                    exc = "drools-gateway-dialect"
                elif a == "human-task" and o == 2:
                    exc = "dotted-hyphenated-process-id"
                extra = {}
                if a == "subprocess":
                    callee = ids[("subprocess", 1)][0] if o == 0 else ids[("human-task", 2)][0]
                    self.calls[pid] = callee
                    deps.append(f"bpmn:{callee}")
                    extra["callee"] = callee
                elif a == "rule-task":
                    drl = drls[o]
                    deps.append(drl["identity"])
                    extra["group"] = drl["group"]
                elif a == "decision-task":
                    dmn = dmns[o]
                    deps.append(dmn["identity"])
                    extra["dmn"] = dmn
                elif a == "service-handler":
                    h = self._handler(len(self.handlers) + 1, dom)
                    self.handlers.append(h)
                    wid_by_domain.setdefault(dom, []).append(h)
                    deps.append(f"wid:{BASE_PKG}.{dom}")
                    extra["handler"] = h
                elif a == "human-task":
                    extra["task"] = TASKS[g % len(TASKS)] + f"{g:04d}"
                    extra["group"] = GROUPS[g % len(GROUPS)]
                self._bpmn(pid, dom, g, a, exc, model, deps, extra)
            for j in range(n_listener):
                self.listeners.append(self._listener(u * n_listener + j + 1, task=(j % 2 == 1)))
            for j in range(n_security):
                self.securities.append(self._security(u * n_security + j + 1))
        for dom in sorted(wid_by_domain):
            self._wid(dom, wid_by_domain[dom])
        self._config()
        return self

    # ---------------------------------------------------------------- java
    def _model(self, n):
        dom = self.domain()
        noun = NOUNS[n % len(NOUNS)]
        cls = f"{_cap(dom)}{noun}{n:04d}"
        fqcn = f"{BASE_PKG}.model.{cls}"
        persistent = n % 3 == 0
        imports = ["import java.io.Serializable;"]
        ann = ""
        if persistent:
            imports += ["import javax.persistence.Entity;", "import javax.persistence.Id;"]
            ann = "@Entity\n"
        fields = [("String", "reference"), ("String", "status"), ("java.math.BigDecimal", "amount"),
                  ("Integer", "score"), ("Boolean", "validated")]
        body = []
        for t, f in fields:
            idann = "    @Id\n" if persistent and f == "reference" else ""
            body.append(f"{idann}    private {t} {f};")
        for t, f in fields:
            body.append(f"    public {t} get{_cap(f)}() {{ return {f}; }}")
            body.append(f"    public void set{_cap(f)}({t} {f}) {{ this.{f} = {f}; }}")
        text = (f"package {BASE_PKG}.model;\n\n" + "\n".join(imports) + "\n\n"
                f"/** Fictional {dom} domain object (synthetic pilot fixture). */\n"
                f"{ann}public class {cls} implements Serializable {{\n"
                f"    private static final long serialVersionUID = {n}L;\n\n" + "\n".join(body) + "\n}\n")
        ident = f"java:{fqcn}"
        disp = "migrate-with-update" if persistent else "migrate"
        self.add(f"{JAVA}/{fqcn.replace('.', '/')}.java", text, "java_model", ident,
                 {"archetype": "domain-model", "persistent": persistent}, [], disp, False,
                 {"fqcn": fqcn})
        return {"identity": ident, "fqcn": fqcn, "cls": cls, "persistent": persistent}

    def _handler(self, n, dom):
        name = f"{SERVICES[n % len(SERVICES)]}{n:04d}"
        cls = f"{name}WorkItemHandler"
        fqcn = f"{BASE_PKG}.handler.{cls}"
        wid_ann = ""
        wid_imp = ""
        if n % 2 == 1:
            wid_imp = "import org.jbpm.process.workitem.core.util.Wid;\n"
            wid_ann = f'@Wid(widfile = "WorkDefinitions.wid", name = "{name}", displayName = "{name}")\n'
        text = (f"package {BASE_PKG}.handler;\n\n"
                "import java.util.HashMap;\nimport java.util.Map;\n\n"
                "import org.kie.api.runtime.process.WorkItem;\n"
                "import org.kie.api.runtime.process.WorkItemHandler;\n"
                "import org.kie.api.runtime.process.WorkItemManager;\n" + wid_imp + "\n"
                f"/** Fictional {dom} integration stub (synthetic pilot fixture; no external system). */\n"
                f"{wid_ann}public class {cls} implements WorkItemHandler {{\n\n"
                "    @Override\n"
                "    public void executeWorkItem(WorkItem workItem, WorkItemManager manager) {\n"
                '        Object reference = workItem.getParameter("Reference");\n'
                "        Map<String, Object> results = new HashMap<>();\n"
                f'        results.put("Result", "{name}:" + reference);\n'
                "        manager.completeWorkItem(workItem.getId(), results);\n"
                "    }\n\n"
                "    @Override\n"
                "    public void abortWorkItem(WorkItem workItem, WorkItemManager manager) {\n"
                "        manager.abortWorkItem(workItem.getId());\n"
                "    }\n}\n")
        ident = f"java:{fqcn}"
        self.add(f"{JAVA}/{fqcn.replace('.', '/')}.java", text, "java_handler", ident,
                 {"archetype": "work-item-handler", "wid_annotation": bool(wid_ann)},
                 [f"wid:{BASE_PKG}.{dom}"], "migrate-with-update", False, {"fqcn": fqcn, "wid_name": name})
        return {"identity": ident, "fqcn": fqcn, "name": name, "domain": dom}

    def _listener(self, n, task):
        if task:
            cls = f"TaskAuditListener{n:04d}"
            body = ("import org.kie.api.task.TaskEvent;\n"
                    "import org.kie.api.task.TaskLifeCycleEventListener;\n\n"
                    f"public class {cls} implements TaskLifeCycleEventListener {{\n" +
                    "".join(f"    @Override public void {p}{e}(TaskEvent event) {{ }}\n"
                            for e in ("TaskActivatedEvent", "TaskClaimedEvent", "TaskCompletedEvent",
                                      "TaskStartedEvent")
                            for p in ("before", "after")) + "}\n")
            arche = "task-lifecycle-listener"
        else:
            cls = f"ProcessAuditListener{n:04d}"
            body = ("import org.kie.api.event.process.DefaultProcessEventListener;\n"
                    "import org.kie.api.event.process.ProcessCompletedEvent;\n"
                    "import org.kie.api.event.process.ProcessStartedEvent;\n\n"
                    f"public class {cls} extends DefaultProcessEventListener {{\n"
                    "    @Override public void afterProcessStarted(ProcessStartedEvent event) { }\n"
                    "    @Override public void afterProcessCompleted(ProcessCompletedEvent event) { }\n}\n")
            arche = "process-event-listener"
        fqcn = f"{BASE_PKG}.listener.{cls}"
        text = f"package {BASE_PKG}.listener;\n\n" + body
        ident = f"java:{fqcn}"
        self.add(f"{JAVA}/{fqcn.replace('.', '/')}.java", text, "java_listener", ident,
                 {"archetype": arche}, [], "migrate-with-update", False, {"fqcn": fqcn})
        return {"identity": ident, "fqcn": fqcn, "task": task}

    def _security(self, n):
        cls = f"BranchUserGroupCallback{n:04d}"
        fqcn = f"{BASE_PKG}.security.{cls}"
        groups = ", ".join(f'"{g}"' for g in GROUPS)
        text = (f"package {BASE_PKG}.security;\n\n"
                "import java.util.Arrays;\nimport java.util.List;\n\n"
                "import org.kie.api.task.UserGroupCallback;\n\n"
                "/** Fictional static group mapping (synthetic pilot fixture; no directory server). */\n"
                f"public class {cls} implements UserGroupCallback {{\n"
                f"    private static final List<String> GROUPS = Arrays.asList({groups});\n"
                "    @Override public boolean existsUser(String userId) { return userId != null; }\n"
                "    @Override public boolean existsGroup(String groupId) { return GROUPS.contains(groupId); }\n"
                "    @Override public List<String> getGroupsForUser(String userId) { return GROUPS; }\n}\n")
        ident = f"java:{fqcn}"
        self.add(f"{JAVA}/{fqcn.replace('.', '/')}.java", text, "java_security", ident,
                 {"archetype": "user-group-callback"}, [], "replace", False, {"fqcn": fqcn})
        return {"identity": ident, "fqcn": fqcn}

    # ---------------------------------------------------------------- rules
    def _drl(self, n, umodels, shared_session):
        dom = self.domain()
        pkg = f"{BASE_PKG}.{dom}.rules"
        group = f"{dom}-rules-{n:04d}"
        model = self.rng.choice(umodels)
        threshold = self.rng.randrange(500, 5000, 50)
        score = self.rng.randrange(550, 720, 10)
        names = [f"{_cap(dom)} R{n:04d} {s}" for s in ("High Value", "Low Score", "Standard")]
        v = model["cls"]
        rules = [
            (names[0], 10, f"$o : {v}(amount > {threshold}, status == null)",
             '$o.setStatus("REFER");\n    $o.setValidated(true);'),
            (names[1], 5, f"$o : {v}(score < {score}, status == null)",
             '$o.setStatus("DECLINE");\n    $o.setValidated(true);'),
            (names[2], 1, f"$o : {v}(amount <= {threshold}, score >= {score}, status == null)",
             '$o.setStatus("APPROVE");\n    $o.setValidated(true);'),
        ]
        if shared_session:
            rules[0] = (names[0], 10, rules[0][2],
                        '$o.setStatus("REFER");\n    $o.setValidated(true);\n'
                        f'    insert(new {v}());\n    update($o);')
        body = "".join(
            f'rule "{nm}"\n    ruleflow-group "{group}"\n    salience {sal}\nwhen\n    {lhs}\nthen\n    {rhs}\nend\n\n'
            for nm, sal, lhs, rhs in rules)
        text = (f"package {pkg};\n\nimport {model['fqcn']};\n\n"
                f"// Fictional {dom} rules (synthetic pilot fixture)\n\n" + body)
        ident = f"drl:{pkg}/{group}"
        scen = {"archetype": "ruleflow-group"}
        disp = "migrate"
        if shared_session:
            scen["exception"] = "shared-session-insert"
            disp = "migrate-with-update"
        self.add(f"{RES}/{pkg.replace('.', '/')}/{_cap(dom)}Rules{n:04d}.drl", text, "drl", ident,
                 scen, [model["identity"]], disp, True,
                 {"package": pkg, "group": group, "rule_names": names})
        return {"identity": ident, "group": group}

    def _dmn(self, n, legacy):
        dom = self.domain()
        name = f"{_cap(dom)} Eligibility {n:04d}"
        ns = f"https://fictionalbank.example/dmn/{dom}/eligibility{n:04d}"
        dns = NS_DMN11 if legacy else NS_DMN12
        lo = self.rng.randrange(18, 25)
        cap = self.rng.randrange(1000, 20000, 500)
        text = f"""<?xml version="1.0" encoding="UTF-8"?>
<dmn:definitions xmlns:dmn={quoteattr(dns)} xmlns={quoteattr(ns)} xmlns:feel="http://www.omg.org/spec/FEEL/20140401" id="_def{n:04d}" name={quoteattr(name)} namespace={quoteattr(ns)}>
  <dmn:inputData id="_in{n:04d}_age" name="Age">
    <dmn:variable id="_in{n:04d}_age_v" name="Age" typeRef="number"/>
  </dmn:inputData>
  <dmn:inputData id="_in{n:04d}_amount" name="Amount">
    <dmn:variable id="_in{n:04d}_amount_v" name="Amount" typeRef="number"/>
  </dmn:inputData>
  <dmn:decision id="_dec{n:04d}" name="Eligible">
    <dmn:variable id="_dec{n:04d}_v" name="Eligible" typeRef="boolean"/>
    <dmn:informationRequirement id="_ir{n:04d}a">
      <dmn:requiredInput href="#_in{n:04d}_age"/>
    </dmn:informationRequirement>
    <dmn:informationRequirement id="_ir{n:04d}b">
      <dmn:requiredInput href="#_in{n:04d}_amount"/>
    </dmn:informationRequirement>
    <dmn:decisionTable id="_dt{n:04d}" hitPolicy="FIRST">
      <dmn:input id="_dt{n:04d}_i1"><dmn:inputExpression id="_dt{n:04d}_e1" typeRef="number"><dmn:text>Age</dmn:text></dmn:inputExpression></dmn:input>
      <dmn:input id="_dt{n:04d}_i2"><dmn:inputExpression id="_dt{n:04d}_e2" typeRef="number"><dmn:text>Amount</dmn:text></dmn:inputExpression></dmn:input>
      <dmn:output id="_dt{n:04d}_o1"/>
      <dmn:rule id="_dt{n:04d}_r1">
        <dmn:inputEntry id="_dt{n:04d}_r1a"><dmn:text>&lt; {lo}</dmn:text></dmn:inputEntry>
        <dmn:inputEntry id="_dt{n:04d}_r1b"><dmn:text>-</dmn:text></dmn:inputEntry>
        <dmn:outputEntry id="_dt{n:04d}_r1o"><dmn:text>false</dmn:text></dmn:outputEntry>
      </dmn:rule>
      <dmn:rule id="_dt{n:04d}_r2">
        <dmn:inputEntry id="_dt{n:04d}_r2a"><dmn:text>-</dmn:text></dmn:inputEntry>
        <dmn:inputEntry id="_dt{n:04d}_r2b"><dmn:text>&lt;= {cap}</dmn:text></dmn:inputEntry>
        <dmn:outputEntry id="_dt{n:04d}_r2o"><dmn:text>true</dmn:text></dmn:outputEntry>
      </dmn:rule>
      <dmn:rule id="_dt{n:04d}_r3">
        <dmn:inputEntry id="_dt{n:04d}_r3a"><dmn:text>-</dmn:text></dmn:inputEntry>
        <dmn:inputEntry id="_dt{n:04d}_r3b"><dmn:text>-</dmn:text></dmn:inputEntry>
        <dmn:outputEntry id="_dt{n:04d}_r3o"><dmn:text>false</dmn:text></dmn:outputEntry>
      </dmn:rule>
    </dmn:decisionTable>
  </dmn:decision>
</dmn:definitions>
"""
        ident = f"dmn:{ns}#{name}"
        scen = {"archetype": "decision-table"}
        disp = "migrate"
        if legacy:
            scen["exception"] = "dmn-1-1-namespace"
            disp = "migrate-with-update"
        self.add(f"{RES}/{BASE_PKG.replace('.', '/')}/{dom}/{name}.dmn", text, "dmn", ident, scen, [],
                 disp, True, {"namespace": ns, "name": name, "decision": "Eligible"})
        return {"identity": ident, "namespace": ns, "name": name}

    # ---------------------------------------------------------------- processes
    def _bpmn(self, pid, dom, g, arche, exc, model, deps, extra):
        nodes = []  # (id, tag, attrs, inner)
        flows = []  # (id, src, tgt, condition xml or "")
        var = "subject"
        nodes.append(("Start", "startEvent", 'name="Start"', ""))
        init_fmt = SCRIPT_JS if exc == "javascript-script" else SCRIPT_JAVA
        if exc == "javascript-script":
            init_body = 'kcontext.setVariable("status", "started");\nprint("started " + kcontext.getProcessInstance().getId());'
        else:
            init_body = 'kcontext.setVariable("status", "started");'
        nodes.append(("Init", "scriptTask", f'name="Initialise" scriptFormat="{init_fmt}"',
                      f"<bpmn2:script>{escape(init_body)}</bpmn2:script>"))
        prev = "Init"
        flows.append(("F_Start_Init", "Start", "Init", ""))

        def chain(nid, tag, attrs, inner=""):
            nonlocal prev
            nodes.append((nid, tag, attrs, inner))
            flows.append((f"F_{prev}_{nid}", prev, nid, ""))
            prev = nid

        if arche == "script":
            chain("Compute", "scriptTask", f'name="Compute fee" scriptFormat="{SCRIPT_JAVA}"',
                  "<bpmn2:script>" + escape('kcontext.setVariable("status", "computed");') + "</bpmn2:script>")
        elif arche == "gateway":
            chain("Split", "exclusiveGateway", 'name="Amount?" gatewayDirection="Diverging"')
            hi_lang = LANG_DROOLS if exc == "drools-gateway-dialect" else SCRIPT_JAVA
            hi_expr = f"{model['cls']}(amount &gt; 10000)" if exc == "drools-gateway-dialect" else \
                f"return {var} != null &amp;&amp; {var}.getAmount() != null &amp;&amp; {var}.getAmount().intValue() &gt; 10000;"
            lo_expr = f"return {var} == null || {var}.getAmount() == null || {var}.getAmount().intValue() &lt;= 10000;"
            for branch, lang, expr in (("High", hi_lang, hi_expr), ("Low", SCRIPT_JAVA, lo_expr)):
                nodes.append((f"{branch}Path", "scriptTask", f'name="{branch} path" scriptFormat="{SCRIPT_JAVA}"',
                              "<bpmn2:script>" + escape(f'kcontext.setVariable("status", "{branch.lower()}");') + "</bpmn2:script>"))
                cond = (f'<bpmn2:conditionExpression xsi:type="bpmn2:tFormalExpression" language="{lang}">'
                        f"{expr}</bpmn2:conditionExpression>")
                flows.append((f"F_Split_{branch}", "Split", f"{branch}Path", cond))
            nodes.append(("Join", "exclusiveGateway", 'name="Join" gatewayDirection="Converging"', ""))
            flows.append(("F_High_Join", "HighPath", "Join", ""))
            flows.append(("F_Low_Join", "LowPath", "Join", ""))
            prev = "Join"
        elif arche == "human-task":
            t = extra["task"]
            inner = (f'<bpmn2:ioSpecification id="IO_{t}">'
                     f'<bpmn2:dataInput id="{t}_TaskName" name="TaskName"/>'
                     f'<bpmn2:dataInput id="{t}_GroupId" name="GroupId"/>'
                     f'<bpmn2:dataInput id="{t}_subjectIn" name="subjectIn" itemSubjectRef="_subjectItem"/>'
                     f'<bpmn2:inputSet id="IS_{t}"><bpmn2:dataInputRefs>{t}_TaskName</bpmn2:dataInputRefs>'
                     f'<bpmn2:dataInputRefs>{t}_GroupId</bpmn2:dataInputRefs>'
                     f'<bpmn2:dataInputRefs>{t}_subjectIn</bpmn2:dataInputRefs></bpmn2:inputSet>'
                     f'</bpmn2:ioSpecification>'
                     f'<bpmn2:dataInputAssociation id="DIA_{t}_n"><bpmn2:targetRef>{t}_TaskName</bpmn2:targetRef>'
                     f'<bpmn2:assignment id="A_{t}_n"><bpmn2:from xsi:type="bpmn2:tFormalExpression">{t}</bpmn2:from>'
                     f'<bpmn2:to xsi:type="bpmn2:tFormalExpression">{t}_TaskName</bpmn2:to></bpmn2:assignment></bpmn2:dataInputAssociation>'
                     f'<bpmn2:dataInputAssociation id="DIA_{t}_g"><bpmn2:targetRef>{t}_GroupId</bpmn2:targetRef>'
                     f'<bpmn2:assignment id="A_{t}_g"><bpmn2:from xsi:type="bpmn2:tFormalExpression">{extra["group"]}</bpmn2:from>'
                     f'<bpmn2:to xsi:type="bpmn2:tFormalExpression">{t}_GroupId</bpmn2:to></bpmn2:assignment></bpmn2:dataInputAssociation>'
                     f'<bpmn2:dataInputAssociation id="DIA_{t}_s"><bpmn2:sourceRef>{var}</bpmn2:sourceRef>'
                     f'<bpmn2:targetRef>{t}_subjectIn</bpmn2:targetRef></bpmn2:dataInputAssociation>')
            chain("Human", "userTask", f'name="{t}" drools:taskName="{t}"', inner)
        elif arche == "subprocess":
            chain("Call", "callActivity", f'name="Call child" calledElement="{extra["callee"]}" drools:independent="false" drools:waitForCompletion="true"')
        elif arche == "rule-task":
            chain("Rules", "businessRuleTask",
                  f'name="Apply rules" implementation="{IMPL_RULE}" drools:ruleFlowGroup="{extra["group"]}"')
        elif arche == "decision-task":
            d = extra["dmn"]
            pairs = (("namespace", d["namespace"]), ("model", d["name"]), ("decision", "Eligible"))
            inner = '<bpmn2:ioSpecification id="IO_Decide">' + "".join(
                f'<bpmn2:dataInput id="Decide_{k}" name="{k}"/>' for k, _ in pairs) + \
                '<bpmn2:inputSet id="IS_Decide">' + "".join(
                f"<bpmn2:dataInputRefs>Decide_{k}</bpmn2:dataInputRefs>" for k, _ in pairs) + \
                "</bpmn2:inputSet></bpmn2:ioSpecification>" + "".join(
                f'<bpmn2:dataInputAssociation id="DIA_Decide_{k}"><bpmn2:targetRef>Decide_{k}</bpmn2:targetRef>'
                f'<bpmn2:assignment id="A_Decide_{k}"><bpmn2:from xsi:type="bpmn2:tFormalExpression">{escape(v)}</bpmn2:from>'
                f'<bpmn2:to xsi:type="bpmn2:tFormalExpression">Decide_{k}</bpmn2:to></bpmn2:assignment></bpmn2:dataInputAssociation>'
                for k, v in pairs)
            chain("Decide", "businessRuleTask", f'name="Evaluate eligibility" implementation="{IMPL_DMN}"', inner)
        elif arche == "service-handler":
            h = extra["handler"]
            chain("Service", "task", f'name="{h["name"]}" drools:taskName="{h["name"]}"')
        chain("End", "endEvent", 'name="End"')

        incoming, outgoing = {}, {}
        for fid, s, t, _ in flows:
            outgoing.setdefault(s, []).append(fid)
            incoming.setdefault(t, []).append(fid)
        parts = []
        for nid, tag, attrs, inner in nodes:
            io = "".join(f"<bpmn2:incoming>{f}</bpmn2:incoming>" for f in incoming.get(nid, [])) + \
                "".join(f"<bpmn2:outgoing>{f}</bpmn2:outgoing>" for f in outgoing.get(nid, []))
            parts.append(f'    <bpmn2:{tag} id="{nid}" {attrs}>{io}{inner}</bpmn2:{tag}>')
        for fid, s, t, cond in flows:
            parts.append(f'    <bpmn2:sequenceFlow id="{fid}" sourceRef="{s}" targetRef="{t}">{cond}</bpmn2:sequenceFlow>')
        shapes = "".join(
            f'      <bpmndi:BPMNShape id="{nid}_di" bpmnElement="{nid}"><dc:Bounds x="{100 + i * 150}" y="100" width="100" height="80"/></bpmndi:BPMNShape>\n'
            for i, (nid, *_rest) in enumerate(nodes))
        edges = "".join(
            f'      <bpmndi:BPMNEdge id="{fid}_di" bpmnElement="{fid}"/>\n' for fid, *_r in flows)
        name = f"{_cap(dom)} {arche.replace('-', ' ')} {g:04d}"
        text = f"""<?xml version="1.0" encoding="UTF-8"?>
<bpmn2:definitions xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:bpmn2="{NS_BPMN}" xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" xmlns:di="http://www.omg.org/spec/DD/20100524/DI" xmlns:drools="http://www.jboss.org/drools" id="_defs_{g:04d}" targetNamespace="http://www.omg.org/bpmn20">
  <bpmn2:itemDefinition id="_subjectItem" structureRef="{model['fqcn']}"/>
  <bpmn2:itemDefinition id="_statusItem" structureRef="String"/>
  <bpmn2:process id="{pid}" name={quoteattr(name)} isExecutable="true" drools:packageName="{BASE_PKG}.{dom}" drools:version="1.0">
    <bpmn2:property id="{var}" itemSubjectRef="_subjectItem" name="{var}"/>
    <bpmn2:property id="status" itemSubjectRef="_statusItem" name="status"/>
{chr(10).join(parts)}
  </bpmn2:process>
  <bpmndi:BPMNDiagram id="_diagram_{g:04d}">
    <bpmndi:BPMNPlane id="_plane_{g:04d}" bpmnElement="{pid}">
{shapes}{edges}    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</bpmn2:definitions>
"""
        self.process_nodes += len(nodes)
        scen = {"archetype": arche}
        disp = "migrate"
        if exc:
            scen["exception"] = exc
            disp = "migrate-with-update"
        fname = f"{_cap(dom)}{_cap(arche.replace('-task', 'Task').replace('-handler', 'Handler').replace('-', ''))}{g:04d}.bpmn"
        self.add(f"{RES}/{BASE_PKG.replace('.', '/')}/{dom}/{fname}", text, "bpmn", f"bpmn:{pid}",
                 scen, deps, disp, True, {"process_id": pid, "nodes": len(nodes)})
        if arche == "human-task":
            self._form(pid, dom, extra["task"], model)

    def _form(self, pid, dom, task, model):
        props = [{"name": n, "typeInfo": {"type": "BASE", "className": c, "multiple": False}}
                 for n, c in (("reference", "java.lang.String"), ("status", "java.lang.String"),
                              ("amount", "java.math.BigDecimal"), ("approved", "java.lang.Boolean"))]
        doc = {"id": f"form-{pid}-{task}", "name": f"{task}-taskform.frm",
               "model": {"processId": pid, "taskName": task, "name": "task", "properties": props},
               "fields": [{"name": p["name"], "binding": p["name"], "code": "TextBox"} for p in props],
               "layoutTemplate": {"version": 2, "rows": []}}
        text = json.dumps(doc, indent=2, sort_keys=True) + "\n"
        self.add(f"{RES}/{BASE_PKG.replace('.', '/')}/{dom}/{task}-taskform.frm", text, "form",
                 f"form:{pid}:{task}", {"archetype": "task-form"}, [f"bpmn:{pid}"], "regenerate", False,
                 {"process_id": pid, "task_name": task})

    def _wid(self, dom, handlers):
        entries = ",\n".join(
            "  [\n"
            f'    "name" : "{h["name"]}",\n'
            '    "parameters" : [ "Reference" : new StringDataType() ],\n'
            '    "results" : [ "Result" : new StringDataType() ],\n'
            f'    "displayName" : "{h["name"]}",\n'
            '    "icon" : "defaultservicenodeicon.png"\n'
            "  ]" for h in handlers)
        text = ("import org.jbpm.process.core.datatype.impl.type.StringDataType;\n\n[\n" + entries + "\n]\n")
        self.add(f"{RES}/{BASE_PKG.replace('.', '/')}/{dom}/WorkDefinitions.wid", text, "wid",
                 f"wid:{BASE_PKG}.{dom}", {"archetype": "work-definitions"}, [], "migrate", False,
                 {"names": [h["name"] for h in handlers]})

    def _config(self):
        tier = self.tier
        pom = f"""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.fictionalbank</groupId>
  <artifactId>bank-{tier}</artifactId>
  <version>1.0.0-SNAPSHOT</version>
  <packaging>kjar</packaging>
  <name>Fictional Bank {tier} workload (synthetic)</name>
  <properties>
    <maven.compiler.source>11</maven.compiler.source>
    <maven.compiler.target>11</maven.compiler.target>
    <version.org.kie>7.67.2.Final-redhat-00017</version.org.kie>
  </properties>
  <dependencies>
    <dependency><groupId>org.kie</groupId><artifactId>kie-api</artifactId><version>${{version.org.kie}}</version><scope>provided</scope></dependency>
    <dependency><groupId>org.kie</groupId><artifactId>kie-internal</artifactId><version>${{version.org.kie}}</version><scope>provided</scope></dependency>
    <dependency><groupId>org.jbpm</groupId><artifactId>jbpm-flow</artifactId><version>${{version.org.kie}}</version><scope>provided</scope></dependency>
    <dependency><groupId>org.jbpm</groupId><artifactId>jbpm-workitems-core</artifactId><version>${{version.org.kie}}</version><scope>provided</scope></dependency>
    <dependency><groupId>javax.persistence</groupId><artifactId>javax.persistence-api</artifactId><version>2.2</version><scope>provided</scope></dependency>
  </dependencies>
  <build>
    <plugins>
      <plugin><groupId>org.kie</groupId><artifactId>kie-maven-plugin</artifactId><version>${{version.org.kie}}</version><extensions>true</extensions></plugin>
    </plugins>
  </build>
</project>
"""
        self.add("pom.xml", pom, "config", "config:pom.xml", {"archetype": "maven-pom"}, [],
                 "migrate-with-update", False)
        km = ('<?xml version="1.0" encoding="UTF-8"?>\n<kmodule xmlns="http://www.drools.org/xsd/kmodule" '
              'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n'
              f'  <kbase name="bank{_cap(tier)}KBase" default="true" packages="{BASE_PKG}.*">\n'
              f'    <ksession name="bank{_cap(tier)}KSession" default="true" type="stateful"/>\n'
              "  </kbase>\n</kmodule>\n")
        self.add(f"{RES}/META-INF/kmodule.xml", km, "config", f"config:{RES}/META-INF/kmodule.xml",
                 {"archetype": "kmodule"}, [], "remove", False)
        wih = "".join(
            "    <work-item-handler>\n      <resolver>mvel</resolver>\n"
            f"      <identifier>new {h['fqcn']}()</identifier>\n"
            f"      <parameters/>\n      <name>{h['name']}</name>\n    </work-item-handler>\n"
            for h in self.handlers)
        pl = "".join(
            f"    <event-listener>\n      <resolver>reflection</resolver>\n      <identifier>{l['fqcn']}</identifier>\n"
            "      <parameters/>\n    </event-listener>\n" for l in self.listeners if not l["task"])
        tl = "".join(
            f"    <task-event-listener>\n      <resolver>reflection</resolver>\n      <identifier>{l['fqcn']}</identifier>\n"
            "      <parameters/>\n    </task-event-listener>\n" for l in self.listeners if l["task"])
        dd = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
              '<deployment-descriptor xsi:schemaLocation="http://www.jboss.org/jbpm deployment-descriptor.xsd" '
              'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n'
              "  <persistence-unit>org.jbpm.domain</persistence-unit>\n"
              "  <audit-persistence-unit>org.jbpm.domain</audit-persistence-unit>\n"
              "  <audit-mode>JPA</audit-mode>\n  <persistence-mode>JPA</persistence-mode>\n"
              "  <runtime-strategy>PER_PROCESS_INSTANCE</runtime-strategy>\n"
              f"  <event-listeners>\n{pl}  </event-listeners>\n"
              f"  <task-event-listeners>\n{tl}  </task-event-listeners>\n"
              f"  <work-item-handlers>\n{wih}  </work-item-handlers>\n"
              "  <required-roles/>\n  <limit-serialization-classes>true</limit-serialization-classes>\n"
              "</deployment-descriptor>\n")
        dd_deps = [h["identity"] for h in self.handlers] + [l["identity"] for l in self.listeners]
        self.add(f"{RES}/META-INF/kie-deployment-descriptor.xml", dd, "config",
                 f"config:{RES}/META-INF/kie-deployment-descriptor.xml",
                 {"archetype": "deployment-descriptor"}, dd_deps, "remove", False)
        ents = [m for m in self.models if m["persistent"]]
        px = ('<?xml version="1.0" encoding="UTF-8"?>\n'
              '<persistence version="2.0" xmlns="http://java.sun.com/xml/ns/persistence" '
              'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n'
              '  <persistence-unit name="bank-domain" transaction-type="JTA">\n'
              "    <provider>org.hibernate.jpa.HibernatePersistenceProvider</provider>\n"
              "    <jta-data-source>java:jboss/datasources/FictionalBankDS</jta-data-source>\n" +
              "".join(f"    <class>{m['fqcn']}</class>\n" for m in ents) +
              "    <exclude-unlisted-classes>true</exclude-unlisted-classes>\n"
              "  </persistence-unit>\n</persistence>\n")
        self.add(f"{RES}/META-INF/persistence.xml", px, "config", f"config:{RES}/META-INF/persistence.xml",
                 {"archetype": "persistence-unit"}, [m["identity"] for m in ents], "remove", False)
        self.add("project.imports", "<configuration>\n  <imports>\n    <imports/>\n  </imports>\n  <version>1.0</version>\n</configuration>\n",
                 "config", "config:project.imports", {"archetype": "bc-metadata"}, [], "remove", False)
        self.add("project.repositories",
                 "<project-repositories>\n  <repositories>\n    <repository>\n      <include>true</include>\n"
                 "      <metadata>\n        <id>fictional-bank-internal</id>\n"
                 "        <url>https://maven.fictionalbank.example/releases</url>\n"
                 "        <source>PROJECT</source>\n      </metadata>\n    </repository>\n  </repositories>\n</project-repositories>\n",
                 "config", "config:project.repositories", {"archetype": "bc-metadata"}, [], "remove", False)
        self.add("package-names-white-list", f"{BASE_PKG}.**\n", "config", "config:package-names-white-list",
                 {"archetype": "bc-metadata"}, [], "remove", False)


def _chain_depth(calls):
    best = 0
    for start in calls:
        depth, cur, seen = 1, start, {start}
        while cur in calls:
            cur = calls[cur]
            if cur in seen:
                raise ValueError("call cycle")
            seen.add(cur)
            depth += 1
        best = max(best, depth)
    return best


def _manifest_hash(m):
    body = {k: v for k, v in m.items() if k != "manifest_sha256"}
    return _sha(_canon(body))


def build_manifest(tier, tiers=None):
    """Return (files, manifest) without writing anything."""
    tiers = tiers or load_tiers()
    b = _Builder(tier, tiers).build()
    assets = []
    for a in sorted(b.assets, key=lambda x: x["path"]):
        data = b.files[a["path"]]
        assets.append(dict(a, sha256=_sha(data), bytes=len(data)))
    business = {k: sum(1 for a in assets if a["kind"] == k) for k in ("bpmn", "dmn", "drl")}
    support = {}
    for a in assets:
        if not a["business"]:
            support[a["kind"]] = support.get(a["kind"], 0) + 1
    manifest = {
        "schema_version": tiers["schema_version"],
        "generator_version": tiers["generator_version"],
        "tier": tier,
        "seed": tiers["seed"],
        "project_dir": f"v8-projects/v8-bank-{tier}",
        "summary": {
            "business": business,
            "support": dict(sorted(support.items())),
            "total_files": len(assets),
            "total_bytes": sum(a["bytes"] for a in assets),
            "process_nodes": b.process_nodes,
            "dependency_edges": sum(len(a["dependencies"]) for a in assets),
            "exceptions": sum(1 for a in assets if a["scenario"].get("exception")),
            "exception_breakdown": _count(a["scenario"]["exception"] for a in assets if a["scenario"].get("exception")),
            "max_call_chain_depth": _chain_depth(b.calls),
        },
        "assets": assets,
    }
    manifest["manifest_sha256"] = _manifest_hash(manifest)
    return b.files, manifest


def _count(items):
    out = {}
    for i in items:
        out[i] = out.get(i, 0) + 1
    return dict(sorted(out.items()))


def _project_files(project):
    return sorted(p.relative_to(project).as_posix() for p in project.rglob("*") if p.is_file())


def verify_manifest(manifest_path):
    """Return a list of human-readable problems; empty means the inputs match the manifest."""
    manifest_path = Path(manifest_path)
    m = json.loads(manifest_path.read_text())
    problems = []
    if _manifest_hash(m) != m.get("manifest_sha256"):
        problems.append("manifest_sha256 mismatch: manifest body was modified")
    project = manifest_path.parent / m["project_dir"]
    if not project.is_dir():
        return problems + [f"project dir missing: {project}"]
    expected = {a["path"]: a for a in m["assets"]}
    actual = set(_project_files(project))
    for path in sorted(set(expected) - actual):
        problems.append(f"missing file: {path}")
    for path in sorted(actual - set(expected)):
        problems.append(f"unexpected file: {path}")
    for path in sorted(set(expected) & actual):
        data = (project / path).read_bytes()
        if _sha(data) != expected[path]["sha256"]:
            problems.append(f"sha256 mismatch: {path}")
        elif len(data) != expected[path]["bytes"]:
            problems.append(f"size mismatch: {path}")
    return problems


def preflight(run_dir):
    run_dir = Path(run_dir)
    m = json.loads((run_dir / "source-manifest.json").read_text())
    project = run_dir / m["project_dir"]
    xml_errors = []
    for a in m["assets"]:
        if a["path"].endswith((".bpmn", ".dmn", ".xml", "project.imports", "project.repositories")):
            try:
                ET.parse(project / a["path"])
            except ET.ParseError as e:
                xml_errors.append(f"{a['path']}: {e}")
    ids = {a["identity"] for a in m["assets"]}
    unresolved = [f"{a['identity']} -> {d}" for a in m["assets"] for d in a["dependencies"] if d not in ids]
    integrity = verify_manifest(run_dir / "source-manifest.json")
    import check_coverage  # local module; imported lazily to keep generation standalone
    index = check_coverage.index_project(project)
    broken = check_coverage.check_references(index)
    ok = not (xml_errors or unresolved or integrity or broken or index["parse_errors"])
    result = {
        "status": "pass" if ok else "fail",
        "tier": m["tier"],
        "seed": m["seed"],
        "manifest_sha256": m["manifest_sha256"],
        "summary": m["summary"],
        "checks": {
            "xml_parse_errors": xml_errors,
            "unresolved_manifest_dependencies": unresolved,
            "manifest_integrity_problems": integrity,
            "broken_source_references": broken,
            "index_parse_errors": index["parse_errors"],
            "indexed_counts": {k: len(v) for k, v in index["by_kind"].items()},
        },
        "notes": "Mechanical preflight only: inputs are uncompiled and not established as v8-runtime-valid.",
    }
    (run_dir / "preflight.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def generate(tier, run_dir, tiers=None):
    run_dir = Path(run_dir)
    files, manifest = build_manifest(tier, tiers)
    project = run_dir / manifest["project_dir"]
    if project.exists() and any(project.iterdir()):
        raise FileExistsError(f"refusing to overwrite existing inputs: {project}")
    if (run_dir / "source-manifest.json").exists():
        raise FileExistsError(f"refusing to overwrite existing manifest in {run_dir}")
    for rel, data in files.items():
        p = project / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    (run_dir / "source-manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    preflight(run_dir)
    return manifest


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--tier", choices=["small", "medium", "large"])
    g.add_argument("--verify", metavar="MANIFEST")
    ap.add_argument("--run-dir")
    args = ap.parse_args(argv)
    if args.verify:
        problems = verify_manifest(args.verify)
        for p in problems:
            print(f"FAIL  {p}")
        print("PASS  source inputs match manifest" if not problems else f"== {len(problems)} problem(s)")
        return 1 if problems else 0
    if not args.run_dir:
        ap.error("--run-dir is required with --tier")
    try:
        m = generate(args.tier, args.run_dir)
    except FileExistsError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    pre = json.loads((Path(args.run_dir) / "preflight.json").read_text())
    print(json.dumps({"tier": m["tier"], "manifest_sha256": m["manifest_sha256"],
                      "summary": m["summary"], "preflight": pre["status"]}, indent=2))
    return 0 if pre["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
