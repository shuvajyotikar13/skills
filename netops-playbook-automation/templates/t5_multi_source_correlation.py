"""
Template 5: Multi-Source Correlation Workflow
===============================================
Collect events from multiple log sources, command outputs, and TSF
files, then deduplicate, reconcile timelines, and correlate across
sources to build a unified analysis.

Use this template when:
- Events come from 3+ different data sources
- You need to merge and deduplicate across sources
- Timeline reconciliation is needed
- Cross-source correlation reveals root causes
- The playbook involves correlating different event types

TODO markers indicate where to customize for your specific playbook.
"""

# NO IMPORTS NEEDED for SDK APIs - auto-injected at runtime
import re
from datetime import datetime, timedelta
from collections import defaultdict


# =========================================================================
# TASK FUNCTIONS — Parallel data gathering
# =========================================================================

@task(name="Gather Source A")
def gather_source_a(case_context: Dict[str, Any]) -> list:
    """Gather events from source A (e.g., control_plane_agent.log).

    TODO: Implement data gathering for your first source.
    """
    logger = get_run_logger()
    events = []

    try:
        # TODO: Replace with your log file and parsing logic
        # logs = get_logs("control_plane_agent.log", case_context)
        # for entry in logs:
        #     event = parse_source_a_event(entry)
        #     if event:
        #         event["source"] = "source_a"
        #         events.append(event)
        logger.info(f"Source A: gathered {len(events)} events")
    except Exception as e:
        logger.error(f"Source A gathering failed: {e}")

    return events


@task(name="Gather Source B")
def gather_source_b(case_context: Dict[str, Any]) -> list:
    """Gather events from source B (e.g., system commands).

    TODO: Implement data gathering for your second source.
    """
    logger = get_run_logger()
    events = []

    try:
        # TODO: Replace with your command parsing logic
        # raw_commands = get_commands(case_context)
        # command_outputs = {e.command: e.output for e in raw_commands}
        # events = parse_command_events(command_outputs)
        # for e in events:
        #     e["source"] = "source_b"
        logger.info(f"Source B: gathered {len(events)} events")
    except Exception as e:
        logger.error(f"Source B gathering failed: {e}")

    return events


@task(name="Gather Source C")
def gather_source_c(case_context: Dict[str, Any]) -> list:
    """Gather events from source C (e.g., diagnostic log files).

    TODO: Implement data gathering for your third source.
    """
    logger = get_run_logger()
    events = []

    try:
        # TODO: Replace with your log file and parsing logic
        # logs = get_logs("show_log_system.txt", case_context)
        # for entry in logs:
        #     event = parse_source_c_event(entry)
        #     if event:
        #         event["source"] = "source_c"
        #         events.append(event)
        logger.info(f"Source C: gathered {len(events)} events")
    except Exception as e:
        logger.error(f"Source C gathering failed: {e}")

    return events


# =========================================================================
# HELPER FUNCTIONS
# =========================================================================

def deduplicate_events(events: list, time_tolerance_seconds: int = 2) -> list:
    """Deduplicate events from multiple sources.

    Events are considered duplicates if they have the same type and
    occur within the time tolerance window.

    TODO: Customize deduplication logic for your event types.

    Args:
        events: Sorted list of event dicts.
        time_tolerance_seconds: Max time difference for duplicates.

    Returns:
        Deduplicated list of events.
    """
    if not events:
        return events

    deduped = [events[0]]
    for event in events[1:]:
        prev = deduped[-1]
        # TODO: Customize duplicate detection criteria
        is_dup = (
            event.get("type") == prev.get("type")
            and event.get("entity") == prev.get("entity")
            and abs_time_diff(event.get("timestamp", ""),
                              prev.get("timestamp", "")) <= time_tolerance_seconds
        )
        if not is_dup:
            deduped.append(event)

    return deduped


def abs_time_diff(ts1: str, ts2: str) -> float:
    """Calculate absolute time difference in seconds between two timestamps."""
    try:
        fmt = "%Y-%m-%d %H:%M:%S"
        t1 = datetime.strptime(ts1[:19], fmt)
        t2 = datetime.strptime(ts2[:19], fmt)
        return abs((t1 - t2).total_seconds())
    except (ValueError, TypeError):
        return float("inf")


def correlate_across_sources(
    events_type_a: list,
    events_type_b: list,
    window_minutes: int = 5,
) -> list:
    """Correlate events of type A with events of type B.

    TODO: Customize correlation logic for your event types.

    Args:
        events_type_a: Primary events to correlate.
        events_type_b: Secondary events to check for correlation.
        window_minutes: Time window for correlation.

    Returns:
        List of correlation finding dicts.
    """
    correlations = []
    window_seconds = window_minutes * 60

    for event_a in events_type_a:
        related = []
        for event_b in events_type_b:
            diff = abs_time_diff(
                event_a.get("timestamp", ""),
                event_b.get("timestamp", ""),
            )
            if diff <= window_seconds:
                related.append(event_b)

        if related:
            correlations.append({
                "type": "issue",
                "severity": "warning",
                "description": (
                    f"Event '{event_a.get('type')}' at {event_a.get('timestamp')} "
                    f"correlated with {len(related)} events from other sources"
                ),
                "affected_component": event_a.get("entity", "Unknown"),
                "detection_method": "Cross-source time-window correlation",
            })

    return correlations


# =========================================================================
# MAIN WORKFLOW
# =========================================================================

@workflow_tool(
    name="TODO:workflow_name",  # TODO: e.g., "ha:multi_source_analysis"
    description="TODO: Describe the multi-source correlation analysis",
    requires=[],
    tags=["TODO", "correlation"],
    tsf_data={
        "commands": [
            "show system info",
            # TODO: Add commands for source B
        ],
        "log_files": [
            # TODO: Add log files for sources A and C
        ],
    },
    keywords=["TODO", "correlation"],
)
@flow(name="TODO-workflow-slug")
def multi_source_correlation_workflow(
    tsf_id: Optional[str] = None,
    case_context: Optional[Dict[str, Any]] = None,
    case_identifier: Optional[str] = None,
    device_serial: Optional[str] = None,
    **kwargs,
) -> Dict[str, Any]:
    """TODO: Describe the multi-source correlation workflow."""
    logger = get_run_logger()
    logger.info(f"Starting multi-source correlation for TSF: {tsf_id}")

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

        # Step 1: Gather from all sources
        source_a_events = gather_source_a(case_context)
        source_b_events = gather_source_b(case_context)
        source_c_events = gather_source_c(case_context)

        source_counts = {
            "source_a": len(source_a_events),
            "source_b": len(source_b_events),
            "source_c": len(source_c_events),
        }
        analysis_data["source_counts"] = source_counts
        logger.info(f"Source counts: {source_counts}")

        # Step 2: Merge and sort all events
        all_events = source_a_events + source_b_events + source_c_events
        all_events.sort(key=lambda x: x.get("timestamp", ""))

        # Step 3: Deduplicate across sources
        deduped = deduplicate_events(all_events)
        analysis_data["total_events"] = len(all_events)
        analysis_data["deduped_events"] = len(deduped)
        logger.info(f"Events: {len(all_events)} total, {len(deduped)} after dedup")

        # Step 4: Correlate across event types
        # TODO: Split events by type and correlate
        # type_a_events = [e for e in deduped if e.get("type") == "type_a"]
        # type_b_events = [e for e in deduped if e.get("type") == "type_b"]
        # correlations = correlate_across_sources(type_a_events, type_b_events)
        # findings.extend(correlations)

        # Step 5: Build observation
        observation = []
        if findings or deduped:
            obs_md = "## Multi-Source Correlation Results\n\n"
            obs_md += "### Data Sources\n\n"
            for src, count in source_counts.items():
                obs_md += f"- **{src}:** {count} events\n"
            obs_md += f"\n**Total unique events:** {len(deduped)}\n\n"
            if findings:
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
