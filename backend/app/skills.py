"""Skill taxonomy: canonical names, aliases and "implies" relations.

Used for
  * normalising skill strings (LLM output or rule-based extraction) to one canonical form,
  * scanning free text for skill mentions (rule-based fallback + evidence search),
  * inferring general skills from specific ones (PostgreSQL => SQL, EKS => Kubernetes + AWS).

Anything not in the taxonomy is kept as a cleaned free-text skill and can still be
matched semantically by embeddings.
"""
from __future__ import annotations

import re
from functools import lru_cache

# canonical display name -> (aliases, implies)
TAXONOMY: dict[str, tuple[list[str], list[str]]] = {
    # languages
    "Python": (["python3", "py"], []),
    "Java": (["core java", "java se", "j2ee", "java ee"], []),
    "JavaScript": (["js", "es6", "es6+", "ecmascript", "vanilla javascript"], []),
    "TypeScript": (["ts"], ["JavaScript"]),
    "SQL": (["structured query language", "t-sql", "pl/sql", "plsql"], []),
    "Scala": ([], []),
    "C++": (["cpp"], []),
    "Go": (["golang"], []),
    "Bash": (["shell scripting", "shell script", "bash scripting", "shell"], []),
    "R": ([], []),
    "HTML": (["html5"], []),
    "CSS": (["css3"], []),
    "SASS": (["scss"], ["CSS"]),
    "DAX": ([], ["Power BI"]),
    # backend frameworks
    "Spring Boot": (["springboot", "spring-boot"], ["Java", "Spring"]),
    "Spring": (["spring framework", "spring mvc", "spring cloud", "spring data"], ["Java"]),
    "Hibernate": (["jpa", "hibernate/jpa"], ["Java"]),
    "FastAPI": (["fast api"], ["Python", "REST APIs"]),
    "Django": ([], ["Python"]),
    "Django REST Framework": (["drf", "django rest"], ["Django", "Python", "REST APIs"]),
    "Flask": ([], ["Python"]),
    "Node.js": (["nodejs", "node", "node js"], ["JavaScript"]),
    "Express.js": (["express", "expressjs"], ["Node.js", "JavaScript"]),
    "SQLAlchemy": ([], ["Python", "SQL"]),
    "Celery": ([], ["Python"]),
    "GraphQL": ([], []),
    "REST APIs": (["rest", "restful", "rest api", "restful apis", "restful services", "rest endpoints",
                   "api design", "rest api design", "rest api integration"], []),
    "Microservices": (["microservice", "microservices architecture"], []),
    "JWT": (["json web token"], []),
    "Socket.io": ([], ["Node.js"]),
    # frontend
    "React": (["reactjs", "react.js", "react 18"], ["JavaScript"]),
    "Redux": (["redux toolkit", "rtk", "rtk query"], ["React"]),
    "Next.js": (["nextjs", "next js"], ["React"]),
    "Tailwind CSS": (["tailwind", "tailwindcss"], ["CSS"]),
    "Bootstrap": ([], ["CSS"]),
    "Jest": ([], ["JavaScript"]),
    "React Testing Library": (["rtl", "testing library"], ["React"]),
    "Figma": ([], []),
    "Web Accessibility": (["wcag", "accessibility", "a11y", "wcag accessibility"], []),
    "Storybook": ([], []),
    "Responsive Design": (["responsive web design"], ["CSS"]),
    # databases
    "PostgreSQL": (["postgres", "postgre", "psql"], ["SQL"]),
    "MySQL": ([], ["SQL"]),
    "Oracle": (["oracle sql", "oracle db"], ["SQL"]),
    "SQLite": ([], ["SQL"]),
    "MongoDB": (["mongo", "mongoose"], []),
    "Redis": ([], []),
    "Snowflake": ([], ["Data Warehousing", "SQL"]),
    "BigQuery": (["google bigquery"], ["Data Warehousing", "SQL"]),
    "Redshift": (["amazon redshift"], ["Data Warehousing", "SQL"]),
    "Data Warehousing": (["data warehouse", "dwh", "data modelling", "data modeling", "star schema"], []),
    "Firebase": ([], []),
    # messaging / data eng
    "Apache Kafka": (["kafka"], []),
    "RabbitMQ": ([], []),
    "Apache Spark": (["spark"], []),
    "PySpark": ([], ["Apache Spark", "Python"]),
    "Apache Airflow": (["airflow", "cloud composer"], []),
    "dbt": (["data build tool"], ["SQL"]),
    "ETL": (["etl/elt", "elt", "etl pipelines", "data pipelines", "etl pipeline design"], []),
    "Databricks": ([], ["Apache Spark"]),
    "AWS Glue": (["glue"], ["AWS"]),
    "AWS EMR": (["emr"], ["AWS", "Apache Spark"]),
    "GCP Pub/Sub": (["pub/sub", "pubsub"], ["GCP"]),
    "Great Expectations": ([], []),
    # cloud / devops
    "AWS": (["amazon web services", "aws cloud", "ec2", "aws ec2", "s3", "aws s3", "lambda", "aws lambda",
             "ecs", "rds", "cloudwatch"], []),
    "AWS SageMaker": (["sagemaker"], ["AWS", "Model Deployment"]),
    "GCP": (["google cloud", "google cloud platform"], []),
    "Azure": (["microsoft azure"], []),
    "Docker": (["docker-compose", "docker compose", "containerization", "containerisation"], []),
    "Kubernetes": (["k8s", "eks", "aks", "gke", "kubernetes (eks)"], []),
    "Helm": ([], ["Kubernetes"]),
    "Terraform": ([], ["Infrastructure as Code"]),
    "Infrastructure as Code": (["iac"], []),
    "Ansible": ([], []),
    "Jenkins": ([], ["CI/CD"]),
    "GitHub Actions": (["gh actions"], ["CI/CD"]),
    "GitLab CI": (["gitlab ci/cd"], ["CI/CD"]),
    "ArgoCD": (["argo cd"], ["CI/CD", "Kubernetes"]),
    "CI/CD": (["ci cd", "cicd", "continuous integration", "continuous delivery", "continuous deployment"], []),
    "Prometheus": ([], ["Monitoring"]),
    "Grafana": ([], ["Monitoring"]),
    "Monitoring": (["observability", "alerting"], []),
    "Linux": (["linux administration", "unix", "linux server"], []),
    "Git": (["github", "gitlab", "version control"], []),
    # data science / ML
    "pandas": ([], ["Python"]),
    "NumPy": ([], ["Python"]),
    "scikit-learn": (["sklearn", "scikit learn"], ["Machine Learning", "Python"]),
    "XGBoost": ([], ["Machine Learning"]),
    "LightGBM": ([], ["Machine Learning"]),
    "statsmodels": ([], ["Statistics"]),
    "Prophet": ([], ["Time-series Forecasting"]),
    "Time-series Forecasting": (["time series forecasting", "time-series", "demand forecasting"], []),
    "Machine Learning": (["ml", "supervised learning", "predictive modelling", "predictive modeling",
                          "classification", "regression", "applied machine learning"], []),
    "Deep Learning": (["neural networks", "dl"], ["Machine Learning"]),
    "Statistics": (["statistical analysis", "hypothesis testing", "statistical methods", "basic statistics",
                    "inferential statistics"], []),
    "A/B Testing": (["ab testing", "a/b tests", "experimentation", "split testing"], ["Statistics"]),
    "Matplotlib": ([], ["Data Visualization"]),
    "Seaborn": ([], ["Data Visualization"]),
    "Data Visualization": (["data visualisation", "visualization", "visualisation", "dashboarding",
                           "dashboards"], []),
    "Tableau": ([], ["Data Visualization"]),
    "Power BI": (["powerbi", "power-bi", "pbi"], ["Data Visualization"]),
    "Excel": (["ms excel", "microsoft excel", "advanced excel", "pivot tables", "vlookup", "power query"], []),
    "Google Analytics": ([], []),
    "Jupyter": (["jupyter notebook"], []),
    "PyTorch": (["torch", "torchserve"], ["Deep Learning", "Python"]),
    "TensorFlow": (["tf"], ["Deep Learning"]),
    "Keras": ([], ["Deep Learning", "TensorFlow"]),
    "MLflow": ([], ["Experiment Tracking"]),
    "Weights & Biases": (["wandb", "w&b"], ["Experiment Tracking"]),
    "Experiment Tracking": ([], []),
    "Kubeflow": ([], ["Kubernetes", "MLOps"]),
    "MLOps": ([], []),
    "Model Deployment": (["model serving", "model deployment / model serving", "deploying models",
                         "model inference serving"], []),
    "ONNX": ([], []),
    "TensorRT": ([], []),
    "Feature Store": (["feature stores"], []),
    "Computer Vision": (["cv", "image classification", "image segmentation"], ["Deep Learning"]),
    # NLP / GenAI
    "NLP": (["natural language processing", "nlp fundamentals", "text classification", "ner"], []),
    "Hugging Face Transformers": (["hugging face", "huggingface", "transformers", "hf transformers"],
                                  ["NLP", "Deep Learning"]),
    "BERT": (["distilbert", "roberta"], ["Hugging Face Transformers", "NLP"]),
    "LLMs": (["llm", "large language models", "large language models (llms)", "openai api", "gpt",
              "llama", "gemini api"], ["NLP"]),
    "Prompt Engineering": ([], ["LLMs"]),
    "RAG": (["retrieval-augmented generation", "retrieval augmented generation"], ["LLMs"]),
    "LangChain": ([], ["LLMs"]),
    "LlamaIndex": (["llama index", "llama-index"], ["LLMs"]),
    "Vector Databases": (["vector database", "vector db", "vector search"], []),
    "FAISS": ([], ["Vector Databases"]),
    "Pinecone": ([], ["Vector Databases"]),
    "ChromaDB": (["chroma"], ["Vector Databases"]),
    "Sentence Transformers": (["sentence-transformers", "sbert"], ["NLP"]),
    "Fine-tuning": (["lora", "peft", "lora/peft", "fine tuning", "lora/peft fine-tuning",
                     "fine-tuning with lora / peft"], []),
    "LLM Evaluation": (["llm eval", "evaluation harness"], []),
    "spaCy": (["spacy"], ["NLP"]),
    "NLTK": ([], ["NLP"]),
    # testing / misc
    "JUnit": ([], ["Java"]),
    "Mockito": ([], ["Java"]),
    "pytest": ([], ["Python"]),
    "Postman": ([], []),
    "Stakeholder Communication": (["stakeholder management", "stakeholder reporting"], []),
}

# ---------------------------------------------------------------- non-tech roles
TAXONOMY.update({
    # marketing
    "SEO": (["search engine optimization", "search engine optimisation", "on-page seo", "technical seo",
             "seo writing", "seo audits", "technical seo audits"], []),
    "Keyword Research": ([], ["SEO"]),
    "SEM": (["search engine marketing", "paid search", "ppc", "pay-per-click"], []),
    "Google Ads": (["google adwords", "adwords", "performance max", "pmax", "google search ads",
                    "google shopping ads", "google ads (search, shopping, performance max)"],
                   ["SEM", "Performance Marketing"]),
    "Meta Ads": (["facebook ads", "instagram ads", "facebook/instagram ads", "meta ads manager"],
                 ["Social Media Marketing", "Performance Marketing"]),
    "Performance Marketing": (["paid marketing", "paid media", "paid campaigns", "growth marketing"], []),
    "Google Analytics": (["google analytics 4", "ga4", "universal analytics"], []),
    "Email Marketing": (["email campaigns", "email newsletters", "drip campaigns", "newsletters"], []),
    "Marketing Automation": (["marketing automation journeys"], []),
    "Klaviyo": ([], ["Email Marketing", "Marketing Automation"]),
    "Mailchimp": ([], ["Email Marketing", "Marketing Automation"]),
    "Social Media Marketing": (["social media", "social media management", "instagram marketing",
                               "linkedin marketing", "social media marketing (linkedin)"], []),
    "Content Writing": (["content creation", "blog writing", "article writing", "content marketing",
                         "content writing or content marketing"], []),
    "Copywriting": (["copy writing", "english copywriting"], []),
    "Editing": (["proofreading", "copyediting", "copy editing"], []),
    "WordPress": ([], ["CMS"]),
    "CMS": (["content management system", "wordpress or another cms"], []),
    "Canva": ([], []),
    "Editorial Calendar": (["content calendar"], []),
    "ROI Analysis": (["roas", "return on ad spend", "campaign roi", "campaign budgeting and roi analysis"], []),
    # sales / business development
    "B2B Sales": (["b2b field sales", "business-to-business sales", "corporate sales", "industrial sales"], []),
    "Field Sales": (["on-field sales"], []),
    "Lead Generation": (["lead gen", "prospecting", "lead qualification"], []),
    "Cold Calling": (["tele-calling", "telecalling", "tele sales", "telesales", "inside sales"], []),
    "Negotiation": (["negotiation skills", "negotiation and closing", "negotiation and closing skills"], []),
    "Contract Negotiation": ([], ["Negotiation"]),
    "CRM": (["customer relationship management", "crm software"], []),
    "Salesforce": (["salesforce crm", "sfdc"], ["CRM"]),
    "Zoho CRM": ([], ["CRM"]),
    "HubSpot": (["hubspot crm"], ["CRM"]),
    "Key Account Management": (["key accounts", "account management", "enterprise account management"], []),
    "Enterprise Sales": (["enterprise / key account sales", "enterprise account sales"], []),
    "Strategic Partnerships": (["partnerships", "partnership development", "alliances"], []),
    "Market Research": (["market analysis"], []),
    "Go-to-market Strategy": (["gtm", "go to market", "gtm strategy", "go-to-market"], []),
    "Proposal Writing": (["proposals", "rfp", "rfp management", "rfp responses", "proposal writing and rfp management"], []),
    "Sales Forecasting": (["revenue forecasting", "pipeline forecasting"], []),
    "Business Development": (["biz dev", "client acquisition"], []),
    # HR
    "HR Operations": (["hr ops", "employee lifecycle management", "employee lifecycle", "hr administration"], []),
    "Payroll": (["payroll processing", "payroll management"], []),
    "Labour Law Compliance": (["labor law compliance", "statutory compliance", "labour laws", "labor laws",
                               "pf & esi compliance", "pf/esi", "pf", "esi", "labour law compliance (pf, esi)"], []),
    "HRMS": (["hris", "darwinbox", "keka", "keka hrms", "sap successfactors", "successfactors", "zoho people"], []),
    "Employee Engagement": ([], []),
    "Grievance Handling": (["grievance redressal", "employee relations"], []),
    "Performance Management": (["appraisals", "performance appraisal", "appraisal cycle"], []),
    "Onboarding": (["employee onboarding", "induction"], []),
    "Recruitment": (["end-to-end recruitment", "talent acquisition", "recruiting", "full-cycle recruiting"], []),
    "Candidate Sourcing": (["sourcing", "boolean search", "headhunting", "talent sourcing"], []),
    "LinkedIn Recruiter": ([], ["Candidate Sourcing"]),
    "Naukri": (["naukri.com"], ["Candidate Sourcing"]),
    "Applicant Tracking System": (["ats", "greenhouse", "lever", "zoho recruit", "applicant tracking systems",
                                   "greenhouse ats"], []),
    "Interviewing": (["screening", "candidate screening", "screening and interviewing", "interview coordination",
                      "interview scheduling"], []),
    "Offer Negotiation": (["offer management"], ["Negotiation"]),
    "Campus Hiring": (["campus recruitment"], []),
    "Employer Branding": ([], []),
    # operations / project management
    "Supply Chain Management": (["supply chain", "supply-chain management", "scm"], []),
    "Warehouse Operations": (["warehousing", "warehouse management", "warehouse / supply-chain operations"],
                             ["Supply Chain Management"]),
    "Logistics Operations": (["last-mile delivery", "last mile delivery"], ["Supply Chain Management"]),
    "Inventory Management": (["inventory control", "stock management"], []),
    "Team Leadership": (["people management", "team management", "leading teams",
                         "team leadership and workforce planning"], []),
    "Workforce Planning": (["manpower planning", "shift planning"], []),
    "Lean": (["lean manufacturing", "lean management"], ["Process Improvement"]),
    "Six Sigma": (["six sigma green belt", "lean six sigma", "lean / six sigma", "lean six sigma green belt"],
                  ["Process Improvement"]),
    "Process Improvement": (["continuous improvement", "process optimisation", "process optimization",
                             "process improvement (lean / six sigma)"], []),
    "Vendor Management": (["vendor coordination", "supplier management", "3pl management"], []),
    "SLA Management": (["sla", "service level agreements"], []),
    "KPI Tracking": (["kpi dashboards", "kpis", "kpi tracking and budgeting"], []),
    "MIS Reporting": (["mis"], []),
    "Budgeting": (["budget management", "budgeting and cost control", "cost control", "budget planning",
                   "operating budget", "budget tracking"], []),
    "Project Management": (["project planning", "project planning and scheduling", "project scheduling",
                            "project coordination"], []),
    "MS Project": (["microsoft project"], ["Project Management"]),
    "Primavera": (["primavera p6"], ["Project Management"]),
    "Risk Management": (["risk tracking", "risk registers", "risk assessment"], []),
    "Cross-functional Coordination": (["cross-functional team coordination", "cross-functional collaboration"], []),
    "Change Management": (["change requests"], []),
    "PMP": (["project management professional", "pmp certification"], ["Project Management"]),
    "PRINCE2": (["prince2 foundation"], ["Project Management"]),
    "Agile": (["agile/scrum", "agile / scrum", "scrum"], []),
    # finance / accounting
    "Accounting": (["bookkeeping", "book keeping", "books of accounts", "general ledger"], []),
    "Tally": (["tally erp", "tally erp 9", "tally prime", "tally erp / tally prime"], ["Accounting"]),
    "Taxation": (["direct tax", "indirect tax"], []),
    "GST": (["gst filing", "gst returns", "gst compliance", "goods and services tax", "gst filing and compliance",
             "gstr"], ["Taxation"]),
    "TDS": (["tds returns", "tax deducted at source"], ["Taxation"]),
    "Bank Reconciliation": (["bank reconciliations"], []),
    "Accounts Payable": (["payables"], []),
    "Accounts Receivable": (["receivables"], []),
    "Financial Statements": (["financial statement preparation", "final accounts"], []),
    "Auditing": (["statutory audit", "audit support", "internal audit"], []),
    "Financial Modelling": (["financial modeling", "3-statement model", "three statement model"], []),
    "Financial Forecasting": (["forecasting"], []),
    "Variance Analysis": (["budget vs actual", "budget-vs-actual"], []),
    "Valuation": (["dcf", "dcf valuation", "discounted cash flow", "comparable company analysis", "comparables",
                   "trading comps", "valuation (dcf, comparable companies)"], []),
    "FP&A": (["financial planning and analysis"], []),
    "PowerPoint": (["ms powerpoint", "microsoft powerpoint", "powerpoint presentations"], []),
    "Export Documentation": ([], []),
})

# Pairs that look similar to embeddings/string matching but are different skills.
FALSE_FRIENDS = {frozenset({"java", "javascript"}), frozenset({"react", "react native"}),
                 frozenset({"c++", "c#"}), frozenset({"sql", "nosql"})}


def _clean(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"\s+", " ", s)
    s = s.strip(" .,;:-•*")
    return s


def _strip_version(s: str) -> str:
    # "java 17" -> "java", "python 3.11" -> "python", "react 18" handled via alias
    return re.sub(r"\s+v?\d+(\.\d+)*\+?$", "", s).strip()


@lru_cache(maxsize=1)
def _alias_index() -> dict[str, str]:
    idx: dict[str, str] = {}
    for canon, (aliases, _) in TAXONOMY.items():
        idx[_clean(canon)] = canon
        for a in aliases:
            idx[_clean(a)] = canon
    return idx


def normalize(skill: str) -> str:
    """Map a raw skill string to its canonical name (or a cleaned version of itself)."""
    if not skill:
        return ""
    c = _clean(skill)
    idx = _alias_index()
    if c in idx:
        return idx[c]
    v = _strip_version(c)
    if v in idx:
        return idx[v]
    # "AWS (ECS, RDS, S3)" -> try the head before the parenthesis
    head = _clean(re.sub(r"\(.*?\)", "", c))
    if head in idx:
        return idx[head]
    return skill.strip().strip(" .,;:-•*")


def split_compound(skill: str) -> list[str]:
    """'AWS (ECS, RDS, S3)' -> ['AWS', 'ECS', 'RDS', 'S3'];  'Stripe/Razorpay integration' stays."""
    m = re.match(r"^(.*?)\((.*)\)\s*$", skill.strip())
    if not m:
        return [skill]
    head, inner = m.group(1).strip(), m.group(2)
    parts = [head] if head else []
    parts += [p.strip() for p in re.split(r"[,;]", inner) if p.strip()]
    return parts


def implied(canon: str, _seen=None) -> set[str]:
    """Transitive closure of 'implies' for a canonical skill."""
    _seen = _seen or set()
    out = set()
    for imp in TAXONOMY.get(canon, ([], []))[1]:
        if imp not in _seen:
            _seen.add(imp)
            out.add(imp)
            out |= implied(imp, _seen)
    return out


def normalize_list(skills: list[str]) -> list[str]:
    seen, out = set(), []
    for s in skills or []:
        for part in split_compound(s):
            n = normalize(part)
            if n and n.lower() not in seen:
                seen.add(n.lower())
                out.append(n)
    return out


# Aliases too ambiguous to trust in free text ("the rest of", "go to", "ML" is fine in a skills
# list but not as evidence). They still work for normalising explicit skill lists.
AMBIGUOUS = {"r", "go", "shell", "rest", "express", "glue", "node", "ml", "cv", "dl", "tf", "ts",
             "rtl", "pbi", "py", "forecasting", "classification", "regression", "visualization",
             "visualisation", "dashboards", "dashboarding", "accessibility", "gpt", "llama", "torch",
             "emr", "chroma", "alerting", "observability", "shell", "spring", "testing library", "lambda",
             "lean", "inventory", "partnerships", "proposals", "screening", "sourcing", "induction", "kpis",
             "mis", "sla", "pf", "esi", "ats", "lever", "greenhouse", "appraisals", "prospecting", "comparables",
             "newsletters", "social media", "forecasting", "budget management", "dcf", "gtm", "rfp",
             "ecs", "rds", "s3", "ec2", "experimentation", "transformers", "hugging face", "tableau desktop"}


def _term_pattern(term: str) -> re.Pattern:
    esc = re.escape(_clean(term)).replace(r"\ ", r"\s+")
    return re.compile(rf"(?<![\w+#.]){esc}(?![\w+#])", re.I)


@lru_cache(maxsize=1)
def _scan_patterns() -> list[tuple[re.Pattern, str]]:
    pats = []
    for canon, (aliases, _) in TAXONOMY.items():
        for term in [canon] + aliases:
            t = _clean(term)
            if t in AMBIGUOUS or len(t) <= 1:
                continue
            pats.append((_term_pattern(t), canon))
    pats.sort(key=lambda p: -len(p[0].pattern))  # longest first: 'spring boot' before 'spring'
    return pats


def scan_text(text: str) -> list[str]:
    """Find canonical skills mentioned anywhere in free text."""
    found, seen = [], set()
    for pat, canon in _scan_patterns():
        if canon not in seen and pat.search(text):
            seen.add(canon)
            found.append(canon)
    return found


def mentions(text: str, canon: str) -> bool:
    """Does the free text mention this canonical skill (by any unambiguous alias)?"""
    for term in [canon] + TAXONOMY.get(canon, ([], []))[0]:
        t = _clean(term)
        if t in AMBIGUOUS or len(t) <= 1:
            continue
        if _term_pattern(t).search(text):
            return True
    return False


def mention_spans(text: str, canon: str) -> list[tuple[int, int]]:
    """All (start, end) spans where the skill is mentioned, de-duplicated across aliases."""
    spans = set()
    for term in [canon] + TAXONOMY.get(canon, ([], []))[0]:
        t = _clean(term)
        if t in AMBIGUOUS or len(t) <= 1:
            continue
        spans |= {m.span() for m in _term_pattern(t).finditer(text)}
    return sorted(spans)


def are_false_friends(a: str, b: str) -> bool:
    return frozenset({a.lower(), b.lower()}) in FALSE_FRIENDS
