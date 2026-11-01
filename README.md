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

The interactive landing page introduces PhantomLink through an immersive, cybersecurity-inspired visual experience.

### Investigation Lab
![Investigation Lab](docs/screenshots/02-investigation.png)

The main investigation workspace allows users to submit URLs, review risk assessments, and explore explainable security findings.

### Evidence Intelligence
![Evidence Intelligence](docs/screenshots/03-evidence.png)

This page presents investigation evidence, supporting indicators, and detailed analysis to help users understand observed URL characteristics.

### DNS Intelligence
![DNS Intelligence](docs/screenshots/04-dns.png)

Displays DNS-related information and investigation insights to provide additional context about analyzed domains.

### Investigation Archive
![Investigation Archive](docs/screenshots/05-archive.png)

Provides access to historical investigation records with session-based separation of user data.

### Analytics Dashboard
![Analytics Dashboard](docs/screenshots/06-analytics.png)

Visualizes investigation statistics and risk-related summaries through an interactive analytics interface.

## Risk Classification Testing

The screenshots below show actual outputs from local URL
investigations. These classifications are heuristic results,
not verified phishing verdicts.

### LOW RISK

Demonstrates a URL investigation with few or no suspicious heuristic indicators. A LOW RISK result does not guarantee website safety.

![LOW RISK - Part 1](docs/screenshots/testing/low-01.png)

![LOW RISK - Part 2](docs/screenshots/testing/low-02.png)

![LOW RISK - Part 3](docs/screenshots/testing/low-03.png)

### MEDIUM RISK

Demonstrates an investigation where multiple observable risk indicators warrant further review. The classification is based on heuristic rules.

![MEDIUM RISK - Part 1](docs/screenshots/testing/medium-01.png)

![MEDIUM RISK - Part 2](docs/screenshots/testing/medium-02.png)

![MEDIUM RISK - Part 3](docs/screenshots/testing/medium-03.png)

![MEDIUM RISK - Part 4](docs/screenshots/testing/medium-04.png)

### HIGH RISK

Demonstrates an investigation with stronger or accumulated heuristic indicators. This classification does not independently confirm phishing.

![HIGH RISK - Part 1](docs/screenshots/testing/high-01.png)

![HIGH RISK - Part 2](docs/screenshots/testing/high-02.png)

![HIGH RISK - Part 3](docs/screenshots/testing/high-03.png)

![HIGH RISK - Part 4](docs/screenshots/testing/high-04.png)

## Testing and Evaluation

- Backend: **242 Pytest tests passed**.
- Security test file: **20 tests passed** (included in the 242).
- Real URL evaluation: 100 samples (50 phishing-labeled URLs and 50 legitimate candidates), all classified LOW RISK.
- Among them, 10 phishing-labeled dataset samples were classified LOW RISK.
- These findings highlight the limitations of the V1 heuristic engine.

[Full real URL evaluation](docs/testing/real_url_evaluation.md)

<!-- PHANTOMLINK GALLERY END -->



### 100 Real URL Evaluation

PhantomLink V1 was evaluated offline using 100 real URL samples: 50 phishing-labeled URLs from OpenPhish and 50 legitimate candidates from Tranco.

| Risk Level | Number of URLs |
|---|---:|
| LOW RISK | 100 |
| MEDIUM RISK | 0 |
| HIGH RISK | 0 |

All 100 URLs were processed without execution errors. However, all 50 phishing-labeled samples were classified LOW RISK, demonstrating a limitation of the current heuristic detection engine.

**Important:** Dataset labels were not independently reverified. This evaluation does not establish the current safety of the URLs.

[View Full 100-URL Evaluation](docs/testing/real_url_evaluation_100.md)

<!-- CLASSIFICATION TESTS START -->

## Extended Risk Classification Testing

PhantomLink V1 was tested through additional offline heuristic scenarios using multiple real domains and deliberately constructed URL paths.

### Medium Risk Demonstration

- Total scenarios: **68**
- LOW: **0**
- MEDIUM: **68**
- HIGH: **0**
- Errors: **0**

[View Medium Risk Test Results](docs/testing/medium_risk_68_scenarios.csv)

### High Risk Demonstration

- Total scenarios: **87**
- LOW: **0**
- MEDIUM: **0**
- HIGH: **87**
- Errors: **0**

[View High Risk Test Results](docs/testing/high_risk_87_scenarios.csv)

### Real-World Dataset Evaluation

A separate evaluation used 100 dataset URLs: 50 phishing-labeled OpenPhish samples and 50 Tranco legitimate candidates.

All 100 samples were classified LOW RISK. This demonstrates a limitation of the current V1 heuristic detector.

[View 100 Real URL Evaluation](docs/testing/real_url_evaluation_100.md)

**Important:** Synthetic classification demonstrations are not measurements of real-world phishing detection accuracy. No target websites were visited during these offline tests.

<!-- CLASSIFICATION TESTS END -->
