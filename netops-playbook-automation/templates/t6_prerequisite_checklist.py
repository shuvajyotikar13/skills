"""
Template 6: Prerequisite Checklist Workflow
=============================================
Validate a series of prerequisites for a feature to function correctly.
Follows a linear checklist: license -> certificate -> connectivity ->
configuration -> runtime state. Each check is pass/fail with specific
remediation.

Use this template when:
- The playbook is a sequential checklist of prerequisites
- Each step is pass/fail with specific remediation
- Steps follow a dependency chain (license before cert before connectivity)
- The playbook validates feature readiness
- You may want to short-circuit on critical failures

TODO markers indicate where to customize for your specific playbook.
"""

# NO IMPORTS NEEDED for SDK APIs - auto-injected at runtime
import re


# =========================================================================
# HELPER FUNCTIONS — TODO: Add parsers for each check
# =========================================================================

def parse_system_info(output: str) -> dict:
    """Parse 'show system info' output."""
    parsed = {}
    patterns = {
        'hostname': r"hostname:\s*(.*)",
        'model': r"model:\s*(.*)",
        'serial': r"serial:\s*(.*)",
        'sw_version': r"sw-version:\s*(.*)",
        'family': r"family:\s*(.*)",
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, output)
        if match:
            parsed[key] = match.group(1).strip()
    return parsed


def parse_license_info(output: str) -> dict:
    """Parse 'request license info' output for a specific license.

    TODO: Customize for the license your feature requires.
    """
    license_data = {
        'license_found': False,
        'feature': 'NOT FOUND',
        'expires': 'NOT FOUND',
        'expired': 'UNKNOWN',
    }

    if not output:
        return license_data

    # TODO: Replace with your license feature name
    license_keywords = [
        # "Advanced Threat Protection",
        # "Cloud Security Service",
        # "Data Loss Prevention",
    ]

    lines = output.split('\n')
    for i, line in enumerate(lines):
        if any(kw.lower() in line.lower() for kw in license_keywords):
            license_data['license_found'] = True
            license_data['feature'] = line.strip()
            # Look ahead for expiry info
            for j in range(i, min(i + 10, len(lines))):
                check_line = lines[j].strip()
                if check_line.startswith('Expires:'):
                    license_data['expires'] = check_line.split(':', 1)[1].strip()
                elif check_line.startswith('Expired?:'):
                    license_data['expired'] = check_line.split(':', 1)[1].strip()
            break

    return license_data


def parse_device_certificate(output: str) -> dict:
    """Parse 'show device-certificate status' output."""
    cert = {
        'status': 'NOT FOUND',
        'is_valid': False,
        'fetch_failed': False,
    }

    if not output:
        return cert

    status_match = re.search(r"Current device certificate status:\s*(.*)", output)
    if status_match:
        cert['status'] = status_match.group(1).strip()
        cert['is_valid'] = cert['status'].lower() == 'valid'

    fetch_match = re.search(r"Last fetched status:\s*(.*)", output)
    if fetch_match:
        cert['fetch_failed'] = fetch_match.group(1).strip().lower() == 'failure'

    return cert


def parse_ha_state(output: str) -> dict:
    """Parse 'show high-availability state' output."""
    data = {'enabled': False, 'local_state': 'standalone'}

    if not output or "HA not enabled" in output:
        return data

    state_match = re.search(r"State:\s*([a-zA-Z\-]+)", output)
    if state_match:
        data['enabled'] = True
        data['local_state'] = state_match.group(1).lower()

    return data


# TODO: Add more parsers for your specific checks
# def parse_connectivity_status(output: str) -> dict: ...
# def parse_feature_config(config_xml: str) -> dict: ...


# =========================================================================
# MAIN WORKFLOW
# =========================================================================

@workflow_tool(
    name="TODO:workflow_name",  # TODO: e.g., "feature:prerequisite_check"
    description="TODO: Validates all prerequisites for [feature]",
    requires=[],
    tags=["TODO", "prerequisites"],
    tsf_data={
        "commands": [
            "show system info",
            "request license info",
            "show device-certificate status",
            "show high-availability state",
            # TODO: Add feature-specific commands
        ],
    },
    keywords=["TODO", "prerequisites", "validation"],
)
@flow(name="TODO-workflow-slug")
def prerequisite_checklist_workflow(
    tsf_id: Optional[str] = None,
    case_context: Optional[Dict[str, Any]] = None,
    case_identifier: Optional[str] = None,
    device_serial: Optional[str] = None,
    **kwargs,
) -> Dict[str, Any]:
    """TODO: Validates all prerequisites for [feature].

    Checks performed in order:
    1. TODO: License check
    2. TODO: Certificate check
    3. TODO: Connectivity check
    4. TODO: Configuration check
    5. TODO: Runtime state check
    """
    logger = get_run_logger()
    logger.info(f"Starting prerequisite checklist for TSF: {tsf_id}")

    findings = []
    remediation_actions = []
    checks_passed = 0
    checks_total = 0
    analysis_data = {}

    try:
        if not case_context:
            return create_result(
                status="warning",
                playbook_name="TODO_playbook_name",
                display_name="TODO Display Name",
                observation=[], findings=[],
            )

        # ---- CHECK 0: Device Info ----
        sys_cmds = get_commands(case_context, command_filter="show system info")
        sys_output = sys_cmds[0].output if sys_cmds else ""
        sys_info = parse_system_info(sys_output)
        analysis_data["system_info"] = sys_info

        # HA awareness
        ha_cmds = get_commands(case_context, command_filter="show high-availability state")
        ha_output = ha_cmds[0].output if ha_cmds else ""
        ha_state = parse_ha_state(ha_output)
        analysis_data["ha_state"] = ha_state

        # ---- CHECK 1: License ----
        checks_total += 1
        license_cmds = get_commands(case_context, command_filter="request license info")
        license_output = license_cmds[0].output if license_cmds else ""
        license_data = parse_license_info(license_output)
        analysis_data["license"] = license_data

        if not license_data['license_found']:
            findings.append({
                "type": "issue", "severity": "critical",
                "description": "TODO: Required license not found",
                "affected_component": "Licensing",
                "detection_method": "request license info analysis",
            })
            remediation_actions.append({
                "action_type": "manual_review",
                "description": "TODO: Install the required license",
                "risk_level": "low",
                "requires_maintenance": False,
            })
            # Short-circuit: no point checking further without license
            # TODO: Uncomment if you want to stop on license failure
            # return create_result(status="error", ...)
        elif license_data.get('expired', '').lower() == 'yes':
            findings.append({
                "type": "issue", "severity": "critical",
                "description": "TODO: Required license is expired",
                "affected_component": "Licensing",
                "detection_method": "request license info analysis",
            })
        else:
            checks_passed += 1

        # ---- CHECK 2: Device Certificate ----
        checks_total += 1
        cert_cmds = get_commands(case_context, command_filter="show device-certificate status")
        cert_output = cert_cmds[0].output if cert_cmds else ""
        cert_data = parse_device_certificate(cert_output)
        analysis_data["certificate"] = cert_data

        if not cert_data['is_valid']:
            findings.append({
                "type": "issue", "severity": "critical",
                "description": f"Device certificate status: {cert_data['status']}",
                "affected_component": "Device Certificate",
                "detection_method": "show device-certificate status",
            })
            remediation_actions.append({
                "action_type": "command",
                "description": "Fetch a new device certificate",
                "command": "request certificate fetch",
                "risk_level": "low",
                "requires_maintenance": False,
            })
        else:
            checks_passed += 1

        # ---- CHECK 3: TODO: Add more checks ----
        # checks_total += 1
        # ... your check logic ...
        # if check_passed:
        #     checks_passed += 1
        # else:
        #     findings.append({...})

        # ---- BUILD OBSERVATION ----
        observation = []
        hostname = sys_info.get("hostname", "N/A")
        model = sys_info.get("model", "N/A")
        ha_str = ha_state['local_state'] if ha_state['enabled'] else "standalone"

        obs_md = f"## Prerequisite Checklist Results\n\n"
        obs_md += f"**Device:** {hostname} ({model})\n"
        obs_md += f"**HA State:** {ha_str}\n"
        obs_md += f"**Checks Passed:** {checks_passed}/{checks_total}\n\n"

        if findings:
            obs_md += "### Failed Checks\n\n"
            for f in findings:
                obs_md += f"- **[{f['severity']}]** {f['description']}\n"
        else:
            obs_md += "### All Checks Passed\n\n"
            obs_md += "All prerequisites are met.\n"

        if remediation_actions:
            obs_md += "\n### Remediation Actions\n\n"
            for r in remediation_actions:
                obs_md += f"- {r['description']}"
                if r.get('command'):
                    obs_md += f" (`{r['command']}`)"
                obs_md += "\n"

        observation = [{"markdown": obs_md}]

        # Determine status
        status = "success"
        if any(f["severity"] == "critical" for f in findings):
            status = "error"
        elif any(f["severity"] == "warning" for f in findings):
            status = "warning"

        return create_result(
            status=status,
            playbook_name="TODO_playbook_name",
            display_name="TODO Display Name",
            observation=observation,
            findings=findings,
            remediation_actions=remediation_actions,
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
