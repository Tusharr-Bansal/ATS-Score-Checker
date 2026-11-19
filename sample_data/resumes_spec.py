"""Seventy synthetic resumes: three per job description (strong / mid / junior) for 20 JDs,
plus 10 off-domain distractors (role "NONE") that should score Weak against every JD.

All people, companies and contact details are fictional. Wording varies on
purpose (e.g. "Postgres", "k8s", "Spring framework", "sklearn", "ReactJS") so
exact keyword matching is not enough. Some resumes have no explicit skills
section and only mention skills inside experience bullets.
"""

R = []


def add(rid, role, level, name, location, summary, skills, experience, education,
        projects=(), certs=(), fmt="pdf", adjacent=()):
    R.append(dict(id=rid, role=role, level=level, name=name, adjacent=list(adjacent),
                  email=f"{name.lower().replace(' ', '.')}@example.com",
                  phone=f"+91-90000-{int(rid[1:]):05d}", location=location,
                  summary=summary, skills=skills, experience=experience,
                  education=education, projects=list(projects), certs=list(certs), fmt=fmt))


# ---------------------------------------------------------------- J01 Java backend
add("R01", "J01", "strong", "Arjun Mehta", "Bengaluru",
    "Backend engineer with 7 years building payment and banking microservices on the JVM.",
    ["Java 17", "Spring Boot", "Spring Cloud", "Hibernate/JPA", "PostgreSQL", "MySQL", "Apache Kafka",
     "Docker", "Kubernetes", "AWS", "Redis", "JUnit", "Mockito", "REST APIs", "Microservices"],
    [("Senior Software Engineer", "Ledgerline Fintech", "Mar 2021 - Present",
      ["Led a team of 4 building card-settlement microservices in Java/Spring Boot handling 2M txns/day",
       "Introduced Kafka-based event sourcing; cut reconciliation time by 60%",
       "Migrated services to Kubernetes on AWS EKS; added Redis caching for hot lookups"]),
     ("Software Engineer", "Corebank Systems", "Jul 2017 - Feb 2021",
      ["Built REST APIs for loan origination using Spring MVC and PostgreSQL",
       "Wrote JUnit/Mockito test suites raising coverage from 40% to 85%"])],
    [("B.Tech in Computer Science", "National Institute of Technology, Surathkal", "2013 - 2017")],
    projects=[("Open-source contribution", "Contributed connection-pool fixes to a Spring Data module")],
    certs=["Oracle Certified Professional: Java SE 11 Developer"])

add("R02", "J01", "mid", "Kavya Raman", "Chennai",
    "Java developer with ~4.5 years of experience in Spring-based enterprise services.",
    ["Java", "Spring framework", "Spring Boot", "Postgres", "Oracle SQL", "RabbitMQ", "Kafka",
     "Docker", "Jenkins", "Git", "JUnit"],
    [("Software Engineer II", "Tessellate Insurance Tech", "06/2022 - Present",
      ["Develop policy-management microservices in Spring Boot exposed as REST endpoints",
       "Replaced RabbitMQ point-to-point queues with Kafka topics for claims events",
       "Dockerised 6 legacy services and wrote Jenkins pipelines"]),
     ("Associate Software Engineer", "Bluepeak Consulting", "07/2020 - 05/2022",
      ["Maintained Java 8 batch jobs and Oracle stored procedures for a retail bank client"])],
    [("B.E. in Information Technology", "Anna University", "2016 - 2020")],
    fmt="docx")

add("R03", "J01", "junior", "Rohan Das", "Kolkata",
    "Junior backend developer, 1.5 years with Java and Spring Boot. Also comfortable with JavaScript on the frontend.",
    ["Java", "Spring Boot", "MySQL", "JavaScript", "HTML", "CSS", "Git"],
    [("Junior Software Developer", "Quickcart Solutions", "Apr 2025 - Present",
      ["Built CRUD REST APIs in Spring Boot with MySQL for an inventory module",
       "Fixed UI bugs in the JavaScript admin dashboard"]),
     ("Software Engineering Intern", "Quickcart Solutions", "Oct 2024 - Mar 2025",
      ["Wrote unit tests and documentation for internal APIs"])],
    [("B.Tech in Computer Science", "Heritage Institute of Technology", "2020 - 2024")],
    projects=[("Library Management System", "Spring Boot + MySQL app with JWT login")])

# ---------------------------------------------------------------- J02 Python backend
add("R04", "J02", "strong", "Sneha Kulkarni", "Pune",
    "Python backend engineer (6 years) focused on API platforms in healthcare and SaaS.",
    ["Python", "FastAPI", "Django", "Django REST Framework", "PostgreSQL", "SQLAlchemy", "Redis",
     "Celery", "Docker", "AWS (ECS, RDS, S3)", "GraphQL", "pytest", "Kubernetes"],
    [("Senior Backend Engineer", "Carewave Health", "Jan 2022 - Present",
      ["Built FastAPI services for appointment scheduling serving 3k clinics; p95 latency under 80 ms",
       "Designed PostgreSQL schemas and partitioning for 400M-row audit tables",
       "Moved async workloads to Celery + Redis; containerised with Docker and deployed on ECS"]),
     ("Backend Engineer", "Formstack Labs", "Aug 2019 - Dec 2021",
      ["Developed Django REST Framework APIs and a GraphQL gateway",
       "Wrote pytest suites and CI pipelines on GitHub Actions"]),
     ("Software Engineer", "Infowave", "Jun 2018 - Jul 2019",
      ["Python scripts and Flask microservices for data ingestion"])],
    [("B.Tech in Computer Engineering", "College of Engineering Pune", "2014 - 2018")],
    fmt="docx")

add("R05", "J02", "mid", "Imran Shaikh", "Hyderabad",
    "Backend developer with 3 years of Python/Django experience building REST APIs.",
    ["Python", "Django", "DRF", "Flask", "MySQL", "Postgres", "Redis", "Docker", "Git", "Linux"],
    [("Backend Developer", "Tickety Events", "Sep 2023 - Present",
      ["Build ticketing REST APIs in Django REST Framework backed by Postgres",
       "Implemented rate limiting and caching with Redis"]),
     ("Python Developer", "Softgrid Technologies", "Jun 2021 - Aug 2023",
      ["Developed Flask services and MySQL reporting queries",
       "Wrote Dockerfiles and docker-compose setups for local development"])],
    [("B.Sc. in Computer Science", "Osmania University", "2018 - 2021")],
    projects=[("Async task runner", "Small background-job runner using Python asyncio and Redis queues")])

add("R06", "J02", "junior", "Priya Nair", "Kochi",
    "Recent graduate with a 6-month Python backend internship. Built academic projects in Java too.",
    ["Python", "FastAPI", "SQLite", "Java", "C++", "Git"],
    [("Backend Intern", "Nimbus Edtech", "Jan 2026 - Jun 2026",
      ["Built FastAPI endpoints for quiz submissions with SQLite",
       "Wrote API documentation using OpenAPI"])],
    [("B.Tech in Computer Science", "Model Engineering College, Kochi", "2022 - 2026")],
    projects=[("Hostel complaint portal", "FastAPI + SQLite web app with JWT auth"),
              ("Bank simulator", "Java console application (OOP coursework)")],
    fmt="docx")

# ---------------------------------------------------------------- J03 Data scientist
add("R07", "J03", "strong", "Ananya Iyer", "Gurugram",
    "Data scientist with 6 years in retail and e-commerce analytics: forecasting, churn and experimentation.",
    ["Python", "pandas", "NumPy", "scikit-learn", "XGBoost", "LightGBM", "statsmodels", "Prophet",
     "SQL", "A/B testing", "Hypothesis testing", "Matplotlib", "Seaborn", "Tableau", "PyTorch"],
    [("Senior Data Scientist", "Basketful Retail", "Feb 2022 - Present",
      ["Built store-SKU demand forecasting (LightGBM + Prophet) reducing stock-outs by 18%",
       "Designed and analysed 30+ A/B tests on pricing and promotions using sequential testing",
       "Presented insights to category heads with Tableau dashboards"]),
     ("Data Scientist", "Shopnova", "Jul 2020 - Jan 2022",
      ["Customer churn model (XGBoost, AUC 0.86) with SHAP explanations for marketing",
       "Feature engineering in SQL and pandas on 50M-row clickstream data"])],
    [("M.Sc. in Statistics", "Indian Statistical Institute", "2018 - 2020"),
     ("B.Sc. in Mathematics", "St. Stephen's College, Delhi", "2015 - 2018")],
    certs=["Tableau Desktop Specialist"])

add("R08", "J03", "mid", "Vikram Joshi", "Ahmedabad",
    "Applied data scientist with 3 years building predictive models and statistical analyses.",
    ["Python", "pandas", "sklearn", "Statistics", "Regression", "Classification", "SQL", "Seaborn",
     "Jupyter"],
    [("Data Scientist", "Finlytics Credit", "Aug 2023 - Present",
      ["Credit-risk scorecards with logistic regression and gradient boosting",
       "Statistical hypothesis tests to validate policy changes"]),
     ("Junior Data Scientist", "Insightly Analytics", "Jul 2022 - Jul 2023",
      ["Customer segmentation using k-means; visualised clusters in Seaborn"])],
    [("M.Tech in Data Science", "DA-IICT Gandhinagar", "2020 - 2022")],
    fmt="docx")

add("R09", "J03", "junior", "Meera Pillai", "Thiruvananthapuram",
    "Aspiring data scientist; 1 year of analytics experience plus ML projects.",
    None,  # no skills section: skills only appear in the text
    [("Analytics Associate", "Datanest", "Sep 2025 - Present",
      ["Clean data in Python pandas and write SQL queries for weekly KPI reports",
       "Built a logistic regression model to flag late payments as a side project for the team"])],
    [("B.Sc. in Statistics", "University of Kerala", "2022 - 2025")],
    projects=[("House price prediction", "scikit-learn random forest with feature engineering and cross-validation"),
              ("Kaggle Titanic", "EDA with Matplotlib and classification models")])

# ---------------------------------------------------------------- J04 ML engineer / MLOps
add("R10", "J04", "strong", "Siddharth Rao", "Pune",
    "ML engineer with 6 years taking computer-vision and ranking models to production at scale.",
    ["Python", "PyTorch", "TensorFlow", "MLflow", "Kubeflow", "Docker", "Kubernetes", "AWS SageMaker",
     "AWS (EC2, S3, Lambda)", "CI/CD", "GitHub Actions", "ONNX", "TensorRT", "Airflow", "FastAPI"],
    [("Senior ML Engineer", "Opticore Vision", "May 2022 - Present",
      ["Built training pipelines on Kubeflow and model registry with MLflow for 12 CV models",
       "Served models with TorchServe on Kubernetes; ONNX/TensorRT optimisation cut latency 3x",
       "Set up CI/CD for models: automated retraining, evaluation gates and canary deployment"]),
     ("Machine Learning Engineer", "Recomatic", "Jun 2020 - Apr 2022",
      ["Deployed recommendation models on AWS SageMaker endpoints; Airflow for feature pipelines",
       "Dockerised TensorFlow inference services"])],
    [("B.Tech in Electronics and Communication", "VIT Vellore", "2016 - 2020")],
    certs=["AWS Certified Machine Learning - Specialty"], fmt="docx")

add("R11", "J04", "mid", "Neha Gupta", "Noida",
    "Software engineer turned ML engineer; 3.5 years deploying deep learning models.",
    ["Python", "PyTorch", "Docker", "k8s", "MLflow", "Weights & Biases", "AWS", "Jenkins", "FastAPI"],
    [("ML Engineer", "Voxel Health AI", "Jan 2024 - Present",
      ["Packaged PyTorch segmentation models into FastAPI services in Docker, deployed on k8s",
       "Tracked experiments in MLflow and W&B; wrote Jenkins pipelines for model releases"]),
     ("Software Engineer", "Codewell", "Jun 2022 - Dec 2023",
      ["Python backend services on AWS; introduced containerised deployments"])],
    [("B.Tech in Computer Science", "JIIT Noida", "2018 - 2022")])

add("R12", "J04", "junior", "Aditya Verma", "Indore",
    "Junior ML engineer with 1 year experience; enjoys deploying models.",
    ["Python", "TensorFlow", "Keras", "Docker", "Flask", "Git"],
    [("Associate ML Engineer", "Smartscan AI", "Aug 2025 - Present",
      ["Trained TensorFlow image classifiers and served them via Flask in Docker"])],
    [("B.Tech in Information Technology", "IIIT Kota", "2021 - 2025")],
    projects=[("Model monitoring demo", "Logged predictions and drift metrics for a Keras model")],
    fmt="docx")

# ---------------------------------------------------------------- J05 Data engineer
add("R13", "J05", "strong", "Rahul Khanna", "Hyderabad",
    "Data engineer with 7 years building batch and streaming platforms.",
    ["Python", "SQL", "PySpark", "Apache Spark", "Scala", "Airflow", "Kafka", "Snowflake", "BigQuery",
     "dbt", "AWS Glue", "EMR", "S3", "Databricks", "Data modelling"],
    [("Lead Data Engineer", "Freightly", "Apr 2021 - Present",
      ["Built streaming ingestion from Kafka into Snowflake processing 5 TB/day",
       "Orchestrated 300+ Airflow DAGs; introduced dbt models with tests and documentation",
       "Optimised PySpark jobs on Databricks, reducing compute cost by 35%"]),
     ("Data Engineer", "Telemetrix", "Jan 2018 - Mar 2021",
      ["ETL pipelines in Spark/Scala on AWS EMR; data lake on S3 with Glue catalog"]),
     ("Software Engineer", "Infobeans", "Jul 2016 - Dec 2017",
      ["SQL reporting and Python automation"])],
    [("B.E. in Computer Science", "BITS Pilani, Hyderabad Campus", "2012 - 2016")])

add("R14", "J05", "mid", "Divya Menon", "Bengaluru",
    "Data engineer (3 years) building ELT pipelines and warehouse models.",
    ["Python", "SQL", "Spark", "Airflow", "BigQuery", "dbt", "GCP", "Pub/Sub", "Git"],
    [("Data Engineer", "Adspring Media", "Mar 2024 - Present",
      ["Built ELT pipelines into BigQuery with dbt transformations and Airflow (Cloud Composer)",
       "Streaming ingestion with GCP Pub/Sub"]),
     ("Associate Data Engineer", "Analytiq", "Aug 2022 - Feb 2024",
      ["Spark batch jobs for log aggregation; data quality checks with Great Expectations"])],
    [("B.Tech in Computer Science", "PES University", "2018 - 2022")],
    fmt="docx")

add("R15", "J05", "junior", "Karan Malhotra", "Chandigarh",
    "Entry-level data engineer with ETL internship experience.",
    ["Python", "SQL", "PostgreSQL", "Pandas", "Apache Airflow", "Excel"],
    [("Data Engineering Intern", "Agrolink", "Jan 2026 - Jul 2026",
      ["Wrote Airflow DAGs to load CSV exports into PostgreSQL",
       "Python ETL scripts with pandas for cleaning sensor data"])],
    [("B.E. in Computer Science", "Chandigarh University", "2022 - 2026")],
    projects=[("Mini data warehouse", "Star schema in PostgreSQL loaded by Python ETL")])

# ---------------------------------------------------------------- J06 Frontend React
add("R16", "J06", "strong", "Ishita Bose", "Mumbai",
    "Frontend engineer with 5 years crafting accessible React applications.",
    ["JavaScript (ES6+)", "TypeScript", "React", "Redux Toolkit", "Next.js", "HTML5", "CSS3", "Tailwind CSS",
     "Jest", "React Testing Library", "Figma", "WCAG accessibility", "REST APIs"],
    [("Senior Frontend Engineer", "Canvaskit", "Jun 2023 - Present",
      ["Led migration of a design-collaboration app from JS to TypeScript and React 18",
       "Built a component library with Storybook; achieved WCAG 2.1 AA compliance",
       "State management with Redux Toolkit and RTK Query"]),
     ("Frontend Developer", "Brandbox", "Jul 2021 - May 2023",
      ["Built Next.js marketing site and dashboard; Jest/RTL test coverage 80%",
       "Translated Figma designs into responsive pages with Tailwind"])],
    [("B.Tech in Computer Science", "VJTI Mumbai", "2017 - 2021")],
    fmt="docx")

add("R17", "J06", "mid", "Aman Sethi", "Delhi",
    "Frontend developer, ~2.5 years with ReactJS and modern CSS.",
    ["ReactJS", "JavaScript", "TypeScript", "Redux", "HTML", "CSS", "SASS", "Axios", "Jest"],
    [("Frontend Developer", "Trippy Travel", "May 2024 - Present",
      ["Built booking flows in React + Redux consuming REST APIs",
       "Wrote Jest unit tests for reducers and components"]),
     ("UI Developer", "Webcraft Agency", "Jun 2023 - Apr 2024",
      ["Responsive landing pages in HTML/SASS and vanilla JavaScript"])],
    [("BCA", "Guru Gobind Singh Indraprastha University", "2020 - 2023")])

add("R18", "J06", "junior", "Tanvi Shah", "Surat",
    "Frontend enthusiast with 8 months of internship experience in React.",
    ["HTML", "CSS", "JavaScript", "React", "Bootstrap", "Git"],
    [("Frontend Intern", "Pixelbyte", "Mar 2026 - Present",
      ["Built React components for an admin panel; styled with Bootstrap"])],
    [("B.Tech in Information Technology", "SVNIT Surat", "2022 - 2026")],
    projects=[("Weather app", "React app using a public REST weather API")],
    fmt="docx")

# ---------------------------------------------------------------- J07 Full stack MERN
add("R19", "J07", "strong", "Nikhil Agarwal", "Jaipur",
    "Full stack developer with 5 years on the MERN stack building e-commerce platforms.",
    ["JavaScript", "TypeScript", "Node.js", "Express.js", "MongoDB", "Mongoose", "React", "Redux",
     "JWT", "Stripe/Razorpay integration", "Docker", "AWS EC2", "Redis", "Git"],
    [("Senior Full Stack Developer", "Bazaarly", "Feb 2023 - Present",
      ["Built multi-vendor marketplace APIs in Node/Express with MongoDB aggregation pipelines",
       "Implemented JWT auth, Razorpay payments and Redis-backed carts",
       "React storefront with server-side rendering; deployed with Docker on AWS EC2"]),
     ("Full Stack Developer", "Shopkart Labs", "Jul 2021 - Jan 2023",
      ["MERN admin dashboards; REST APIs for orders and inventory"])],
    [("B.Tech in Computer Science", "Malaviya National Institute of Technology Jaipur", "2017 - 2021")])

add("R20", "J07", "mid", "Pooja Yadav", "Lucknow",
    "MERN developer with 2 years of professional experience.",
    ["NodeJS", "Express", "MongoDB", "React", "JavaScript", "REST", "Git", "Postman"],
    [("Software Developer", "Edulane", "Sep 2024 - Present",
      ["Node.js + Express REST APIs with MongoDB for a course platform",
       "React pages for student dashboards"])],
    [("B.Tech in Computer Science", "AKTU", "2020 - 2024")],
    projects=[("Chat app", "Socket.io + Node + React real-time chat")],
    fmt="docx")

add("R21", "J07", "junior", "Harsh Vardhan", "Bhopal",
    "Junior web developer, 1 year, mostly frontend with some Node.js.",
    ["JavaScript", "React", "Node.js", "HTML", "CSS", "Firebase"],
    [("Web Developer", "Localfix", "Oct 2025 - Present",
      ["React UI for a service-booking app; small Node.js scripts and Firebase functions"])],
    [("B.Tech in Computer Science", "MANIT Bhopal", "2021 - 2025")])

# ---------------------------------------------------------------- J08 DevOps
add("R22", "J08", "strong", "Manish Tiwari", "Chennai",
    "DevOps/SRE engineer with 7 years running cloud infrastructure on AWS.",
    ["AWS", "Terraform", "Kubernetes (EKS)", "Helm", "Docker", "Jenkins", "GitHub Actions", "Ansible",
     "Prometheus", "Grafana", "Linux", "Bash", "Python", "ArgoCD"],
    [("Senior DevOps Engineer", "Cloudnine SaaS", "Jan 2022 - Present",
      ["Managed 6 EKS clusters with Helm and ArgoCD; all infrastructure in Terraform",
       "Built GitHub Actions pipelines for 50 services; deploy time down from 40 to 8 minutes",
       "Prometheus/Grafana monitoring and on-call runbooks"]),
     ("DevOps Engineer", "Hostify", "Jun 2019 - Dec 2021",
      ["Jenkins CI/CD, Ansible playbooks, Linux server hardening, Bash automation"])],
    [("B.E. in Computer Science", "SSN College of Engineering", "2015 - 2019")],
    certs=["AWS Certified Solutions Architect - Associate", "Certified Kubernetes Administrator (CKA)"],
    fmt="docx")

add("R23", "J08", "mid", "Ritika Saxena", "Gurugram",
    "Cloud engineer with 3 years automating infrastructure.",
    ["Amazon Web Services", "Terraform", "Docker", "Kubernetes", "GitLab CI", "Linux", "Shell scripting",
     "CloudWatch"],
    [("Cloud Engineer", "Payzen", "Jul 2023 - Present",
      ["Terraform modules for VPC, RDS and ECS; Kubernetes workloads on EKS",
       "GitLab CI pipelines and CloudWatch alarms"]),
     ("Systems Engineer", "Netcore Infra", "Jul 2022 - Jun 2023",
      ["Linux administration and shell scripting for 200 servers"])],
    [("B.Tech in Information Technology", "Amity University", "2018 - 2022")])

add("R24", "J08", "junior", "Varun Bhatt", "Vadodara",
    "Junior DevOps engineer with 1 year experience.",
    ["Linux", "Docker", "Jenkins", "AWS EC2", "Git", "Bash"],
    [("Junior DevOps Engineer", "Buildfast", "Sep 2025 - Present",
      ["Maintain Jenkins jobs and Docker images; manage EC2 instances"])],
    [("B.E. in Computer Engineering", "MSU Baroda", "2021 - 2025")],
    certs=["AWS Certified Cloud Practitioner"], fmt="docx")

# ---------------------------------------------------------------- J09 NLP / GenAI
add("R25", "J09", "strong", "Aditi Sharma", "Bengaluru",
    "NLP engineer with 4 years building LLM and retrieval systems.",
    ["Python", "PyTorch", "Hugging Face Transformers", "LLMs", "Prompt engineering", "RAG", "LangChain",
     "LlamaIndex", "FAISS", "Pinecone", "LoRA/PEFT fine-tuning", "spaCy", "FastAPI", "LLM evaluation"],
    [("NLP Engineer", "Docusense AI", "Jun 2023 - Present",
      ["Built RAG over 2M legal documents with hybrid BM25 + dense retrieval (FAISS) and re-ranking",
       "Fine-tuned Llama-family models with LoRA for clause extraction (+14 F1)",
       "Created evaluation harness measuring faithfulness and hallucination rate"]),
     ("Machine Learning Engineer", "Textura", "Aug 2022 - May 2023",
      ["BERT-based classifiers with Hugging Face; spaCy NER pipelines; FastAPI serving"])],
    [("M.Tech in Computer Science (AI)", "IIIT Hyderabad", "2020 - 2022")],
    projects=[("Agentic research assistant", "LangChain agent with tool use and cited answers")])

add("R26", "J09", "mid", "Farhan Qureshi", "Lucknow",
    "ML engineer (2.5 years) moving into generative AI; built chatbots with LLM APIs.",
    ["Python", "Transformers", "OpenAI API", "LangChain", "ChromaDB", "Sentence Transformers", "PyTorch",
     "NLTK", "Flask"],
    [("ML Engineer", "Helpdeskly", "Jun 2024 - Present",
      ["Built a support chatbot using retrieval-augmented generation with LangChain and ChromaDB",
       "Embeddings with Sentence Transformers; prompt templates for answer grounding"]),
     ("Data Science Intern", "Textify", "Jan 2024 - May 2024",
      ["Text classification with PyTorch and NLTK preprocessing"])],
    [("B.Tech in Computer Science", "Integral University", "2019 - 2023")],
    fmt="docx")

add("R27", "J09", "junior", "Sanya Kapoor", "Delhi",
    "Final-year-level NLP practitioner with research internship experience.",
    None,
    [("Research Intern (NLP)", "Language Lab, a university research group", "Jan 2026 - Jun 2026",
      ["Fine-tuned DistilBERT using Hugging Face for sentiment classification",
       "Experimented with prompt engineering on open-source LLMs"])],
    [("B.Tech in Computer Science", "Delhi Technological University", "2022 - 2026")],
    projects=[("PDF question answering", "Small RAG demo with LangChain and FAISS over course notes")])

# ---------------------------------------------------------------- J10 Data analyst
add("R28", "J10", "strong", "Neeraj Chauhan", "Delhi",
    "Business/data analyst with 4 years in FMCG sales and marketing analytics.",
    ["SQL", "Advanced Excel (Pivot tables, VLOOKUP, Power Query)", "Power BI", "Tableau", "DAX",
     "Python (pandas)", "A/B testing", "Google Analytics", "Stakeholder management"],
    [("Senior Data Analyst", "Freshmart FMCG", "Apr 2023 - Present",
      ["Own Power BI sales dashboards used by 60 category managers",
       "Campaign performance and A/B test readouts for marketing",
       "SQL on Snowflake to build reporting tables"]),
     ("Data Analyst", "Retailpulse", "Jul 2021 - Mar 2023",
      ["Weekly business reports in Excel and Tableau; customer segmentation in pandas"])],
    [("B.Com (Hons)", "Shri Ram College of Commerce", "2018 - 2021")],
    fmt="docx")

add("R29", "J10", "mid", "Shruti Desai", "Mumbai",
    "Data analyst with 2 years of reporting and dashboarding experience.",
    ["SQL", "MS Excel", "Tableau", "Power BI", "Python", "Statistics"],
    [("Data Analyst", "Kiranakart", "Jun 2024 - Present",
      ["Tableau dashboards for order trends; SQL queries on MySQL",
       "Excel models for promotion ROI"])],
    [("B.A. in Economics", "University of Mumbai", "2020 - 2023")],
    certs=["Google Data Analytics Professional Certificate"])

add("R30", "J10", "junior", "Mohit Jain", "Jaipur",
    "Entry-level analyst; 6-month MIS internship.",
    ["Excel", "SQL", "Power BI", "Google Sheets"],
    [("MIS Intern", "Pinkcity Textiles", "Jan 2026 - Jun 2026",
      ["Prepared daily MIS reports in Excel; built a Power BI sales dashboard"])],
    [("BBA", "University of Rajasthan", "2022 - 2025")],
    fmt="docx")

RESUMES = R


# =========================================================================== NON-TECH ROLES
# ---------------------------------------------------------------- J11 Digital marketing manager
add("R31", "J11", "strong", "Riya Malhotra", "Mumbai",
    "Performance marketer with 7 years scaling D2C beauty and fashion brands profitably.",
    ["Google Ads", "Meta Ads", "Performance Max", "SEO", "SEM", "Google Analytics 4", "Klaviyo",
     "Marketing automation", "A/B testing", "Budget management", "Team leadership"],
    [("Head of Growth Marketing", "Glowbox Beauty", "Jan 2022 - Present",
      ["Managed INR 80 lakh/month across Google and Meta Ads at 3.4x blended ROAS",
       "Built SEO programme that tripled organic sessions in 18 months",
       "Set up Klaviyo flows (welcome, abandoned cart) contributing 22% of revenue; led a team of 5"]),
     ("Digital Marketing Manager", "Threadline Apparel", "Jun 2019 - Dec 2021",
      ["Ran Shopping and Search campaigns; reduced CAC by 30% with landing-page A/B tests",
       "GA4 attribution and weekly performance reporting to founders"])],
    [("MBA in Marketing", "Narsee Monjee Institute of Management Studies", "2017 - 2019"),
     ("B.Com", "University of Mumbai", "2014 - 2017")],
    certs=["Google Ads Search Certification", "Meta Certified Media Buying Professional"])

add("R32", "J11", "mid", "Karthik Subramanian", "Chennai",
    "Digital marketer with 4 years in paid search and social for e-commerce.",
    ["Google Ads", "Facebook Ads", "Instagram marketing", "Search engine optimization", "Google Analytics",
     "Mailchimp", "Excel"],
    [("Senior Digital Marketing Executive", "Kitchenkart", "Mar 2023 - Present",
      ["Run Google Search and Shopping plus Facebook/Instagram campaigns with INR 15 lakh monthly spend",
       "Keyword research and on-page SEO for 400 product pages"]),
     ("Digital Marketing Executive", "Clickwise Agency", "Jul 2021 - Feb 2023",
      ["Managed paid campaigns for 8 clients; monthly reports from Google Analytics",
       "Built Mailchimp newsletters and drip campaigns"])],
    [("B.B.A.", "Loyola College, Chennai", "2018 - 2021")], fmt="docx")

add("R33", "J11", "junior", "Ananya Ghosh", "Kolkata",
    "Marketing graduate with 1 year in social media and paid ads.",
    ["Social media marketing", "Meta Ads", "Canva", "Google Analytics", "Content creation"],
    [("Digital Marketing Associate", "Brewbean Cafe Chain", "Aug 2025 - Present",
      ["Manage Instagram and Facebook pages; run small Meta Ads campaigns for store launches",
       "Track website visits in Google Analytics"])],
    [("BBA in Marketing", "St. Xavier's College, Kolkata", "2022 - 2025")],
    certs=["Google Digital Garage: Fundamentals of Digital Marketing"])

# ---------------------------------------------------------------- J12 Content marketing specialist
add("R34", "J12", "strong", "Nandini Rao", "Bengaluru",
    "B2B content marketer with 5 years writing for SaaS and fintech audiences.",
    ["Content writing", "Copywriting", "SEO writing", "Keyword research", "WordPress", "Editorial calendar",
     "LinkedIn marketing", "Email newsletters", "Canva", "Case studies"],
    [("Senior Content Marketer", "Payflow SaaS", "May 2023 - Present",
      ["Own the blog and editorial calendar; 60+ SEO articles grew organic sign-ups 2.5x",
       "Write customer case studies and whitepapers after interviewing CFOs",
       "Repurpose long-form content into LinkedIn posts and a fortnightly newsletter"]),
     ("Content Writer", "Fintalk Media", "Jun 2021 - Apr 2023",
      ["Wrote and edited explainers on personal finance; managed WordPress publishing"])],
    [("M.A. in English", "Christ University", "2019 - 2021"),
     ("B.A. in Journalism", "Mount Carmel College", "2016 - 2019")], fmt="docx")

add("R35", "J12", "mid", "Saurabh Mishra", "Noida",
    "Content writer with 2.5 years of SEO and social content experience.",
    ["Content writing", "SEO", "WordPress", "Social media", "Proofreading", "Google Docs"],
    [("Content Writer", "Edutrail Online", "Jun 2024 - Present",
      ["Write SEO blog posts on careers and exams; publish on WordPress",
       "Create LinkedIn and Instagram captions"]),
     ("Content Intern", "Newsroot", "Jul 2023 - May 2024",
      ["Wrote news summaries and edited copy"])],
    [("B.A. in Mass Communication", "Amity University", "2020 - 2023")])

add("R36", "J12", "junior", "Fatima Sheikh", "Hyderabad",
    "Fresh graduate who writes; runs a personal blog on books.",
    None,
    [("Content Writing Intern", "Bookbuzz", "Feb 2026 - Jun 2026",
      ["Wrote 20 book reviews and edited author interviews for the website",
       "Learned basic keyword research for SEO"])],
    [("B.A. in English Literature", "Osmania University", "2023 - 2026")],
    projects=[("Personal blog", "WordPress blog with 3,000 monthly readers")], fmt="docx")

# ---------------------------------------------------------------- J13 Sales executive B2B
add("R37", "J13", "strong", "Mitesh Patel", "Ahmedabad",
    "B2B field sales professional with 6 years selling industrial products in Gujarat.",
    ["B2B sales", "Field sales", "Lead generation", "Cold calling", "Negotiation", "Salesforce CRM",
     "Key account management", "Collections", "Gujarati", "Hindi", "English"],
    [("Senior Sales Executive", "Polywrap Packaging", "Apr 2022 - Present",
      ["Achieved 118% of annual target (INR 4.2 crore) selling packaging to pharma and FMCG plants",
       "Generated leads via cold calls and plant visits; managed pipeline in Salesforce",
       "Negotiated annual rate contracts and handled collections"]),
     ("Sales Executive", "Indus Chemicals", "Jul 2020 - Mar 2022",
      ["Field sales of industrial chemicals; added 35 new accounts"])],
    [("B.Com", "Gujarat University", "2017 - 2020")])

add("R38", "J13", "mid", "Deepak Yadav", "Indore",
    "Sales executive with 2 years in B2B distribution sales.",
    ["Sales", "Lead generation", "Client meetings", "Negotiation", "Zoho CRM", "MS Excel"],
    [("Sales Executive", "Officemate Supplies", "Aug 2024 - Present",
      ["Sell office supplies to corporate clients; meet monthly targets",
       "Log leads and follow-ups in Zoho CRM"])],
    [("BBA", "Devi Ahilya Vishwavidyalaya", "2021 - 2024")], fmt="docx")

add("R39", "J13", "junior", "Pallavi Joshi", "Pune",
    "Recent graduate with a tele-sales internship.",
    ["Tele-calling", "Customer communication", "MS Office"],
    [("Inside Sales Intern", "Learnly Edtech", "Jan 2026 - Jun 2026",
      ["Called 80 leads a day to book course demos; converted 25 enrolments"])],
    [("B.Com", "Savitribai Phule Pune University", "2022 - 2025")])

# ---------------------------------------------------------------- J14 Business development manager
add("R40", "J14", "strong", "Vivek Chaturvedi", "Gurugram",
    "Business development leader with 9 years closing enterprise deals in logistics and SaaS.",
    ["Enterprise sales", "Strategic partnerships", "Market research", "Go-to-market strategy",
     "Proposal writing", "RFP management", "Contract negotiation", "HubSpot", "Sales forecasting"],
    [("Business Development Manager", "Shipwise Technologies", "Mar 2021 - Present",
      ["Closed 14 enterprise contracts worth INR 38 crore ARR with D2C brands and marketplaces",
       "Built partnerships with 6 3PLs; led RFP responses and pricing proposals",
       "Owned quarterly revenue forecasts and pipeline reviews in HubSpot"]),
     ("Key Account Manager", "Cargonet Express", "Jun 2017 - Feb 2021",
      ["Managed top 20 enterprise accounts; negotiated multi-year contracts"])],
    [("MBA in Marketing & Strategy", "MDI Gurgaon", "2015 - 2017"),
     ("B.Tech in Mechanical Engineering", "NIT Kurukshetra", "2011 - 2015")], fmt="docx")

add("R41", "J14", "mid", "Sonal Arora", "Delhi",
    "Business development professional with 5 years in B2B services.",
    ["Business development", "Client acquisition", "Partnerships", "Salesforce", "Negotiation",
     "Proposals"],
    [("Business Development Manager", "Eventura Corporate Services", "Jan 2023 - Present",
      ["Acquire corporate clients for events and offsites; prepared 40+ proposals",
       "Built partnerships with hotel chains"]),
     ("Business Development Executive", "Eventura Corporate Services", "Jul 2021 - Dec 2022",
      ["Prospecting and lead qualification in Salesforce"])],
    [("MBA in Marketing", "Jagan Institute of Management Studies", "2019 - 2021")])

add("R42", "J14", "junior", "Rahul Bhardwaj", "Chandigarh",
    "MBA graduate with 1 year in business development.",
    ["Market research", "Lead generation", "MS PowerPoint", "Excel"],
    [("Business Development Associate", "Agriconnect", "Jul 2025 - Present",
      ["Research target markets and prepare pitch decks for partner meetings"])],
    [("MBA", "University Business School, Chandigarh", "2023 - 2025")], fmt="docx")

# ---------------------------------------------------------------- J15 HR generalist
add("R43", "J15", "strong", "Meenakshi Kulkarni", "Pune",
    "HR generalist with 7 years running HR operations in healthcare and manufacturing.",
    ["HR operations", "Employee lifecycle management", "Payroll processing", "PF & ESI compliance",
     "Labour law compliance", "Darwinbox", "Employee engagement", "Grievance handling",
     "Performance management", "Advanced Excel"],
    [("Senior HR Generalist", "Lifecare Hospitals", "Jun 2021 - Present",
      ["HR operations for 1,500 staff: onboarding, exits and records in Darwinbox",
       "Monthly payroll inputs, PF/ESI filings and labour law audits with zero findings",
       "Ran engagement surveys and the annual appraisal cycle; handled grievances"]),
     ("HR Executive", "Precision Castings Ltd", "Jul 2019 - May 2021",
      ["Attendance, leave and payroll processing for 600 workers"])],
    [("MBA in Human Resources", "Symbiosis Institute of Business Management", "2017 - 2019")],
    fmt="docx")

add("R44", "J15", "mid", "Arvind Nair", "Kochi",
    "HR executive with 3 years in HR operations and payroll.",
    ["HR operations", "Payroll", "Keka HRMS", "Onboarding", "Employee engagement", "PF", "ESI"],
    [("HR Executive", "Seaview Resorts", "Aug 2023 - Present",
      ["Onboarding and exit formalities; maintain employee records in Keka",
       "Process payroll and PF/ESI contributions; organise engagement events"])],
    [("PGDM in HR", "Rajagiri Business School", "2021 - 2023")])

add("R45", "J15", "junior", "Sneha Reddy", "Hyderabad",
    "HR graduate with an internship in HR operations.",
    ["MS Excel", "Onboarding", "Documentation"],
    [("HR Intern", "Techwave Services", "Jan 2026 - Jun 2026",
      ["Coordinated onboarding documentation and maintained employee files"])],
    [("MBA in Human Resources", "ICFAI Business School", "2024 - 2026")], fmt="docx")

# ---------------------------------------------------------------- J16 Talent acquisition
add("R46", "J16", "strong", "Kunal Sharma", "Hyderabad",
    "Talent acquisition specialist with 5 years of high-volume and lateral hiring.",
    ["End-to-end recruitment", "Candidate sourcing", "LinkedIn Recruiter", "Naukri", "Boolean search",
     "Greenhouse ATS", "Screening", "Interview coordination", "Offer negotiation", "Campus hiring",
     "Employer branding"],
    [("Senior Talent Acquisition Specialist", "Brightmind Consulting", "Feb 2022 - Present",
      ["Hired 180+ consultants a year end to end; average time-to-fill 32 days",
       "Sourced passive candidates on LinkedIn Recruiter and Naukri with Boolean search",
       "Managed pipelines in Greenhouse; led campus hiring at 12 colleges"]),
     ("Recruiter", "Talentbridge Staffing", "Jul 2021 - Jan 2022",
      ["Screening and interview scheduling for client roles"])],
    [("MBA in Human Resources", "Osmania University", "2019 - 2021")])

add("R47", "J16", "mid", "Divya Saxena", "Noida",
    "Recruiter with 2.5 years in IT and non-IT hiring.",
    ["Recruitment", "Sourcing", "Naukri", "LinkedIn", "Zoho Recruit", "Screening", "Interview scheduling"],
    [("HR Recruiter", "Peoplefirst Staffing", "May 2024 - Present",
      ["Source and screen candidates for 15 client accounts using Naukri and LinkedIn",
       "Track candidates in Zoho Recruit; coordinate interviews and offers"])],
    [("BBA", "Amity University", "2020 - 2023")], fmt="docx")

add("R48", "J16", "junior", "Akash Verma", "Lucknow",
    "Entry-level recruiter; 6-month internship.",
    ["Sourcing", "Cold calling", "MS Excel"],
    [("Recruitment Intern", "Hirefast", "Jan 2026 - Jun 2026",
      ["Sourced resumes from job portals and called candidates for screening"])],
    [("BBA", "University of Lucknow", "2022 - 2025")])

# ---------------------------------------------------------------- J17 Operations manager
add("R49", "J17", "strong", "Suresh Iyer", "Bengaluru",
    "Operations leader with 10 years in warehousing and quick-commerce fulfilment.",
    ["Warehouse operations", "Supply chain management", "Inventory management", "Team leadership",
     "Workforce planning", "Lean", "Six Sigma Green Belt", "Vendor management", "SLA management",
     "KPI dashboards", "Budgeting", "Advanced Excel"],
    [("Operations Manager", "Zipcart Quick Commerce", "Mar 2022 - Present",
      ["Run 5 dark stores with 150 associates; order fill rate 98.7%, average delivery 14 minutes",
       "Lean/Six Sigma projects cut picking time 22% and cost per order 15%",
       "Manage 3PL vendors and SLAs; own the INR 12 crore annual operating budget"]),
     ("Assistant Operations Manager", "Megamart Retail", "Jun 2016 - Feb 2022",
      ["Inbound, inventory and dispatch at a 2 lakh sq ft distribution centre; led 8 supervisors"])],
    [("MBA in Operations", "SIBM Bengaluru", "2014 - 2016"),
     ("B.E. in Mechanical Engineering", "RV College of Engineering", "2010 - 2014")],
    certs=["Lean Six Sigma Green Belt"], fmt="docx")

add("R50", "J17", "mid", "Prakash Rawat", "Gurugram",
    "Operations professional with 5 years in logistics and last-mile delivery.",
    ["Logistics operations", "Last-mile delivery", "Inventory control", "Team management", "MIS reporting",
     "Vendor coordination"],
    [("Hub Operations Manager", "Swiftship Logistics", "Feb 2023 - Present",
      ["Manage a last-mile hub with 60 riders; track delivery SLAs and MIS reports",
       "Coordinate with vendor fleet partners"]),
     ("Operations Executive", "Swiftship Logistics", "Jun 2021 - Jan 2023",
      ["Shift operations and inventory reconciliation"])],
    [("B.Com", "Delhi University", "2018 - 2021")])

add("R51", "J17", "junior", "Neha Choudhary", "Jaipur",
    "Operations trainee with 1 year in a retail distribution centre.",
    ["Inventory management", "MS Excel", "Shift coordination"],
    [("Operations Trainee", "Rajmart Distribution", "Aug 2025 - Present",
      ["Support inventory counts and dispatch planning for a regional warehouse"])],
    [("BBA", "University of Rajasthan", "2022 - 2025")], fmt="docx")

# ---------------------------------------------------------------- J18 Project manager
add("R52", "J18", "strong", "Anil Deshpande", "Delhi",
    "PMP-certified project manager with 11 years delivering infrastructure consulting projects.",
    ["Project planning", "MS Project", "Primavera P6", "Stakeholder management", "Risk management",
     "Budgeting and cost control", "Cross-functional coordination", "Change management", "Agile"],
    [("Senior Project Manager", "Metrotrack Consultants", "Jan 2020 - Present",
      ["Delivered 9 metro and highway consulting projects (INR 140 crore) on schedule",
       "Planned schedules in MS Project/Primavera; ran client steering committees",
       "Maintained risk registers and controlled change requests and budgets"]),
     ("Project Engineer", "Larsen Infra (fictional)", "Jul 2015 - Dec 2019",
      ["Coordinated subcontractors and progress reporting on site"])],
    [("B.E. in Civil Engineering", "College of Engineering Pune", "2011 - 2015")],
    certs=["PMP (Project Management Professional)"])

add("R53", "J18", "mid", "Rashmi Bhatia", "Noida",
    "Project manager with 6 years coordinating client implementation projects.",
    ["Project management", "Stakeholder communication", "MS Project", "Risk tracking", "Budget tracking",
     "Scrum"],
    [("Project Manager", "Implex Business Services", "Apr 2022 - Present",
      ["Manage 4-6 client implementation projects; weekly status reports to stakeholders",
       "Track risks, issues and budgets in MS Project"]),
     ("Project Coordinator", "Implex Business Services", "Jul 2020 - Mar 2022",
      ["Scheduling, meeting notes and documentation"])],
    [("B.Tech in Electronics", "Jaypee Institute", "2016 - 2020")],
    certs=["PRINCE2 Foundation"], fmt="docx")

add("R54", "J18", "junior", "Gaurav Singh", "Bhopal",
    "Project coordinator with 1 year of experience.",
    ["MS Excel", "Scheduling", "Documentation"],
    [("Project Coordinator", "Buildright Contractors", "Sep 2025 - Present",
      ["Maintain project schedules and minutes of meetings for site teams"])],
    [("B.Tech in Civil Engineering", "MANIT Bhopal", "2021 - 2025")])

# ---------------------------------------------------------------- J19 Accountant
add("R55", "J19", "strong", "Ramesh Agarwal", "Jaipur",
    "Accountant with 8 years handling books, GST and audits for manufacturing exporters.",
    ["Tally Prime", "Tally ERP 9", "GST returns", "TDS", "Bank reconciliation", "Accounts payable",
     "Accounts receivable", "Financial statements", "Statutory audit", "Export documentation", "Advanced Excel"],
    [("Senior Accountant", "Rajputana Handicrafts Exports", "Apr 2020 - Present",
      ["Maintain books in Tally Prime for INR 60 crore turnover; monthly closing",
       "File GSTR-1/3B and TDS returns; handle export refunds",
       "Prepare financial statements and coordinate the statutory audit"]),
     ("Accountant", "Shree Ganesh Textiles", "Jul 2018 - Mar 2020",
      ["Bank reconciliations, vendor ledgers and payables in Tally ERP 9"])],
    [("M.Com", "University of Rajasthan", "2016 - 2018"), ("B.Com", "University of Rajasthan", "2013 - 2016")],
    certs=["CA Intermediate (both groups)"], fmt="docx")

add("R56", "J19", "mid", "Pooja Khandelwal", "Udaipur",
    "Accounts executive with 3 years in GST and bookkeeping.",
    ["Tally", "GST", "TDS", "Bookkeeping", "Bank reconciliation", "MS Excel"],
    [("Accounts Executive", "Lakecity Marbles", "May 2023 - Present",
      ["Bookkeeping and GST filing in Tally; bank reconciliations"]),
     ("Accounts Assistant", "Mohan & Co. Chartered Accountants", "Jun 2022 - Apr 2023",
      ["Data entry and TDS computations for clients"])],
    [("B.Com", "Mohanlal Sukhadia University", "2019 - 2022")])

add("R57", "J19", "junior", "Sunil Meena", "Kota",
    "Commerce graduate with basic accounting knowledge.",
    ["Tally", "MS Excel", "Data entry"],
    [("Accounts Trainee", "Hadoti Traders", "Mar 2026 - Present",
      ["Voucher entry in Tally and filing of invoices"])],
    [("B.Com", "University of Kota", "2022 - 2025")], fmt="docx")

# ---------------------------------------------------------------- J20 Financial analyst
add("R58", "J20", "strong", "Ishaan Kapoor", "Mumbai",
    "FP&A analyst with 5 years in financial modelling, forecasting and valuation.",
    ["Financial modelling", "Budgeting", "Forecasting", "Variance analysis", "DCF valuation",
     "Comparable company analysis", "Advanced Excel", "PowerPoint", "Power BI", "SQL"],
    [("Senior Financial Analyst", "Horizon Consumer Brands", "Jun 2022 - Present",
      ["Built the 3-statement model and annual budget for a INR 900 crore business",
       "Monthly variance analysis and board decks for the CFO; Power BI dashboards",
       "DCF and comparables valuation for two acquisitions"]),
     ("Equity Research Associate", "Northbridge Securities", "Jul 2021 - May 2022",
      ["Maintained models and wrote initiation reports on consumer stocks"])],
    [("MBA in Finance", "SP Jain Institute of Management", "2019 - 2021")],
    certs=["CFA Level II candidate"], fmt="docx")

add("R59", "J20", "mid", "Aditi Jain", "Bengaluru",
    "Financial analyst with 2.5 years in budgeting and MIS.",
    ["Budgeting", "Forecasting", "Financial analysis", "Excel", "PowerPoint", "MIS reporting"],
    [("Financial Analyst", "Greenleaf Foods", "Apr 2024 - Present",
      ["Prepare monthly MIS and budget-vs-actual reports; support annual budgeting"]),
     ("Finance Intern", "Greenleaf Foods", "Jan 2024 - Mar 2024",
      ["Built Excel templates for cost tracking"])],
    [("MBA in Finance", "Christ University", "2022 - 2024")])

add("R60", "J20", "junior", "Varun Mehta", "Ahmedabad",
    "Commerce graduate preparing for CFA Level I; 6-month finance internship.",
    ["Excel", "Financial statements", "PowerPoint"],
    [("Finance Intern", "Sabarmati Capital", "Jan 2026 - Jun 2026",
      ["Compiled financial data of listed companies and built simple ratio analyses"])],
    [("B.Com (Hons)", "HL College of Commerce", "2022 - 2025")], fmt="docx")

# =========================================================================== DISTRACTORS
# Off-domain profiles that match none of the 20 JDs: every score should be "Weak".
add("R61", "NONE", "none", "Lakshmi Menon", "Kochi",
    "Registered nurse with 6 years in critical care.",
    ["Patient care", "ICU nursing", "Medication administration", "Ventilator management", "BLS", "ACLS"],
    [("Staff Nurse (ICU)", "Amrita Hospital", "Jun 2020 - Present",
      ["Care for 3-4 ventilated ICU patients per shift; medication administration and charting"])],
    [("B.Sc. Nursing", "Government College of Nursing, Kottayam", "2016 - 2020")], certs=["ACLS", "BLS"],
    adjacent=["J21"])

add("R62", "NONE", "none", "Sunita Rathore", "Jodhpur",
    "Secondary school mathematics teacher with 9 years of classroom experience.",
    ["Lesson planning", "Classroom management", "CBSE curriculum", "Student assessment", "Parent communication"],
    [("Mathematics Teacher (TGT)", "Kendriya Vidyalaya No. 2", "Jul 2017 - Present",
      ["Teach mathematics to classes 8-10; 96% board pass rate"])],
    [("B.Ed.", "Jai Narain Vyas University", "2015 - 2017"), ("M.Sc. in Mathematics", "Jai Narain Vyas University", "2013 - 2015")],
    fmt="docx")

add("R63", "NONE", "none", "Joseph D'Souza", "Goa",
    "Chef de partie with 7 years in hotel kitchens.",
    ["Continental cuisine", "Menu planning", "Food costing", "HACCP", "Kitchen team supervision"],
    [("Chef de Partie", "Seashore Grand Hotel", "Nov 2019 - Present",
      ["Run the continental section; plan seasonal menus and manage food cost at 28%"])],
    [("Diploma in Culinary Arts", "IHM Goa", "2016 - 2019")], adjacent=["J22"])

add("R64", "NONE", "none", "Priyanka Sood", "Chandigarh",
    "Litigation lawyer with 6 years in civil and commercial disputes.",
    ["Civil litigation", "Legal drafting", "Contract review", "Court appearances", "Legal research"],
    [("Associate Advocate", "Sood & Partners", "Jul 2020 - Present",
      ["Draft plaints, written statements and appeals; appear before the High Court"])],
    [("LL.B.", "Panjab University", "2017 - 2020")], fmt="docx", adjacent=["J23"])

add("R65", "NONE", "none", "Harish Gowda", "Mysuru",
    "Civil site engineer with 5 years on residential construction.",
    ["Site supervision", "AutoCAD", "Quantity estimation", "Quality control", "Concrete technology"],
    [("Site Engineer", "Shreeram Builders", "Jun 2021 - Present",
      ["Supervise structural work for 3 residential towers; quantity estimation and billing"])],
    [("B.E. in Civil Engineering", "SJCE Mysuru", "2017 - 2021")])

add("R66", "NONE", "none", "Farah Khan", "Lucknow",
    "Pharmacist with 4 years in hospital and retail pharmacy.",
    ["Dispensing", "Drug interactions", "Inventory of medicines", "Patient counselling", "Pharmacovigilance"],
    [("Pharmacist", "Sahara Hospital", "Aug 2022 - Present",
      ["Dispense prescriptions and counsel patients; manage medicine stock"])],
    [("B.Pharm", "Integral University", "2018 - 2022")], fmt="docx")

add("R67", "NONE", "none", "Rohit Bhattacharya", "Kolkata",
    "Architect with 6 years designing residential and hospitality projects.",
    ["Architectural design", "AutoCAD", "Revit", "SketchUp", "Building codes", "Site coordination"],
    [("Project Architect", "Studio Ganga Architects", "Jul 2020 - Present",
      ["Design residential villas and boutique hotels; prepare working drawings in Revit"])],
    [("B.Arch", "Jadavpur University", "2015 - 2020")])

add("R68", "NONE", "none", "Tenzin Dolma", "Darjeeling",
    "Hotel front office executive with 4 years of guest services experience.",
    ["Front office operations", "Guest relations", "Opera PMS", "Reservations", "Complaint handling"],
    [("Front Office Executive", "Himalayan Heritage Resort", "Apr 2022 - Present",
      ["Check-ins, reservations on Opera PMS and guest complaint resolution"])],
    [("Diploma in Hotel Management", "IHM Kolkata", "2019 - 2022")], fmt="docx")

add("R69", "NONE", "none", "Manoj Kumar", "Patna",
    "Retail store associate with 3 years in apparel retail.",
    ["Customer service", "Visual merchandising", "Billing (POS)", "Stock replenishment"],
    [("Store Associate", "Trendz Fashion Store", "Jun 2023 - Present",
      ["Assist customers, handle POS billing and maintain store displays"])],
    [("B.A.", "Patna University", "2019 - 2022")])

add("R70", "NONE", "none", "Abhishek Thakur", "Pune",
    "Mechanical design engineer with 5 years in automotive components.",
    ["SolidWorks", "CATIA", "GD&T", "FMEA", "Design for manufacturing", "ANSYS"],
    [("Design Engineer", "Autoparts Precision Ltd", "Jul 2021 - Present",
      ["Design brake and suspension components in CATIA; FMEA and tolerance analysis"])],
    [("B.E. in Mechanical Engineering", "PICT Pune", "2017 - 2021")], fmt="docx")


# =========================================================================== HELD-OUT DOMAINS
# Worded differently from the JDs on purpose ("blood sample collection" vs "venipuncture").
add("R71", "J21", "strong", "Rekha Saini", "Jaipur",
    "Phlebotomy technician with 4 years in diagnostic labs and home collection.",
    ["Blood sample collection", "Finger-prick testing", "Sample tube sequencing", "Patient ID verification",
     "Biomedical waste handling", "LabMate lab software", "Home collection"],
    [("Senior Sample Collection Technician", "Pinkcity Pathlabs", "Mar 2022 - Present",
      ["Draw blood from 50+ patients a day from arm veins, including children and elderly patients",
       "Do finger-prick sugar and haemoglobin tests at the collection counter",
       "Fill tubes in the correct sequence (blood culture, citrate, serum, EDTA, fluoride)",
       "Confirm every patient with two identifiers and label tubes at the bedside",
       "Segregate needles and biomedical waste as per BMW rules; enter samples in LabMate software"]),
     ("Sample Collection Technician", "Healthfirst Labs", "Jul 2020 - Feb 2022",
      ["Home visits for sample collection; maintained ice-box temperature during transport"])],
    [("DMLT (Diploma in Medical Laboratory Technology)", "SMS Medical College, Jaipur", "2018 - 2020")])

add("R72", "J21", "mid", "Imtiyaz Ali", "Ajmer",
    "Lab assistant with 1.5 years of sample collection experience.",
    ["Blood collection", "Sample labelling", "Hygiene practices"],
    [("Lab Assistant", "Ajmer City Diagnostics", "May 2025 - Present",
      ["Collect blood samples from walk-in patients and label sample tubes",
       "Keep the collection area clean and follow hand-hygiene protocol"])],
    [("B.Sc. in Medical Laboratory Technology", "Maharshi Dayanand Saraswati University", "2021 - 2024")],
    fmt="docx")

add("R73", "J22", "strong", "Celine Fernandes", "Bengaluru",
    "Pastry chef with 6 years in French patisseries and hotel bakeries.",
    ["Croissants and Danish", "Puff pastry", "Chocolate work", "Dessert plating", "Recipe costing",
     "Food hygiene", "Wedding cakes"],
    [("Pastry Chef", "Le Petit Four Patisserie", "Apr 2021 - Present",
      ["Bake 400 croissants, pain au chocolat and Danish every morning from house-made butter doughs",
       "Make chocolate bonbons and decorations; temper couverture by tabling and seeding",
       "Created a 6-dessert plated menu for the bistro dinner service",
       "Cost every recipe and kept pastry food cost under 26%",
       "Run HACCP logs for the pastry kitchen and train two commis"]),
     ("Commis Pastry", "The Grand Orchid Hotel", "Jun 2019 - Mar 2021",
      ["Bakery production for buffet and banquet desserts"])],
    [("Diploma in Bakery and Patisserie", "IHM Bengaluru", "2016 - 2019")], fmt="docx")

add("R74", "J22", "mid", "Arjun Pillai", "Kochi",
    "Bakery cook with 2.5 years in a hotel bakery.",
    ["Breads", "Cakes", "Puff pastry", "Kitchen hygiene"],
    [("Bakery Commis", "Malabar Bay Resort", "Jun 2024 - Present",
      ["Prepare breads, puff pastry and cakes for breakfast buffet",
       "Assist pastry chef with dessert garnishing; follow kitchen hygiene checklist"])],
    [("Diploma in Food Production", "IHM Kovalam", "2021 - 2024")])

add("R75", "J23", "strong", "Nidhi Aggarwal", "New Delhi",
    "Litigation paralegal with 4 years supporting commercial disputes in the Delhi High Court.",
    ["Case law research", "Drafting", "E-filing", "Court calendar management", "Paper books"],
    [("Senior Legal Assistant", "Verma & Bose Advocates", "Jan 2022 - Present",
      ["Research precedents on SCC Online and Manupatra and prepare research notes for partners",
       "Prepare first drafts of plaints, written statements, affidavits and interim applications",
       "File documents on the Delhi High Court e-filing portal and track defects",
       "Maintain the hearing diary and limitation tracker for 120+ matters",
       "Index and paginate paper books and maintain matter files"]),
     ("Legal Assistant", "Lex Partners", "Jul 2020 - Dec 2021",
      ["Document management and client correspondence"])],
    [("LL.B.", "Campus Law Centre, University of Delhi", "2017 - 2020")], fmt="docx")

add("R76", "J23", "mid", "Rohan Tiwari", "Lucknow",
    "Legal assistant with 2 years in a district court practice.",
    ["Legal drafting", "Document filing", "Client coordination"],
    [("Legal Assistant", "Tiwari Law Chambers", "Aug 2024 - Present",
      ["Type and format affidavits and applications drafted by the advocate",
       "Physically file documents at the district court and note the next dates of hearing"])],
    [("B.A. LL.B.", "Lucknow University", "2019 - 2024")])
