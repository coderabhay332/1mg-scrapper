Here is the consolidated Master Project Context Document. You can copy and paste this directly into your AI coding assistant (like Cursor, GitHub Copilot, or Claude) to give it the complete product, technical, and architectural context of MediSafe.

MediSafe: Master Project Context Document
1. Project Overview
Name: MediSafe
Tagline: India's first personalized medication safety companion.
Core Problem: Indian healthcare suffers from severe polypharmacy and fragmented prescriptions. Patients see multiple specialists who do not share records. Western tools (like Drugs.com) do not recognize Indian brand names (e.g., Dolo 650, Combiflam) or Indian dietary/Ayurvedic habits (e.g., Karela juice, Ashwagandha).
Core Solution: A localized safety layer between the patient and their medications. It cross-references a user's prescriptions (using Indian brand names) against each other, against their specific health profile, against Indian dietary habits, and against the CDSCO banned drugs list.
Primary Target User: Urban Indian caregivers aged 25–40 managing medications for their elderly parents.

2. Technical Stack
Frontend: React Native (iOS & Android cross-platform).

Backend: Node.js with Express.

Database: PostgreSQL (highly normalized relational structure).

Infrastructure & Deployment: AWS, containerized with Docker, reverse proxy via Nginx.

Offline Data ETL Pipeline: Python (Playwright for scraping, BeautifulSoup/Pandas for data transformation).

Future AI Integrations: LLM for Natural Language Processing (chat interface), AWS Textract / Google Cloud Vision for OCR prescription scanning.

3. Database Architecture (PostgreSQL Schema)
The system relies on a deterministic, pre-mapped database to ensure sub-50ms query times and zero hallucinations. It decouples local brand names from generic chemical compounds.

generics: The master list of chemical compounds (e.g., paracetamol, ibuprofen). Contains baseline pregnancy and severity data.

brands: The Indian market names (e.g., Combiflam, Augmentin 625).

brand_ingredients: Junction table mapping a single brand to its multiple generic compounds with respective strengths.

banned_combinations: Sourced from the official CDSCO gazette. Contains fixed-dose combinations prohibited in India (e.g., Metronidazole + Tetracycline).

food_interactions: The proprietary moat. Maps generic compounds to specific Indian foods and Ayurvedic remedies (e.g., Metformin + Karela juice).

4. Core System Logic & User Flow
Onboarding (The Baseline): User inputs their age, weight, gender, conditions, and current medications. The LLM acts as an intake nurse to ask 3-5 targeted clarifying questions (e.g., "Are you taking any Ayurvedic supplements daily?").

The Dashboard (Continuous Loop): Generates a daily "Eat This, Avoid That" matrix based on active medications.

The Intercept (Collision Detection): When a new drug is added, the Node.js backend executes a strict SQL relational query. It breaks the brand name down into generic components, cross-references them against the existing generic components in the user's profile, checks the food_interactions table, and checks the banned_combinations table.

The Alert: If a collision is detected, the system throws a deterministic, hardcoded warning (not generated dynamically by AI, to prevent liability/hallucinations).

5. Data Sourcing Strategy
The application does not perform live web scraping for user queries. All data is processed offline and seeded into the PostgreSQL database.

Brand mapping: Extracted via Python/Playwright ETL scripts from local pharmacy directories, or seeded via commercial APIs (e.g., HealthOS).

Clinical interactions: Sourced from OpenFDA / DrugBank APIs.

Banned list: Parsed from CDSCO PDF documents into CSV format and loaded into the DB.

Food/Ayurveda: Manually mapped by the medical co-founder and seeded via CSV.

6. Development Phases
Phase 1 (MVP): Core safety engine. Manual medication entry (no OCR), basic brand-to-generic resolution, deterministic interaction checking, and family profiles.

Phase 2 (Growth): Prescription photo upload (OCR), AI health chat (strictly bounded for informational use), expanded Hindi/regional language support, pregnancy-specific modules.

Phase 3 (Scale/B2B): Corporate wellness dashboards, white-labeled pharmacy integrations, API products for clinics.

7. Regulatory & Liability Guardrails
Classification: Built strictly as an "information and awareness tool" to comply with CDSCO guidelines (avoids medical device classification).

Data Privacy: Built for upcoming DISHA compliance (encrypted, locally stored in India, no third-party sharing).

Disclaimers: Every output directs users to consult their physician. AI is restricted to formatting and NLP; all medical collision logic remains deterministic.