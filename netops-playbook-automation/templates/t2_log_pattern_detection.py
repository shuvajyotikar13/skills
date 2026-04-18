"""
Template 2: Log Pattern Detection Workflow
============================================
Scan log files for specific regex patterns to detect events, build
timelines, identify flapping/state transitions, and correlate events
with potential root causes.

Use this template when:
- Primary data comes from log files
- You're looking for specific event patterns (up/down, errors, state changes)
- You need to build a timeline of events
- You need to detect flapping or repeated state transitions
- Analysis is deterministic (no AI/LLM needed)

TODO markers indicate where to customize for your specific playbook.
"""

# NO IMPORTS NEEDED for SDK APIs - auto-injected at runtime
import re
from collections import defaultdict
from datetime import datetime, timedelta


# =========================================================================
# LOG PATTERN CONSTANTS — TODO: Define your event patterns
# =========================================================================

# TODO: Define regex patterns for the events you want to detect
# These should be module-level constants, not inline in functions.

# Example: Event detection patterns
# EVENT_DOWN_PATTERN = r"session left established state"
# EVENT_UP_PATTERN = r"session enters established state"

# Example: Root cause correlation patterns
# COMMIT_PATTERN = r"configuration commit.*started|configuration commit.*processing"
# HA_FAILOVER_PATTERN = r"HA state change.*(?:active|standby|passive)"
# HIGH_CPU_PATTERN = r"high.*cpu|cpu.*usage.*(?:high|critical)"


# =========================================================================
# HELPER FUNCTIONS
# =========================================================================

def parse_event_from_log(log_entry) -> dict:
    """Extract structured event data from a log entry.

    TODO: Customize for your specific log format.

    Args:
        log_entry: A LogEntry object from get_logs().

    Returns:
        Dict with event details or None if not a relevant event.
    """
    message = log_entry.log_message if hasattr(log_entry, 'log_message') else str(log_entry)
    timestamp = log_entry.event_time if hasattr(log_entry, 'event_time') else None

    # TODO: Parse your specific event format
    # Example:
    # if re.search(EVENT_DOWN_PATTERN, message):
    #     return {"type": "down", "timestamp": timestamp, "message": message}
    # elif re.search(EVENT_UP_PATTERN, message):
    #     return {"type": "up", "timestamp": timestamp, "message": message}

    return None


def build_event_timeline(events: list) -> list:
    """Sort events by timestamp and build a timeline.

    Args:
        events: List of event dicts with 'timestamp' keys.

    Returns:
        Sorted list of events.
    """
    return sorted(events, key=lambda e: e.get("timestamp", ""))


def detect_flapping(events: list, window_minutes: int = 10, threshold: int = 3) -> list:
    """Detect flapping by counting state transitions within time windows.

    TODO: Customize window and threshold for your use case.

    Args:
        events: Sorted list of event dicts.
        window_minutes: Time window size in minutes.
        threshold: Minimum transitions to consider flapping.

    Returns:
        List of flap detection findings.
    """
    findings = []
    # TODO: Implement flap detection logic
    # Group events by entity (e.g., peer, tunnel, interface)
    # Count transitions within sliding windows
    # Generate findings for entities exceeding threshold
    return findings


def correlate_with_root_causes(events: list, cause_logs: list, window_minutes: int = 5) -> list:
    """Correlate detected events with potential root cause events.

    Args:
        events: List of detected event dicts.
        cause_logs: List of LogEntry objects for potential causes.
        window_minutes: Time window for correlation.

    Returns:
        List of correlation findings.
    """
    correlations = []
    # TODO: Implement time-window correlation
    # For each event, check if any root cause log occurred within the window
    return correlations


# =========================================================================
# MAIN WORKFLOW
# =========================================================================

@workflow_tool(
    name="TODO:workflow_name",  # TODO: e.g., "routing:bgp_flap_detection"
    description="TODO: Describe what events this workflow detects",
    requires=[],
    tags=["TODO"],
    tsf_data={
        "log_files": [
            # TODO: List the log files you need
            # "/var/log/device/system.log",
            # "/var/log/routing/protocol.log",
        ],
        "commands": ["show system info"],
    },
    keywords=["TODO"],
)
@flow(name="TODO-workflow-slug")
def log_pattern_detection_workflow(
    tsf_id: Optional[str] = None,
    case_context: Optional[Dict[str, Any]] = None,
    case_identifier: Optional[str] = None,
    device_serial: Optional[str] = None,
    **kwargs,
) -> Dict[str, Any]:
    """TODO: Describe the workflow purpose."""
    logger = get_run_logger()
    logger.info(f"Starting log pattern detection for TSF: {tsf_id}")

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

        # Step 1: Fetch event logs
        # TODO: Replace with your log file and pattern
        # event_logs = get_logs("system.log", case_context,
        #                       regex_pattern=EVENT_DOWN_PATTERN + "|" + EVENT_UP_PATTERN)
        event_logs = get_logs("system.log", case_context) if case_context else []
        logger.info(f"Found {len(event_logs)} log entries")

        # Step 2: Parse events
        events = []
        for entry in event_logs:
            event = parse_event_from_log(entry)
            if event:
                events.append(event)
        logger.info(f"Parsed {len(events)} relevant events")

        # Step 3: Build timeline
        timeline = build_event_timeline(events)
        analysis_data["event_count"] = len(timeline)

        # Step 4: Detect flapping / state issues
        flap_findings = detect_flapping(timeline)
        findings.extend(flap_findings)

        # Step 5: Correlate with root causes
        # TODO: Fetch root cause logs
        # cause_logs = get_logs("system.log", case_context,
        #                       regex_pattern=COMMIT_PATTERN + "|" + HA_FAILOVER_PATTERN)
        # correlations = correlate_with_root_causes(timeline, cause_logs)
        # findings.extend(correlations)

        # Step 6: Build observation
        observation = []
        if findings:
            obs_md = "## Event Detection Results\n\n"
            obs_md += f"- Total events detected: {len(events)}\n"
            obs_md += f"- Findings: {len(findings)}\n\n"
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
