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

<!-- PHANTOMLINK GALLERY START -->

## Application Screenshots

### Digital Underworld
![Digital Underworld](docs/screenshots/01-home.png)

### Investigation Lab
![Investigation Lab](docs/screenshots/02-investigation.png)

### Evidence Intelligence
![Evidence Intelligence](docs/screenshots/03-evidence.png)

### DNS Intelligence
![DNS Intelligence](docs/screenshots/04-dns.png)

### Investigation Archive
![Investigation Archive](docs/screenshots/05-archive.png)

### Analytics Dashboard
![Analytics Dashboard](docs/screenshots/06-analytics.png)

## Risk Classification Testing

The screenshots below show actual outputs from local URL
investigations. These classifications are heuristic results,
not verified phishing verdicts.

### LOW RISK

![LOW RISK - Part 1](docs/screenshots/testing/low-01.png)

![LOW RISK - Part 2](docs/screenshots/testing/low-02.png)

![LOW RISK - Part 3](docs/screenshots/testing/low-03.png)

### MEDIUM RISK

![MEDIUM RISK - Part 1](docs/screenshots/testing/medium-01.png)

![MEDIUM RISK - Part 2](docs/screenshots/testing/medium-02.png)

![MEDIUM RISK - Part 3](docs/screenshots/testing/medium-03.png)

![MEDIUM RISK - Part 4](docs/screenshots/testing/medium-04.png)

### HIGH RISK

![HIGH RISK - Part 1](docs/screenshots/testing/high-01.png)

![HIGH RISK - Part 2](docs/screenshots/testing/high-02.png)

![HIGH RISK - Part 3](docs/screenshots/testing/high-03.png)

![HIGH RISK - Part 4](docs/screenshots/testing/high-04.png)

## Testing and Evaluation

- Backend: **242 Pytest tests passed**.
- Security test file: **20 tests passed** (included in the 242).
- Real URL evaluation: 15 samples, all classified LOW RISK.
- Among them, 10 phishing-labeled dataset samples were classified LOW RISK.
- These findings highlight the limitations of the V1 heuristic engine.

[Full real URL evaluation](docs/testing/real_url_evaluation.md)

<!-- PHANTOMLINK GALLERY END -->
