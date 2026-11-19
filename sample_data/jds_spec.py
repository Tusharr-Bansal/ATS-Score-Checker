"""Synthetic job descriptions: J01-J10 tech, J11-J20 non-tech, J21-J23 held-out domains.

Several roles are deliberately close neighbours (Java vs Python backend,
Data Scientist vs ML Engineer vs NLP Engineer, Data Engineer vs Data Analyst,
Frontend vs Full-stack, MLOps vs DevOps) so the ranking has to separate them
on substance, not on generic tech keywords.
"""

JDS = {
    "J01": {
        "file": "J01_java_backend_engineer.txt",
        "text": """Senior Backend Engineer (Java)
Company: Northwind Payments (fictional)  |  Location: Bengaluru / Hybrid

About the role
We are looking for a backend engineer to design and build high-throughput payment microservices.
You will own services end to end, from API design to production monitoring.

Responsibilities
- Design, build and maintain RESTful microservices in Java using Spring Boot
- Model data and write efficient queries on PostgreSQL
- Build event-driven integrations with Apache Kafka
- Containerise services with Docker and support deployments
- Write unit and integration tests (JUnit, Mockito) and take part in code reviews

Requirements
- 4+ years of professional backend development experience
- Strong Java (Java 11+) and Spring Boot / Spring framework
- Microservices architecture and REST API design
- SQL and relational databases (PostgreSQL or MySQL)
- Apache Kafka or similar message broker
- Docker
- Bachelor's degree in Computer Science or a related field

Nice to have
- Kubernetes
- AWS
- Redis caching
- Experience in fintech / payments
""",
    },
    "J02": {
        "file": "J02_python_backend_engineer.txt",
        "text": """Backend Engineer (Python)
Company: Brightleaf Health (fictional)  |  Location: Remote (India)

We build APIs that power a telehealth platform used by thousands of clinics.

What you will do
- Build and scale REST APIs with Python using FastAPI and Django
- Design PostgreSQL schemas and optimise queries
- Implement background jobs with Celery and Redis
- Ship services in Docker containers through CI pipelines
- Collaborate with frontend and product teams on API contracts

What we need
- 3+ years building backend services in Python
- FastAPI or Django (Django REST Framework)
- REST API design
- PostgreSQL / SQL
- Redis and Celery (or another task queue)
- Docker
- Bachelor's degree in Computer Science, IT or equivalent

Good to have
- AWS
- Kubernetes
- GraphQL
- Healthcare domain exposure
""",
    },
    "J03": {
        "file": "J03_data_scientist.txt",
        "text": """Data Scientist
Company: Meridian Retail Analytics (fictional)  |  Location: Gurugram

The team builds models for demand forecasting, customer churn and pricing.

Responsibilities
- Explore large datasets and build predictive models (classification, regression, forecasting)
- Design and analyse A/B tests and experiments with sound statistical methods
- Engineer features using Python, pandas and SQL
- Communicate findings to business stakeholders with clear visualisations
- Work with engineers to move models towards production

Requirements
- 3+ years of experience in data science or applied machine learning
- Python, pandas, NumPy, scikit-learn
- Strong statistics and hypothesis testing
- Machine learning (supervised learning, model evaluation)
- SQL
- Data visualisation (Matplotlib, Seaborn or similar)
- Master's degree in Statistics, Mathematics, Computer Science or another quantitative field

Preferred
- XGBoost / LightGBM
- Time-series forecasting
- Deep learning
- Tableau
""",
    },
    "J04": {
        "file": "J04_ml_engineer_mlops.txt",
        "text": """Machine Learning Engineer (MLOps)
Company: Quanta Vision Labs (fictional)  |  Location: Pune / Hybrid

You will take models from research notebooks to reliable production systems.

Responsibilities
- Build training and inference pipelines for deep learning models
- Package and deploy models as scalable services (Docker, Kubernetes)
- Track experiments and models with MLflow; set up model registry and monitoring
- Build CI/CD for ML (automated training, testing and deployment)
- Optimise model latency and cost on AWS (SageMaker, EC2, S3)

Requirements
- 3+ years in ML engineering or software engineering with ML deployment
- Python
- PyTorch or TensorFlow
- MLflow or similar experiment tracking
- Docker and Kubernetes
- CI/CD
- Model deployment / model serving
- AWS
- Bachelor's degree in Computer Science or Engineering

Nice to have
- Kubeflow
- Apache Airflow
- Feature stores
- ONNX / TensorRT model optimisation
""",
    },
    "J05": {
        "file": "J05_data_engineer.txt",
        "text": """Data Engineer
Company: Lattice Logistics (fictional)  |  Location: Hyderabad

Own the pipelines that move shipment data from operational systems into our warehouse.

Responsibilities
- Build batch and streaming ETL/ELT pipelines
- Develop Spark jobs to process terabytes of event data
- Orchestrate workflows with Apache Airflow
- Model data in the warehouse (Snowflake / BigQuery) and build dbt transformations
- Ensure data quality, lineage and monitoring

Requirements
- 3+ years of data engineering experience
- Python and SQL
- Apache Spark (PySpark)
- Apache Airflow
- Kafka or another streaming platform
- ETL / ELT pipeline design
- Data warehousing (Snowflake, BigQuery or Redshift)
- dbt
- Bachelor's degree in Computer Science or related field

Nice to have
- AWS (Glue, EMR, S3)
- Scala
- Databricks
""",
    },
    "J06": {
        "file": "J06_frontend_react_developer.txt",
        "text": """Frontend Developer (React)
Company: Pixelharbor Studio (fictional)  |  Location: Mumbai / Remote

Build fast, accessible web interfaces for a design-collaboration product.

Responsibilities
- Develop responsive UI components with React and TypeScript
- Manage application state with Redux
- Integrate REST APIs and handle loading/error states well
- Write unit tests with Jest and React Testing Library
- Work closely with designers to translate Figma designs into pixel-perfect pages

Requirements
- 2+ years of frontend development experience
- JavaScript (ES6+) and TypeScript
- React
- Redux or similar state management
- HTML5 and CSS3 (responsive design)
- REST API integration
- Jest / React Testing Library
- Bachelor's degree in Computer Science or equivalent practical experience

Nice to have
- Next.js
- Tailwind CSS
- Web accessibility (WCAG)
- Figma
""",
    },
    "J07": {
        "file": "J07_fullstack_mern_developer.txt",
        "text": """Full Stack Developer (MERN)
Company: Cartwheel Commerce (fictional)  |  Location: Jaipur

We are building a multi-vendor e-commerce platform and need someone comfortable across the stack.

What you will do
- Build backend APIs with Node.js and Express
- Design MongoDB collections and aggregation pipelines
- Build customer-facing features in React
- Implement authentication (JWT) and payment integrations
- Deploy and maintain services

Requirements
- 2+ years of full stack development
- JavaScript
- Node.js and Express.js
- MongoDB
- React
- REST APIs
- Git
- Bachelor's degree in Computer Science / IT

Nice to have
- TypeScript
- Docker
- AWS
- Redis
""",
    },
    "J08": {
        "file": "J08_devops_cloud_engineer.txt",
        "text": """DevOps / Cloud Engineer
Company: Stratus Cloudworks (fictional)  |  Location: Chennai / Hybrid

Own our cloud infrastructure and the delivery pipelines for 40+ services.

Responsibilities
- Provision and manage AWS infrastructure as code with Terraform
- Operate Kubernetes clusters (EKS) and Docker-based workloads
- Build and maintain CI/CD pipelines (Jenkins, GitHub Actions)
- Set up monitoring and alerting with Prometheus and Grafana
- Automate operations with Bash and Python scripting; harden Linux servers

Requirements
- 3+ years in DevOps, SRE or cloud engineering
- AWS
- Terraform
- Kubernetes
- Docker
- CI/CD (Jenkins or GitHub Actions)
- Linux administration
- Bash scripting
- Prometheus / Grafana
- Bachelor's degree in Computer Science, IT or related field

Nice to have
- Ansible
- Helm
- Python
- AWS certification
""",
    },
    "J09": {
        "file": "J09_nlp_genai_engineer.txt",
        "text": """NLP / Generative AI Engineer
Company: Lexicon AI (fictional)  |  Location: Bengaluru

Build LLM-powered products: document question answering, summarisation and agents.

Responsibilities
- Build retrieval-augmented generation (RAG) pipelines over enterprise documents
- Work with LLMs via APIs and open-source models (Hugging Face Transformers)
- Design embeddings, chunking strategies and vector search (FAISS, Pinecone, Chroma)
- Fine-tune transformer models for classification and extraction
- Build evaluation sets and measure answer quality and hallucination

Requirements
- 2+ years of experience in NLP or applied ML
- Python
- NLP fundamentals
- Hugging Face Transformers
- Large language models (LLMs) and prompt engineering
- RAG
- LangChain or LlamaIndex
- Vector databases
- PyTorch
- Bachelor's degree in Computer Science or related field

Nice to have
- Fine-tuning with LoRA / PEFT
- FastAPI
- LLM evaluation
- spaCy
""",
    },
    "J10": {
        "file": "J10_data_analyst.txt",
        "text": """Data Analyst
Company: Orchard Consumer Goods (fictional)  |  Location: Delhi NCR

Turn sales and marketing data into decisions for category managers.

Responsibilities
- Write SQL queries to pull and clean data from the warehouse
- Build and maintain dashboards in Power BI and Tableau
- Analyse sales trends, campaign performance and customer segments
- Prepare weekly business reports and present insights to stakeholders
- Support A/B test readouts with basic statistical analysis

Requirements
- 1+ years of experience as a data or business analyst
- SQL
- Advanced Excel (pivot tables, VLOOKUP)
- Power BI or Tableau
- Data visualisation and dashboarding
- Basic statistics
- Python (pandas) for analysis
- Bachelor's degree in any quantitative discipline (Statistics, Economics, Engineering, Commerce)

Nice to have
- A/B testing
- Stakeholder communication
- Google Analytics
""",
    },
}

JDS.update({
    "J11": {
        "file": "J11_digital_marketing_manager.txt",
        "text": """Digital Marketing Manager
Company: Saffron Skincare (fictional D2C brand)  |  Location: Mumbai

Own paid and organic growth for a fast-growing direct-to-consumer brand.

Responsibilities
- Plan and run performance campaigns on Google Ads and Meta Ads with a monthly budget of INR 50 lakh
- Own SEO strategy: keyword research, on-page optimisation and technical SEO audits
- Track funnels and attribution in Google Analytics 4; report CAC, ROAS and conversion rates
- Run email marketing and marketing automation journeys
- Lead a team of 3 marketers and coordinate with agencies

Requirements
- 4+ years of digital marketing experience, at least 2 in performance marketing
- Google Ads (Search, Shopping, Performance Max) and Meta Ads
- SEO and SEM
- Google Analytics 4
- Email marketing / marketing automation (Klaviyo, Mailchimp or HubSpot)
- Campaign budgeting and ROI analysis
- MBA in Marketing or Bachelor's degree in any discipline

Nice to have
- D2C / e-commerce experience
- A/B testing of landing pages
- Team leadership
""",
    },
    "J12": {
        "file": "J12_content_marketing_specialist.txt",
        "text": """Content Marketing Specialist
Company: Ledgerly (fictional B2B SaaS)  |  Location: Bengaluru / Remote

Create content that brings finance teams to our product.

Responsibilities
- Write blog posts, case studies, whitepapers and newsletters
- Own the editorial calendar and publish on WordPress
- Optimise articles for SEO and track organic traffic
- Repurpose content for LinkedIn and other social media channels
- Interview customers and subject-matter experts

Requirements
- 2+ years in content writing or content marketing
- Excellent English copywriting and editing
- SEO writing (keyword research, on-page SEO)
- WordPress or another CMS
- Social media marketing (LinkedIn)
- Bachelor's degree in English, Journalism, Mass Communication or Marketing

Nice to have
- B2B SaaS experience
- Canva
- Email newsletters
""",
    },
    "J13": {
        "file": "J13_sales_executive_b2b.txt",
        "text": """Sales Executive (B2B)
Company: Kraftpack Industries (fictional packaging manufacturer)  |  Location: Ahmedabad

Grow our customer base among FMCG and pharma manufacturers in Gujarat.

Responsibilities
- Generate leads through cold calling, field visits and referrals
- Meet procurement teams, present solutions and prepare quotations
- Negotiate pricing and close orders against a monthly sales target
- Maintain the pipeline and customer records in Salesforce CRM
- Collect payments and maintain relationships with existing accounts

Requirements
- 2+ years in B2B field sales
- Lead generation and cold calling
- Negotiation and closing skills
- CRM (Salesforce or Zoho CRM)
- Proven record of meeting sales targets
- Bachelor's degree in any discipline

Nice to have
- Industrial / packaging / manufacturing sales
- Gujarati language
- Two-wheeler and willingness to travel
""",
    },
    "J14": {
        "file": "J14_business_development_manager.txt",
        "text": """Business Development Manager
Company: Trellis Logistics Tech (fictional)  |  Location: Gurugram

Open new enterprise accounts and strategic partnerships for our logistics platform.

Responsibilities
- Identify target markets and enterprise accounts through market research
- Build strategic partnerships with 3PLs and marketplaces
- Prepare proposals, pricing and business cases; lead RFP responses
- Negotiate and close multi-year enterprise contracts
- Own the revenue pipeline and quarterly forecasts in HubSpot

Requirements
- 5+ years in business development or enterprise sales
- Enterprise / key account sales
- Strategic partnerships
- Market research and go-to-market strategy
- Proposal writing and RFP management
- Contract negotiation
- CRM (HubSpot or Salesforce) and sales forecasting
- MBA preferred

Nice to have
- Logistics or supply-chain industry experience
- Existing network with D2C brands
""",
    },
    "J15": {
        "file": "J15_hr_generalist.txt",
        "text": """HR Generalist
Company: Riverbend Hospitals (fictional)  |  Location: Pune

Run day-to-day HR operations for 1,200 employees across three hospitals.

Responsibilities
- Manage onboarding, exits and employee records in the HRMS
- Process monthly payroll inputs, attendance and leave
- Ensure compliance with labour laws (PF, ESI, gratuity, Shops & Establishments)
- Drive employee engagement programmes and resolve grievances
- Run the annual performance management cycle

Requirements
- 3+ years as an HR generalist or HR executive
- HR operations and employee lifecycle management
- Payroll processing
- Labour law compliance (PF, ESI)
- HRMS (Darwinbox, Keka or SAP SuccessFactors)
- Employee engagement and grievance handling
- Performance management
- MBA / PGDM in Human Resources

Nice to have
- Healthcare industry experience
- Advanced Excel
""",
    },
    "J16": {
        "file": "J16_talent_acquisition_specialist.txt",
        "text": """Talent Acquisition Specialist
Company: Northstar Consulting (fictional)  |  Location: Hyderabad / Hybrid

Hire 150+ consultants and corporate staff a year.

Responsibilities
- Run end-to-end recruitment: requisition, sourcing, screening, interviews and offers
- Source passive candidates on LinkedIn Recruiter, Naukri and through referrals
- Manage hiring pipelines in the applicant tracking system
- Partner with hiring managers on job descriptions and interview panels
- Drive employer branding and campus hiring

Requirements
- 2+ years in recruitment / talent acquisition
- End-to-end recruitment
- Candidate sourcing (LinkedIn Recruiter, Naukri, job boards)
- Applicant tracking systems (Greenhouse, Lever, Zoho Recruit)
- Screening and interviewing
- Offer negotiation
- Bachelor's degree; MBA in HR preferred

Nice to have
- Campus hiring
- Employer branding
- Recruitment analytics
""",
    },
    "J17": {
        "file": "J17_operations_manager.txt",
        "text": """Operations Manager
Company: Freshbasket (fictional grocery delivery)  |  Location: Bengaluru

Run warehouse and last-mile operations for 4 dark stores.

Responsibilities
- Manage daily warehouse operations: inbound, inventory, picking and dispatch
- Lead a team of 120 associates and 6 shift supervisors
- Design SOPs and drive process improvement using Lean / Six Sigma
- Manage vendors, 3PL partners and service-level agreements
- Track KPIs (order fill rate, delivery time, cost per order) and own the operating budget

Requirements
- 6+ years in operations, at least 3 in a people-management role
- Warehouse / supply-chain operations
- Inventory management
- Team leadership and workforce planning
- Process improvement (Lean / Six Sigma)
- Vendor management
- KPI tracking and budgeting
- Bachelor's degree; MBA in Operations preferred

Nice to have
- Six Sigma Green Belt
- Quick-commerce or e-commerce experience
- Advanced Excel
""",
    },
    "J18": {
        "file": "J18_project_manager.txt",
        "text": """Project Manager
Company: Clearview Infra Consultants (fictional)  |  Location: Delhi NCR

Deliver client projects on time, on budget and to scope.

Responsibilities
- Plan projects: scope, schedule (MS Project), resources and budget
- Run status meetings and report progress to client stakeholders
- Identify and manage risks, issues and change requests
- Coordinate cross-functional teams and subcontractors
- Close projects and capture lessons learned

Requirements
- 5+ years of project management experience
- Project planning and scheduling (MS Project or Primavera)
- Stakeholder management and client communication
- Risk management
- Budgeting and cost control
- Cross-functional team coordination
- PMP or PRINCE2 certification
- Bachelor's degree in Engineering or Management

Nice to have
- Agile / Scrum
- Infrastructure or construction projects
""",
    },
    "J19": {
        "file": "J19_accountant.txt",
        "text": """Accountant
Company: Mehra & Sons Textiles (fictional)  |  Location: Jaipur

Own the books for a mid-sized textile exporter.

Responsibilities
- Maintain books of accounts in Tally ERP / Tally Prime
- File GST returns and handle TDS deductions and returns
- Prepare monthly bank reconciliations and vendor ledgers
- Prepare financial statements and support the statutory audit
- Coordinate with auditors and tax consultants

Requirements
- 3+ years of accounting experience
- Tally ERP / Tally Prime
- GST filing and compliance
- TDS
- Bank reconciliation and accounts payable / receivable
- Financial statement preparation
- Audit support
- B.Com or M.Com; CA Inter is a plus

Nice to have
- Export documentation
- Advanced Excel
""",
    },
    "J20": {
        "file": "J20_financial_analyst.txt",
        "text": """Financial Analyst
Company: Brightpath Capital (fictional)  |  Location: Mumbai

Support the CFO office with planning, analysis and investment decisions.

Responsibilities
- Build and maintain financial models for budgeting and forecasting
- Run monthly variance analysis against budget and explain drivers
- Prepare valuation analyses (DCF, comparables) for investment proposals
- Build management dashboards and board presentations
- Analyse unit economics and profitability by business line

Requirements
- 2+ years in FP&A, corporate finance or equity research
- Financial modelling
- Budgeting and forecasting
- Variance analysis
- Valuation (DCF, comparable companies)
- Advanced Excel
- PowerPoint presentations
- MBA in Finance, CA or CFA

Nice to have
- Power BI or Tableau
- SQL
""",
    },
})

# ---------------------------------------------------------------------------------------------
# HELD-OUT domains: the skill taxonomy (backend/app/skills.py) deliberately knows NONE of this
# vocabulary, and the matching resumes describe the same skills in different words. This measures
# how the matcher behaves on a domain nobody prepared it for.
JDS.update({
    "J21": {
        "heldout": True,
        "file": "J21_phlebotomist.txt",
        "text": """Phlebotomist
Company: Sunrise Diagnostics (fictional)  |  Location: Jaipur

Collect high-quality blood specimens across our walk-in centre and home-collection service.

Responsibilities
- Perform venipuncture and capillary (finger-stick) collections for adults, children and elderly patients
- Follow the correct order of draw and tube additives for each test
- Verify patient identity and label specimens accurately at the point of collection
- Maintain infection control and dispose of sharps and biohazard waste safely
- Register samples in the Laboratory Information System (LIS) and maintain the cold chain during transport

Requirements
- 1+ years of phlebotomy experience
- Venipuncture
- Capillary / finger-stick collection
- Order of draw
- Patient identification and specimen labelling
- Infection control and biohazard waste disposal
- Laboratory Information System (LIS)
- DMLT or B.Sc. in Medical Laboratory Technology

Nice to have
- Paediatric collections
- Home sample collection experience
""",
    },
    "J22": {
        "heldout": True,
        "file": "J22_pastry_chef.txt",
        "text": """Pastry Chef
Company: Maison Amande Patisserie (fictional)  |  Location: Bengaluru

Lead the pastry section of an all-day French cafe and our wedding-cake orders.

Responsibilities
- Produce viennoiserie daily using laminated doughs
- Temper chocolate for bonbons, decorations and showpieces
- Design and execute plated desserts for the dinner menu
- Cost recipes and control food cost for the pastry section
- Maintain food safety standards (FSSAI, HACCP) and train commis

Requirements
- 3+ years in a professional pastry kitchen
- Viennoiserie
- Laminated doughs
- Chocolate tempering
- Plated desserts
- Recipe costing / food cost control
- Food safety (HACCP / FSSAI)
- Diploma in Pastry Arts or Hotel Management

Nice to have
- Wedding / celebration cakes
- Sugar work
""",
    },
    "J23": {
        "heldout": True,
        "file": "J23_paralegal.txt",
        "text": """Paralegal
Company: Khanna Legal Associates (fictional)  |  Location: New Delhi

Support partners in commercial litigation before the Delhi High Court.

Responsibilities
- Conduct case-law research using legal databases
- Draft pleadings, affidavits and applications for partner review
- Prepare and file documents through the court e-filing system
- Maintain the litigation calendar and track hearing dates and limitation deadlines
- Organise case files and indexed paper books

Requirements
- 2+ years as a paralegal or legal assistant
- Legal research (SCC Online, Manupatra)
- Drafting pleadings and affidavits
- Court e-filing
- Docket and deadline management
- Case file management
- Bachelor's degree in Law (LL.B.) or a paralegal certificate

Nice to have
- Commercial litigation exposure
- Hindi drafting
""",
    },
})

# Neighbouring roles: a resume written for one is partially relevant to the other.
ADJACENT = {
    "J01": ["J02"],
    "J02": ["J01", "J07"],
    "J03": ["J04", "J09", "J10"],
    "J04": ["J03", "J08", "J09"],
    "J05": ["J10", "J03"],
    "J06": ["J07"],
    "J07": ["J06", "J02"],
    "J08": ["J04"],
    "J09": ["J03", "J04"],
    "J10": ["J03", "J05", "J20"],
    # non-tech roles, also in near-neighbour pairs
    "J11": ["J12"],
    "J12": ["J11"],
    "J13": ["J14"],
    "J14": ["J13"],
    "J15": ["J16"],
    "J16": ["J15"],
    "J17": ["J18"],
    "J18": ["J17"],
    "J19": ["J20"],
    "J20": ["J19", "J10"],
    "J21": [], "J22": [], "J23": [],   # held-out; related distractors are marked per resume
}
