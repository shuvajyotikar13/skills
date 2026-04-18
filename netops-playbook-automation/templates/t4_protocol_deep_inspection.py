"""
Template 4: Protocol Feature Deep Inspection Workflow
======================================================
Comprehensive troubleshooting of a specific protocol/feature area.
Combines config validation, runtime counter analysis, LLM-powered
case context parsing, and multi-check diagnostic pipelines.

Use this template when:
- Troubleshooting a specific protocol (SCTP, GTP, BGP, OSPF, etc.)
- Multiple independent checks are needed (5+)
- LLM should parse the case description for context
- Config XML + command output + counters all need analysis
- The playbook is large and covers many failure modes

TODO markers indicate where to customize for your specific playbook.
"""

# NO IMPORTS NEEDED for SDK APIs - auto-injected at runtime
import os
import re
import json
import xml.etree.ElementTree as ET


# =========================================================================
# PROTOCOL CONSTANTS — TODO: Define for your protocol
# =========================================================================

# TODO: Define the applications associated with your protocol
PROTOCOL_APPLICATIONS = frozenset({
    # "app_name_1", "app_name_2",
})

# TODO: Define supported hardware models (if applicable)
SUPPORTED_MODELS = frozenset({
    "VIRTUAL-ROUTER-VM",
    # "HW-ROUTER-5000", "HW-ROUTER-9000", ...
})


# =========================================================================
# LLM CASE CONTEXT PARSING — TODO: Customize the prompt
# =========================================================================

_CASE_PARSE_SYSTEM_PROMPT = """\
You are a senior network support engineer. You are analyzing a customer \
support case to extract structured information for troubleshooting.

Your task: read the case title and description, then extract these fields:

- "protocol": transport-layer protocol. null if unknown.
- "source_ip": source IP address. null if absent.
- "destination_ip": destination IP address. null if absent.
- "source_zone": Network source zone. null if absent.
- "destination_zone": Network destination zone. null if absent.
- "security_rule": security policy rule name. null if absent.
- "problem_statement": one concise sentence (max 30 words).
- "suspected_issues": list of issue categories from:
  TODO: Define your issue categories here
  - "category_1" - description
  - "category_2" - description

Return ONLY a valid JSON object. No markdown, no explanation.
Use null for fields that cannot be determined.
"""


def _call_llm(system_prompt: str, user_content: str) -> str:
    """One-shot LLM call via LiteLLM endpoint.

    Returns the raw response text, or empty string on error.
    """
    import requests as _http

    url = os.getenv("LITELLM_URL", "").rstrip("/") + "/chat/completions"
    api_key = os.getenv("LITELLM_API_KEY", "")
    model = os.getenv("LITELLM_MODEL", "anthropic/claude-sonnet-4-6")

    if not url or not model:
        return ""

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        "temperature": 0.0,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        resp = _http.post(url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception:
        return ""


def parse_case_context_with_llm(case_analysis_context: dict) -> dict:
    """Use LLM to extract structured fields from case description."""
    title = case_analysis_context.get("title", "")
    description = case_analysis_context.get("description", "")
    user_content = f"Case Title: {title}\n\nCase Description:\n{description}"

    raw = _call_llm(_CASE_PARSE_SYSTEM_PROMPT, user_content)
    if not raw:
        return {}

    try:
        # Strip markdown code fences if present
        cleaned = re.sub(r"```json\s*", "", raw)
        cleaned = re.sub(r"```\s*$", "", cleaned)
        return json.loads(cleaned)
    except (json.JSONDecodeError, ValueError):
        return {}


# =========================================================================
# HELPER FUNCTIONS
# =========================================================================

def parse_system_info(output: str) -> dict:
    """Parse 'show system info' output."""
    parsed = {}
    patterns = {
        'hostname': r"hostname:\s*(.*)",
        'model': r"model:\s*(.*)",
        'serial': r"serial:\s*(.*)",
        'sw_version': r"sw-version:\s*(.*)",
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, output)
        if match:
            parsed[key] = match.group(1).strip()
    return parsed


# =========================================================================
# CHECK FUNCTIONS — TODO: Implement each diagnostic check
# =========================================================================

def check_platform_support(sys_info: dict) -> list:
    """Check if the platform supports this protocol.

    TODO: Implement platform compatibility check.
    """
    findings = []
    model = sys_info.get("model", "")
    if model and model not in SUPPORTED_MODELS:
        findings.append({
            "type": "issue", "severity": "critical",
            "description": f"Model {model} may not support this protocol",
            "affected_component": "Platform",
            "detection_method": "Model compatibility check",
        })
    return findings


def check_feature_enabled(root: ET.Element, commands: list) -> list:
    """Check if the protocol feature is enabled in config and runtime.

    TODO: Implement feature enablement check.
    """
    findings = []
    # TODO: Check deviceconfig for feature enablement
    # TODO: Check runtime status via command output
    return findings


def check_profile_config(root: ET.Element) -> list:
    """Validate protocol-specific profile configuration.

    TODO: Implement profile validation.
    """
    findings = []
    # TODO: Find profile entries in config XML
    # TODO: Validate required settings
    return findings


def check_security_rules(root: ET.Element) -> list:
    """Validate security rules for protocol traffic.

    TODO: Implement security rule validation.
    """
    findings = []
    # TODO: Find security rules with protocol applications
    # TODO: Validate rule order, profiles, services
    return findings


def check_runtime_counters(commands: list) -> list:
    """Analyze runtime counters for protocol issues.

    TODO: Implement counter analysis.
    """
    findings = []
    # TODO: Parse counter output
    # TODO: Check for error/drop counters
    return findings


# =========================================================================
# MAIN WORKFLOW
# =========================================================================

@workflow_tool(
    name="TODO:troubleshoot",  # TODO: e.g., "sctp:troubleshoot"
    description="TODO: Comprehensive troubleshooting for [protocol]",
    requires=[],
    tags=["TODO"],
    tsf_data={
        "commands": [
            "show system info",
            # TODO: Add protocol-specific commands
        ],
        "log_files": [
            # TODO: Add protocol-specific log files
        ],
    },
    keywords=["TODO"],
)
@flow(name="TODO-troubleshoot")
def protocol_deep_inspection_workflow(
    tsf_id: Optional[str] = None,
    case_context: Optional[Dict[str, Any]] = None,
    case_identifier: Optional[str] = None,
    device_serial: Optional[str] = None,
    **kwargs,
) -> Dict[str, Any]:
    """TODO: Comprehensive troubleshooting for [protocol/feature]."""
    logger = get_run_logger()
    logger.info(f"Starting protocol deep inspection for TSF: {tsf_id}")

    findings = []
    analysis_data = {}

    try:
        if not case_context:
            return create_result(
                status="warning",
                playbook_name="TODO_playbook_name",
                display_name="TODO Display Name",
                observation=[], findings=[],
            )

        # Step 1: Parse case context with LLM (optional)
        case_analysis = case_context.get("case_analysis_context", {})
        if case_analysis:
            case_info = parse_case_context_with_llm(case_analysis)
            analysis_data["case_info"] = case_info
            logger.info(f"LLM case parse: {case_info.get('problem_statement', 'N/A')}")

        # Step 2: Get system info
        sys_cmds = get_commands(case_context, command_filter="show system info")
        sys_output = sys_cmds[0].output if sys_cmds else ""
        sys_info = parse_system_info(sys_output)
        analysis_data["system_info"] = sys_info

        # Step 3: Get config XML
        config_xml = get_configs(case_context)
        root = None
        if config_xml:
            try:
                root = ET.fromstring(config_xml)
            except ET.ParseError as e:
                logger.error(f"Config parse error: {e}")

        # Step 4: Get all commands
        all_commands = get_commands(case_context) if case_context else []

        # Step 5: Run diagnostic pipeline
        findings.extend(check_platform_support(sys_info))

        if root is not None:
            findings.extend(check_feature_enabled(root, all_commands))
            findings.extend(check_profile_config(root))
            findings.extend(check_security_rules(root))

        findings.extend(check_runtime_counters(all_commands))

        # Step 6: Build observation
        observation = []
        if findings:
            obs_md = "## Protocol Troubleshooting Results\n\n"
            obs_md += f"**Device:** {sys_info.get('hostname', 'N/A')} "
            obs_md += f"({sys_info.get('model', 'N/A')})\n\n"
            obs_md += f"### Findings ({len(findings)})\n\n"
            for f in findings:
                obs_md += f"- **[{f['severity']}]** {f['description']}\n"
            observation = [{"markdown": obs_md}]

        status = "success"
        if any(f["severity"] == "critical" for f in findings):
            status = "error"
        elif any(f["severity"] == "warning" for f in findings):
            status = "warning"

        return create_result(
            status=status,
            playbook_name="TODO_playbook_name",
            display_name="TODO Display Name",
            observation=observation, findings=findings,
            analysis_data=analysis_data,
            case_identifier=case_identifier,
            device_serial=device_serial,
        )

    except Exception as e:
        logger.error(f"Workflow failed: {e}")
        return create_result(
            status="error",
            playbook_name="TODO_playbook_name",
            display_name="TODO Display Name",
            observation=[{"markdown": f"## Error\n\nWorkflow failed: {e}"}],
            findings=[],
        )
