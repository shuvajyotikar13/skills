"""
Template 3: AI/LLM-Augmented Log Analysis Workflow
====================================================
Use LogWatch or direct LiteLLM API calls to analyze logs that are
too complex or voluminous for pure regex pattern matching.

Use this template when:
- Logs are unstructured or highly variable
- You need AI to identify patterns, anomalies, or correlations
- The playbook says "analyze logs for X" without specific patterns
- LogWatch clustering + AI analysis is appropriate

TODO markers indicate where to customize for your specific playbook.
"""

# NO IMPORTS NEEDED for SDK APIs - auto-injected at runtime
import os
import re
import tempfile


# =========================================================================
# MAIN WORKFLOW
# =========================================================================

@workflow_tool(
    name="TODO:workflow_name",  # TODO: e.g., "system:ai_log_analysis"
    description="TODO: Describe what this workflow analyzes with AI",
    requires=[],
    tags=["logwatch", "ai", "TODO"],
    tsf_data={
        "log_files": [
            # TODO: List the log files to analyze
            # "/var/log/device/system.log",
        ],
        "commands": ["show system info"],
    },
    keywords=["TODO", "ai", "logwatch"],
)
@flow(name="TODO-workflow-slug")
def ai_log_analysis_workflow(
    litellm_api_key: str = "",
    tsf_id: Optional[str] = None,
    case_context: Optional[Dict[str, Any]] = None,
    case_identifier: Optional[str] = None,
    device_serial: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    **kwargs,
) -> Dict[str, Any]:
    """TODO: Describe the workflow purpose.

    Uses LogWatch AI to analyze logs for [specific issue type].
    """
    logger = get_run_logger()
    logger.info(f"Starting AI log analysis for TSF: {tsf_id}")

    try:
        # Step 1: Setup LLM credentials
        if not litellm_api_key:
            litellm_api_key = os.getenv("LITELLM_API_KEY", "")
        if not litellm_api_key:
            return create_result(
                status="error",
                playbook_name="TODO_playbook_name",
                display_name="TODO Display Name",
                observation=[{"markdown": "## Error\n\nNo LiteLLM API key provided."}],
                findings=[],
            )

        os.environ["LITELLM_API_KEY"] = litellm_api_key
        os.environ["LITELLM_MODEL"] = os.getenv("LITELLM_MODEL", "anthropic/claude-sonnet-4-6")

        if not case_context:
            return create_result(
                status="warning",
                playbook_name="TODO_playbook_name",
                display_name="TODO Display Name",
                observation=[], findings=[],
            )

        # Step 2: Fetch logs via SDK API
        # TODO: Replace with your log file name and filters
        log_entries = get_logs(
            "system.log",  # TODO: your log file
            case_context,
            start_time=start_time,
            end_time=end_time,
        ) if case_context else []

        logger.info(f"Retrieved {len(log_entries)} log entries")

        if not log_entries:
            return create_result(
                status="warning",
                playbook_name="TODO_playbook_name",
                display_name="TODO Display Name",
                observation=[{"markdown": "## No Data\n\nNo log entries found."}],
                findings=[],
            )

        # Step 3: Convert LogEntry objects to temp file for LogWatch
        log_content = "\n".join(
            [e.log_message for e in log_entries if hasattr(e, "log_message")]
        )
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".log"
        ) as tf:
            tf.write(log_content)
            log_path = tf.name

        # Step 4: Run LogWatch AI analysis
        findings = []
        analysis_text = ""

        try:
            from logwatch_agent import LogWatch

            # TODO: Customize the analysis prompt for your use case
            analysis_prompt = (
                "Analyze these logs for TODO: [describe what to look for]. "
                "Identify any errors, anomalies, or patterns. "
                "Provide a structured summary with timestamps."
            )

            config = {
                "connector_config": [
                    {"type": "generic", "config": {"file_path": log_path}}
                ],
                "logwatch_config": {
                    "llm_provider": "litellm",
                    "max_tokens": 2000,
                    "input_token_limit": 50000,
                    "request_timeout": 60,
                    "prompt_config": {
                        "prompt": analysis_prompt,
                        "include_data": True,
                        "include_clusters": True,
                        "include_anomalies": True,
                        "max_clusters": 10,
                        "max_anomalies": 5,
                    },
                    "clustering": {
                        "clustering_level": "basic",
                        "max_sample_logs": 2,
                        "max_log_line_size": 100,
                    },
                },
            }

            logwatch = LogWatch.create(config)
            result = logwatch.analyze()
            analysis_text = result.get("llm_analysis", "No analysis generated")

            # Extract findings from analysis
            if analysis_text and analysis_text != "No analysis generated":
                findings.append({
                    "type": "issue",
                    "severity": "warning",
                    "description": "AI analysis identified potential issues (see observation)",
                    "affected_component": "system.log",  # TODO: your log file
                    "detection_method": "LogWatch AI analysis",
                })

        except ImportError:
            logger.warning("LogWatch not available, skipping AI analysis")
            analysis_text = "LogWatch library not available for AI analysis."
        except Exception as e:
            logger.error(f"LogWatch analysis failed: {e}")
            analysis_text = f"AI analysis failed: {e}"
        finally:
            # Clean up temp file
            try:
                os.unlink(log_path)
            except OSError:
                pass

        # Step 5: Build observation
        observation = []
        if analysis_text:
            obs_md = "## AI Log Analysis Results\n\n"
            obs_md += f"**Log entries analyzed:** {len(log_entries)}\n\n"
            obs_md += "### Analysis\n\n"
            obs_md += analysis_text
            observation = [{"markdown": obs_md}]

        status = "warning" if findings else "success"

        return create_result(
            status=status,
            playbook_name="TODO_playbook_name",
            display_name="TODO Display Name",
            observation=observation,
            findings=findings,
            analysis_data={
                "log_count": len(log_entries),
                "analysis_length": len(analysis_text),
            },
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
