"""
app.py - Digital Investigation Console for AI Mystery Detective Team
"""

import os
import gradio as gr
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import agents
import case_data

def execute_investigation(case_mode):
    include_evidence_e = (case_mode == "1. Original Case Facts (With Evidence E)")
    
    if include_evidence_e:
        run_mode_info = "🟢 **CURRENT RUN:** Original Case Facts (Evidence E Included)"
    else:
        run_mode_info = "🟠 **SECOND RUN:** Modified Case Facts — Evidence E (Blue Velvet Fibers) REMOVED"

    try:
        results = agents.run_investigation(include_evidence_e=include_evidence_e)
        
        status = results.get("status", "INCOMPLETE")
        status_msg = results.get("status_message", "Investigation incomplete.")
        
        detective_report = results.get("detective", "Waiting for investigation run...")
        evidence_report = results.get("evidence", "Waiting for investigation run...")
        suspect_report = results.get("suspect", "Waiting for investigation run...")
        skeptic_report = results.get("skeptic", "Waiting for investigation run...")
        chief_report = results.get("chief", "Chief Verdict Unavailable — Investigation incomplete.")

        if status == "COMPLETED":
            status_banner_md = (
                f"{run_mode_info}\n\n"
                "### ✅ INVESTIGATION COMPLETE\n"
                "All 5 specialists completed successfully."
            )
        else:
            status_banner_md = (
                f"{run_mode_info}\n\n"
                "### ⚠️ INVESTIGATION INCOMPLETE\n"
                f"{status_msg}"
            )
            # NEVER display Chief report as a valid final verdict when status != "COMPLETED"
            chief_report = f"🛑 **Chief Verdict Unavailable — Investigation incomplete.**\n\n*{status_msg}*"

        return (
            status_banner_md,
            detective_report,
            evidence_report,
            suspect_report,
            skeptic_report,
            chief_report
        )
    except Exception as e:
        err_str = str(e)
        if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "quota" in err_str.lower():
            error_msg = "Gemini API quota exhausted for this project (429 RESOURCE_EXHAUSTED). The application and key configuration are working, but the model quota is currently unavailable."
        else:
            error_msg = f"Error Running Investigation:\n`{err_str}`\n\nPlease check your configuration and environment."
        
        formatted_error = f"### ⚠️ System Status Alert\n\n{error_msg}"
        status_banner_md = (
            f"{run_mode_info}\n\n"
            "### ⚠️ INVESTIGATION INCOMPLETE\n"
            f"{error_msg}"
        )
        chief_unavailable = "🛑 **Chief Verdict Unavailable — Investigation incomplete.**"
        return status_banner_md, formatted_error, formatted_error, formatted_error, formatted_error, chief_unavailable



def handle_human_review(decision):
    if decision == "Accept":
        return "✅ **Verdict Accepted by Lead Investigator.** Case closed pending formal documentation."
    elif decision == "Revise":
        return "🔄 **Revision Requested.** Flagged for secondary analysis on suspect motives and timeline."
    elif decision == "Reject":
        return "❌ **Verdict Rejected.** Case returned to Detective Team for further evidence gathering."
    return "Awaiting Lead Investigator decision..."


# Custom CSS for dark investigation console theme
custom_css = """
body, .gradio-container {
    background-color: #0b0f19 !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
}

.main-header {
    text-align: center;
    margin-bottom: 16px;
}

.main-title {
    font-size: 2.2rem;
    font-weight: 800;
    letter-spacing: 1.5px;
    color: #f8fafc;
    margin: 0;
    text-transform: uppercase;
}

.main-subtitle {
    font-size: 1.25rem;
    font-weight: 600;
    color: #38bdf8;
    margin-top: 4px;
    margin-bottom: 2px;
}

.main-tagline {
    font-size: 0.95rem;
    color: #94a3b8;
    font-style: italic;
    margin-bottom: 12px;
}

.status-badge {
    display: inline-block;
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 20px;
    padding: 6px 18px;
    font-family: monospace;
    font-size: 0.85rem;
    color: #f59e0b;
    letter-spacing: 0.5px;
}

.pipeline-banner {
    background-color: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 8px;
    padding: 12px 16px;
    text-align: center;
    font-size: 0.95rem;
    font-weight: 600;
    color: #cbd5e1;
    margin: 16px 0 20px 0;
}

.pipeline-step {
    color: #38bdf8;
}

.pipeline-arrow {
    color: #64748b;
    margin: 0 6px;
}

.pipeline-chief {
    color: #f59e0b;
    font-weight: 700;
}

.pipeline-human {
    color: #10b981;
    font-weight: 700;
}

.console-card {
    background-color: #0f172a !important;
    border: 1px solid #1e293b !important;
    border-radius: 8px !important;
    padding: 16px !important;
}

.chief-verdict-card {
    background-color: #141b2d !important;
    border: 2px solid #f59e0b !important;
    border-radius: 8px !important;
    padding: 20px !important;
    box-shadow: 0 4px 20px rgba(245, 158, 11, 0.12) !important;
}

.chief-badge {
    display: inline-block;
    background-color: #f59e0b22;
    border: 1px solid #f59e0b;
    color: #fbbf24;
    font-size: 0.8rem;
    font-weight: 700;
    padding: 2px 10px;
    border-radius: 4px;
    text-transform: uppercase;
    margin-bottom: 8px;
}

.timeline-box {
    background-color: #1e293b;
    border-left: 4px solid #38bdf8;
    padding: 12px 16px;
    margin: 10px 0;
    border-radius: 0 6px 6px 0;
}

.timeline-entry {
    margin-bottom: 6px;
    font-size: 0.9rem;
}

.timeline-time {
    color: #38bdf8;
    font-weight: 700;
    font-family: monospace;
}
"""

with gr.Blocks(title="AI Mystery Detective Team — Console") as demo:
    
    # TOP HEADER
    with gr.Column(elem_classes=["main-header"]):
        gr.HTML("""
            <div class="main-header">
                <div class="main-title">🕵️ AI MYSTERY DETECTIVE TEAM</div>
                <div class="main-subtitle">The Vanishing Aurora Diamond</div>
                <div class="main-tagline">One mystery • Five specialists • One accountable conclusion</div>
                <div class="status-badge">Case 001 | Lead Investigator POV | Gemini 3.6 Flash • Low Thinking</div>
            </div>
        """)

    # INVESTIGATION PIPELINE VISUAL
    gr.HTML("""
        <div class="pipeline-banner">
            <span>INVESTIGATION PIPELINE:</span>
            <span class="pipeline-arrow">&nbsp;&nbsp;</span>
            <span class="pipeline-step">1 Detective</span>
            <span class="pipeline-arrow">➔</span>
            <span class="pipeline-step">2 Evidence</span>
            <span class="pipeline-arrow">➔</span>
            <span class="pipeline-step">3 Suspect</span>
            <span class="pipeline-arrow">➔</span>
            <span class="pipeline-step">4 Skeptic</span>
            <span class="pipeline-arrow">➔</span>
            <span class="pipeline-chief">5 Chief</span>
            <span class="pipeline-arrow">➔</span>
            <span class="pipeline-human">Human Review</span>
        </div>
    """)

    # CASE CONTROL AREA & CASE BRIEF
    with gr.Row():
        with gr.Column(scale=1, elem_classes=["console-card"]):
            gr.Markdown("### 🎛️ Case Control Panel")
            case_mode = gr.Radio(
                choices=[
                    "1. Original Case Facts (With Evidence E)",
                    "2. Second Run: Remove Evidence E (Blue Velvet Fibers)"
                ],
                value="1. Original Case Facts (With Evidence E)",
                label="Investigation Mode"
            )
            run_btn = gr.Button("🔍 Run Investigation", variant="primary", scale=1)

        with gr.Column(scale=1, elem_classes=["console-card"]):
            with gr.Accordion("📜 Case Briefing & Key Timeline (Click to expand)", open=True):
                gr.HTML("""
                    <div class="timeline-box">
                        <div class="timeline-entry"><span class="timeline-time">8:00 PM</span> — Diamond confirmed in locked display case</div>
                        <div class="timeline-entry"><span class="timeline-time">8:20–8:24 PM</span> — Power failure / gallery blackout</div>
                        <div class="timeline-entry"><span class="timeline-time">8:23 PM</span> — Arjun's access card opens display case</div>
                        <div class="timeline-entry"><span class="timeline-time">8:25 PM</span> — Arjun leaves archive carrying catalogue folder</div>
                        <div class="timeline-entry"><span class="timeline-time">8:30 PM</span> — Diamond discovered missing</div>
                    </div>
                """)
                with gr.Accordion("Full Authoritative Case Details", open=False):
                    gr.Markdown(case_data.get_formatted_case_data(include_evidence_e=True))

    # CURRENT RUN STATUS INDICATOR
    run_mode_banner = gr.Markdown("🟢 **CURRENT RUN:** Original Case Facts (Evidence E Included)")

    # REPORT AREA — FIVE AGENT CARDS IN INVESTIGATION ORDER
    with gr.Tabs():
        with gr.TabItem("🔎 1. Detective — Timeline & Facts"):
            with gr.Column(elem_classes=["console-card"]):
                gr.Markdown("### 🔍 Specialist 1: Detective Agent")
                gr.Markdown("*Focus: Timeline reconstruction, fact verification, and critical time window analysis.*")
                detective_output = gr.Markdown("Waiting for investigation run...")

        with gr.TabItem("🧪 2. Evidence — Evidence Analysis"):
            with gr.Column(elem_classes=["console-card"]):
                gr.Markdown("### 🧪 Specialist 2: Evidence Evaluator")
                gr.Markdown("*Focus: Technical analysis of Evidence items A through G.*")
                evidence_output = gr.Markdown("Waiting for investigation run...")

        with gr.TabItem("👥 3. Suspect — Suspect Comparison"):
            with gr.Column(elem_classes=["console-card"]):
                gr.Markdown("### 👥 Specialist 3: Suspect Profiler")
                gr.Markdown("*Focus: Motive, opportunity, statements, and timeline alignment across all 4 suspects.*")
                suspect_output = gr.Markdown("Waiting for investigation run...")

        with gr.TabItem("🤔 4. Skeptic — Challenge & Alternatives"):
            with gr.Column(elem_classes=["console-card"]):
                gr.Markdown("### 🤔 Specialist 4: Skeptic Agent")
                gr.Markdown("*Focus: Stress-testing assumptions, exploring counter-hypotheses and framing risks.*")
                skeptic_output = gr.Markdown("Waiting for investigation run...")

        with gr.TabItem("👨‍✈️ 5. Chief — Final Verdict"):
            with gr.Column(elem_classes=["chief-verdict-card"]):
                gr.HTML('<div class="chief-badge">Accountable Conclusion</div>')
                gr.Markdown("## 👨‍✈️ Specialist 5: Chief Investigator Verdict")
                gr.Markdown("Synthesis across all 4 specialist reports into a single actionable verdict.")
                
                gr.Markdown("""
                ---
                #### Verdict Structure Guide:
                - **Most Likely Suspect / Explanation**
                - **Confidence Level**
                - **Strongest Supporting Evidence**
                - **Key Weakness in Primary Theory**
                - **Best Alternative Explanation**
                - **Critical Missing Evidence**
                - **Human Review Recommendation**
                ---
                """)
                
                chief_output = gr.Markdown("Click **Run Investigation** to generate final verdict.")
                
                gr.Markdown("### 🧑‍⚖️ Human Review Control")
                with gr.Row():
                    review_input = gr.Radio(
                        choices=["Select a decision", "Accept", "Revise", "Reject"],
                        value="Select a decision",
                        label="Lead Investigator Action"
                    )
                    review_btn = gr.Button("Submit Human Decision", variant="secondary")
                
                review_status = gr.Markdown("Awaiting Lead Investigator decision...")
                
                review_btn.click(
                    fn=handle_human_review,
                    inputs=[review_input],
                    outputs=[review_status]
                )

    # EVENT BINDING
    run_btn.click(
        fn=execute_investigation,
        inputs=[case_mode],
        outputs=[
            run_mode_banner,
            detective_output,
            evidence_output,
            suspect_output,
            skeptic_output,
            chief_output
        ]
    )

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860, share=False, css=custom_css, theme=gr.themes.Base())



