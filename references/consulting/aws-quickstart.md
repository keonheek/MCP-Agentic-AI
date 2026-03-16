# AWS Quickstart — Consulting Technical Gap Closure

_Purpose: Close the "no cloud platform experience" gap for McKinsey QuantumBlack, BCG Gamma, Deloitte Korea AI, Accenture Song._
_Time budget: 1-2 days to have one deployable project._

---

## Why AWS Specifically

| Firm | Cloud Platform | Why It Matters |
|------|---------------|----------------|
| McKinsey QuantumBlack | AWS + Databricks on AWS | QB uses AWS-native services; Kedro/Airflow deployed on EC2/ECS |
| BCG Gamma | AWS / GCP / Azure (client-dependent) | Show cloud awareness, not just one platform |
| Deloitte Korea AI | Azure (primary) + AWS | Deloitte uses both; Azure preferred for enterprise, AWS for data |
| Accenture Song / AI | Azure (primary) | Azure AI-900 cert directly relevant |

**Priority: AWS first** (covers McKinsey QB directly, satisfies "cloud-aware" for BCG/Deloitte). Azure AI-900 is a 1-week cert — do that separately before Accenture deadline.

---

## Recommended Project: Deploy FinAgent API to AWS Lambda

This gives you: "I deployed FinAgent's FastAPI backend to AWS Lambda with API Gateway." — one sentence that closes the cloud gap for all targets.

### What You're Building

```
[User] → [API Gateway] → [Lambda] → [FastAPI app] → [OpenAI API]
                                          ↓
                                    [SQLite layer or S3 for DB file]
```

### Step 1: Set Up AWS Free Tier (15 min)

1. Go to aws.amazon.com → Create Free Tier account
2. Free tier includes:
   - Lambda: 1M requests/month free
   - API Gateway: 1M API calls/month free
   - S3: 5 GB storage free
   - CloudWatch: basic monitoring free
3. Install AWS CLI:
   ```bash
   pip install awscli
   aws configure  # enter Access Key ID, Secret Access Key, region: ap-northeast-2 (Seoul)
   ```

### Step 2: Install Mangum (Lambda adapter for FastAPI)

```bash
pip install mangum
```

Wrap the FastAPI app for Lambda:

```python
# main.py — add at the bottom
from mangum import Mangum
handler = Mangum(app)
```

That's the only code change needed.

### Step 3: Package for Lambda

```bash
# Create deployment package
pip install -r requirements.txt --target ./package
cd package
zip -r ../deployment.zip .
cd ..
zip deployment.zip main.py  # and any other files needed
```

### Step 4: Deploy via AWS Console (GUI — fastest for first time)

1. AWS Console → Lambda → Create function
2. Runtime: Python 3.11 (Lambda doesn't support 3.14 yet)
3. Upload deployment.zip
4. Set environment variables: `OPENAI_API_KEY`, etc.
5. Add API Gateway trigger → creates HTTPS endpoint automatically

### Step 5: Test

```bash
curl https://YOUR_API_ID.execute-api.ap-northeast-2.amazonaws.com/prod/query \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"query": "삼성전자 2024년 매출은?"}'
```

---

## Faster Alternative: AWS EC2 (Less Resume Value, Faster Setup)

If Lambda feels complex, deploy to EC2 instead (~30 min):

```bash
# From local machine
ssh -i your-key.pem ec2-user@YOUR_EC2_IP

# On EC2
sudo yum install python3 git -y
git clone https://github.com/keonhee3337-art/FinAgent
cd FinAgent
pip3 install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 &
```

Resume line: "Deployed FinAgent to AWS EC2 (Python, FastAPI, Amazon Linux)."

Lambda is better — "serverless architecture" is more impressive and directly relevant to McKinsey QB's AWS Lambda usage.

---

## Key AWS Concepts to Know Cold

For McKinsey QuantumBlack technical conversations:

| Concept | What It Is | Why It Matters |
|---------|-----------|----------------|
| **Lambda** | Serverless compute — code runs on demand, no server management | QB deploys microservices on Lambda |
| **S3** | Object storage (files, models, datasets) | Data lake foundation; all ML pipelines read from S3 |
| **EC2** | Virtual machine in the cloud | General compute; training, batch jobs |
| **RDS / Aurora** | Managed relational DB (PostgreSQL, MySQL) | Production DBs; replaces local SQLite |
| **SageMaker** | Managed ML platform | Training + deploying ML models; QB uses this |
| **Glue** | Serverless ETL | Data pipeline orchestration; similar to Airflow |
| **IAM** | Identity and access management | Controls who can access what — always comes up |
| **API Gateway** | HTTP API layer in front of Lambda | The public URL for any Lambda function |
| **CloudWatch** | Monitoring + logging | How you debug Lambda; logs go here |

---

## One-Week Learning Path (Parallel with Applications)

**Day 1 (2-3 hrs):** AWS Free Tier setup + deploy FinAgent to Lambda
**Day 2 (1-2 hrs):** Add S3 for the SQLite database file (replaces local path)
**Day 3 (1 hr):** Set up CloudWatch dashboard — shows request volume, latency
**Day 4-5:** Azure AI-900 certification prep (if Accenture is a priority)
**Day 6:** Update GitHub README to mention AWS Lambda deployment
**Day 7:** Update LinkedIn headline to add "AWS Lambda"

---

## Interview Talking Point

> "I deployed FinAgent's FastAPI backend to AWS Lambda with API Gateway — so it's no longer dependent on Streamlit Cloud. The SQLite database sits on S3. This was my first serverless deployment and it actually improved cold start time compared to a persistent EC2 instance for a low-traffic service."

Why this works:
- Shows you know the tradeoffs (Lambda cold start vs EC2 always-on)
- Shows you understand data storage separately from compute (S3 vs local)
- Connects to what McKinsey QuantumBlack actually builds for clients
- One project, one day of work, closes the cloud gap permanently

---

## After AWS: Azure AI-900 (Accenture)

Accenture uses Azure primarily. AI-900 is the entry-level Azure AI cert.

- Free study material: microsoft.com/learn → AI-900 learning path
- Exam: ~$165 USD (take after free prep)
- Prep time: 1 week of 1-2 hrs/day
- Covering: Azure AI services, cognitive services, ML fundamentals, responsible AI

This is optional — Accenture will not require this cert for an intern interview, but having it is a differentiator. Do it if the Accenture deadline is approaching and you have a week.
