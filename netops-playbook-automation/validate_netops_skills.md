# Validating Agentic Systems in Network Operations

This is the most critical question you can ask when building Agentic systems. Relying on "learning on the job" (trial and error in production) with AI agents that have CLI access to network infrastructure is a recipe for a massive outage.

In traditional software, we have a testing pyramid (Unit -> Integration -> E2E). For AI agents, we need an **Evaluation Pipeline** (often called "Evals") that accounts for the non-deterministic nature of LLMs. 

Here is a comprehensive framework for validating your `netops-playbook-automation` skill and its generated workflows before they ever touch a live router.

---

## Level 1: Deterministic CI/CD (The Foundation)
Before worrying about the AI's reasoning, you must validate the structure of what it generates. You can automate this entirely in GitHub Actions or GitLab CI.

* **Syntax & Linting:** Run the generated Python files through `flake8`, `black`, and `mypy`. If the agent hallucinated a Python syntax error or imported a library that doesn't exist, CI fails immediately.
* **The PII/PHI Scanner:** As we designed earlier, your `netops_pii_scanner.py` runs in the pipeline. If the agent hardcoded a real customer IP or API key, the build fails.
* **Unit Testing the Helpers:** The templates contain deterministic functions (like `parse_device_info` with regex). Write standard `pytest` fixtures for these. Pass mock `show version` outputs from Cisco, Juniper, and PAN-OS, and assert they parse correctly.

## Level 2: Agent Evals (LLM-as-a-Judge)
Because the agent's template selection and code generation are non-deterministic, standard unit tests won't catch logic failures. You need "Evals"—running the agent against a golden dataset and grading the output.

* **The Golden Dataset:** Create a JSON file with 20–50 mock playbook prompts.
  * **Prompt 1:** "Troubleshoot a BGP flap..." -> Expected: Template 2.
  * **Prompt 2:** "Check if the IPsec license is valid..." -> Expected: Template 6.
* **Assertion Evals:** Write a script that loops through the dataset, asks the agent to select a template, and strictly asserts: `assert selected_template == expected_template`.
* **LLM-as-a-Judge:** For the generated Python code, it's hard to use strict assertions. Instead, use a secondary LLM (with a low temperature/high strictness prompt) to grade the output:
  > * "Did the agent use the `diagnostic_context` parameter correctly?"
  > * "Did the agent wrap the execution in a `try/except` block?"
  > * "Score this generated code 1-10 on adherence to the netops standard."
* *Note: Tools like LangSmith, Braintrust, or Promptfoo are excellent for running these Evals in CI.*

## Level 3: The Emulated Sandbox (The "Danger Room")
This is where you validate the runtime behavior of the generated workflow. Instead of running the generated script against a production firewall, you run it against a digital twin.

* **Network Emulation:** Use tools like Containerlab or EVE-NG to spin up lightweight containerized router OS images (like Nokia SR Linux, Arista cEOS, or Juniper cRPD) in your CI pipeline.
* **The Test:** Deploy the agent's generated workflow against the Containerlab topology.
  * Did it successfully connect?
  * Did it parse the actual CLI output correctly?
  * If it was Template 9 (Remediation), did the configuration apply without throwing an error?

## Level 4: Configuration Linting & "Dry Runs"
If your agent is generating actual configuration changes (like in Template 9), you need to validate the intent of the config before it applies.

* **Batfish Integration:** Batfish is an open-source network validation tool. If your agent drafts a new ACL or route, feed that draft config into Batfish. Batfish will mathematically model the network and tell you, *"Warning: This ACL will drop all SSH traffic to the management subnet."*
* **The Terraform Pattern:** Enforce a strict "Dry Run" (`--check`) mode. The agent must first output a `.plan` or `.diff` file showing exactly what it intends to change, which can be routed to a human for a quick visual sign-off (Human-in-the-Loop).

---

By combining traditional CI (Syntax/PII) with LLM Evals (Template Accuracy) and Sandboxing (Containerlab), you build a highly resilient pipeline that catches hallucinations before they become outages.
