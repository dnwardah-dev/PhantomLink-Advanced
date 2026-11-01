<WritingBlock id="58321" variant="document"># PhantomLink V5 — Advanced Interactive Scam Investigator

An interactive cybersecurity investigation platform designed to analyze suspicious URLs, identify observable risk indicators, and explain investigation findings through an immersive visual interface.
Overview
PhantomLink combines secure URL validation, heuristic risk analysis, DNS intelligence, and evidence traceability to help users investigate potentially suspicious links.

Rather than providing only a safe-or-dangerous result, it explains observable indicators, supporting evidence, and analysis limitations.

Disclaimer: PhantomLink is an educational cybersecurity portfolio project. Its heuristic findings are not definitive phishing verdicts.
Key Features
- URL Investigation and Risk Assessment
- Secure URL Validation and SSRF Protection
- DNS Intelligence
- Evidence Traceability
- Interactive URL Evidence Highlighter
- Session-Based Investigation Archive
- Investigation Analytics Dashboard
- JSON and PDF Report Export
- Digital Underworld Interactive Interface
Tech Stack
Layer	Technologies
Frontend	React, Vite, JavaScript, CSS
Backend	Python, FastAPI
Database	SQLite
Testing	Pytest, Vitest, Playwright
Security	URL Validation, SSRF Protections, Session Isolation

Project Structure
- backend/ — FastAPI application, detection engine, datasets, and automated tests.
- frontend/ — React application, UI components, and end-to-end tests.
- README.md — Main project documentation.
Investigation Workflow
1. Submit a URL for investigation.
2. Validate the input against security restrictions.
3. Identify structural and heuristic indicators.
4. Generate explainable risk assessment results.
5. Explore supporting evidence and DNS information.
6. Review findings and export investigation reports.
Security Considerations
PhantomLink applies defensive input validation, private-network restrictions, and session-based investigation isolation.

The results should be interpreted as supporting evidence, not conclusive security judgments.
Development Status
Local cybersecurity portfolio prototype.
Author
Developed as a full-stack cybersecurity engineering portfolio project.</WritingBlock>