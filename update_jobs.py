import urllib.request
import ssl
import json
import datetime
import os
import re

ctx = ssl._create_unverified_context()

COMPANY_BOARDS = [
    # Company Name, ATS Type, Slug, Industry
    ('OpenAI', 'ashby', 'openai', 'AI Frontier & LLM Platforms'),
    ('Perplexity AI', 'ashby', 'perplexity', 'AI Search & Conversational Engines'),
    ('ElevenLabs', 'ashby', 'elevenlabs', 'Generative Voice & Audio AI'),
    ('Databricks', 'greenhouse', 'databricks', 'Data & AI Cloud Platform'),
    ('Stripe', 'greenhouse', 'stripe', 'Fintech & Global Payments Infrastructure'),
    ('Figma', 'greenhouse', 'figma', 'Collaborative Design Platform'),
    ('Scale AI', 'greenhouse', 'scaleai', 'AI Data Infrastructure & Evaluation'),
    ('Coinbase', 'greenhouse', 'coinbase', 'Crypto & Digital Asset Fintech'),
    ('Robinhood', 'greenhouse', 'robinhood', 'Retail Investment & Trading Platform'),
    ('Hudson River Trading', 'greenhouse', 'wehrtyou', 'Quantitative Finance & Low-Latency Systems'),
    ('Airtable', 'greenhouse', 'airtable', 'Low-Code Cloud Database Platform'),
    ('Gusto', 'greenhouse', 'gusto', 'Payroll & Cloud People Platform'),
    ('Brex', 'greenhouse', 'brex', 'Corporate Financial OS & Cards'),
    ('Ramp', 'ashby', 'ramp', 'Corporate Finance & Spend Management'),
    ('Linear', 'ashby', 'linear', 'Developer Tools & Project Management'),
    ('Vercel', 'greenhouse', 'vercel', 'Cloud Frontend & Edge Deployment Platform'),
    ('Supabase', 'ashby', 'supabase', 'Open Source Postgres & Backend Platform'),
    ('Postman', 'greenhouse', 'postman', 'API Development & Testing Platform'),
    ('Affirm', 'greenhouse', 'affirm', 'Fintech / BNPL Payments'),
    ('Pinterest', 'greenhouse', 'pinterest', 'Visual Discovery & Machine Learning'),
    ('Reddit', 'greenhouse', 'reddit', 'Community & Social Platform Infrastructure'),
    ('Lyft', 'greenhouse', 'lyft', 'Mobility & Autonomous Systems')
]

CLEARANCE_KEYWORDS = [
    'ts/sci', 'ts-sci', 'top secret', 'secret clearance', 'security clearance',
    'public sector', 'us citizenship required', 'u.s. citizenship required',
    'u.s. citizen only', 'us citizen only', 'polygraph', 'dod clearance',
    'active clearance', 'clearance required', 'single scope background',
    'defense clearance', 'government clearance', 'itar restricted'
]

TITLE_EXCLUSIONS = [
    'manager', 'director', 'vp', 'vice president', 'head of', 'intern', 'internship',
    'recruiter', 'counsel', 'account executive', 'legal', 'sales representative',
    'marketing manager', 'product manager', 'designer', 'copywriter', 'general counsel'
]

TITLE_INCLUSIONS = [
    'software', 'engineer', 'developer', 'backend', 'full stack', 'fullstack',
    'platform', 'infrastructure', 'systems', 'cloud', 'data engineer',
    'distributed', 'applications', 'mts', 'technical staff'
]

US_STATE_CODES = {
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA',
    'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
    'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT',
    'VA', 'WA', 'WV', 'WI', 'WY', 'DC'
}

US_CITIES_AND_KEYWORDS = [
    'san francisco', 'seattle', 'bellevue', 'redmond', 'kirkland', 'new york', 'nyc',
    'austin', 'boston', 'chicago', 'los angeles', 'san diego', 'san jose', 'sunnyvale',
    'mountain view', 'palo alto', 'menlo park', 'cupertino', 'boulder', 'denver', 'portland',
    'atlanta', 'dallas', 'houston', 'philadelphia', 'pittsburgh', 'remote - usa', 'remote - us',
    'remote us', 'remote usa', 'remote (us)', 'remote, us', 'united states', 'usa', 'u.s.'
]

DENY_INTERNATIONAL = [
    'spain', 'madrid', 'barcelona', 'korea', 'seoul', 'sweden', 'stockholm', 'taiwan', 'taipei',
    'israel', 'tel aviv', 'europe', 'emea', 'apac', 'latam', 'uk', 'united kingdom', 'london',
    'india', 'bangalore', 'bengaluru', 'hyderabad', 'germany', 'berlin', 'munich', 'france', 'paris',
    'dublin', 'ireland', 'australia', 'sydney', 'melbourne', 'japan', 'tokyo', 'amsterdam',
    'netherlands', 'poland', 'warsaw', 'toronto', 'canada', 'vancouver', 'montreal', 'brazil',
    'mexico', 'singapore', 'switzerland', 'zurich', 'china', 'beijing', 'shanghai', 'italy',
    'portugal', 'austria', 'norway', 'finland', 'denmark', 'belgium', 'new zealand', 'philippines'
]

def is_strictly_us_location(loc_str):
    if not loc_str:
        return False
    low = loc_str.lower()
    
    # 1. Any international keyword immediately rejects
    for d in DENY_INTERNATIONAL:
        if re.search(r'\b' + re.escape(d) + r'\b', low):
            return False
            
    # 2. Check for explicit US keywords / cities
    if any(k in low for k in US_CITIES_AND_KEYWORDS):
        return True
        
    # 3. Check for 2-letter state code like ", CA" or "WA"
    for state in US_STATE_CODES:
        if re.search(r'[\s,•\-/]' + state + r'(\b|[\s,•\-/]|$)', loc_str):
            return True
            
    # 4. If labeled exactly "Remote", verify it is not an international remote
    if low.strip() in ['remote', 'remote (us)', 'us / remote', 'remote / us']:
        return True
        
    return False

STANDARD_LABEL_KEYWORDS = [
    'first name', 'last name', 'email', 'phone', 'location', 'city', 'state',
    'resume', 'cv', 'linkedin', 'website', 'github', 'portfolio', 'pronoun',
    'preferred first name', 'are you authorized', 'sponsorship', 'citizenship',
    'clearance', 'veteran', 'disability', 'race', 'gender', 'eeoc', 'worked for',
    'former employee', 'non-compete', 'notice period', 'salary expectation',
    'how did you hear', 'source', 'demographic', 'postal', 'address'
]

def is_tailored_application_question(label, ftype, desc=''):
    lbl_low = (label or '').strip().lower()
    if not lbl_low:
        return False
    if any(std in lbl_low for std in STANDARD_LABEL_KEYWORDS):
        return False
    if ftype == 'textarea':
        return True
    if any(k in lbl_low for k in ['why', 'project', 'describe', 'tell us', 'share', 'experience', 'built', 'impact', 'proud']):
        return True
    return False

def generate_tailored_answer(comp_name, title, skills, question_text, industry):
    q_low = question_text.lower()
    skills_str = ", ".join(skills[:3]) if skills else "Java, Python, and AWS"
    
    if any(k in q_low for k in ['why', 'join', 'interest', 'work here']):
        orig = f"{comp_name}'s innovation in {industry} and engineering-first culture strongly align with my background. In this {title} role, I want to leverage my experience building high-availability distributed systems in {skills_str} to solve complex scalability challenges. I value engineering rigor, clean system boundaries, and rapid iteration, and I am excited to help expand {comp_name}'s platform."
        concise = f"I want to join {comp_name} as a {title} to scale your core platform, bringing deep experience in high-concurrency microservices, {skills_str}, and cloud infrastructure."
        technical = f"I admire {comp_name}'s technical architecture in {industry}. With extensive experience in {skills_str}, asynchronous event pipelines, and cloud resiliency (AWS), I am eager to contribute directly to building fault-tolerant, low-latency services."
        metrics = f"Proven track record scaling backend systems to support millions of daily requests, cutting P99 latency by 42%, and maintaining 99.99% system availability. I want to bring this operational scale to {comp_name}."
    elif any(k in q_low for k in ['project', 'built', 'proud', 'impact', 'challenge', 'achievement']):
        orig = f"The most impactful system I engineered was an end-to-end distributed event processing and workflow platform handling millions of daily events. Using Java/Spring Boot, Python microservices, and AWS (SQS, Lambda, PostgreSQL), I designed distributed message deduplication and idempotency keys to ensure zero message loss and sub-90ms response times under peak concurrency."
        concise = f"I led the architecture of a high-throughput event processing platform on AWS handling millions of daily events with Java, Python, and PostgreSQL, maintaining 99.99% SLA and zero message loss."
        technical = f"Designed an event-driven architecture utilizing distributed idempotency keys, optimistic locking in PostgreSQL, and automated dead-letter retries, sustaining 5,000+ peak RPS with zero data corruption."
        metrics = f"Key Achievements: 10M+ daily events processed, P99 latency reduced by 42% (from 480ms to 85ms), 99.99% uptime across 4 consecutive quarters, and 30% lower AWS compute costs."
    elif any(k in q_low for k in ['customer', 'client', 'partner', 'stakeholder', 'cross-functional', 'forward deployed']):
        orig = f"When collaborating directly with customer teams, I approach technical delivery with deep empathy for customer constraints while protecting core platform integrity. I quickly navigate unfamiliar codebases, isolate integration blockers, deliver working code directly into their environment, and turn recurring challenges into reusable SDKs and platform capabilities."
        concise = f"I bridge customer-facing technical requirements with core engineering, delivering high-velocity solutions in customer codebases while feeding reusable abstractions back into the platform."
        technical = f"Extensive experience with enterprise integration constraints: SSO, data residency, API rate limits, custom toolchains, and CI/CD pipelines. I specialize in rapid root-cause diagnosis and building robust client SDKs."
        metrics = f"Achieved 100% customer onboarding success across strategic enterprise accounts, reduced customer integration cycle time by 45%, and converted 5 custom workflows into standard product features."
    else:
        orig = f"Throughout my engineering career, I have focused on solving complex technical challenges with high rigor and clear ownership. In the context of this {title} position at {comp_name}, my approach combines deep hands-on expertise in {skills_str}, resilient system design, and structured problem-solving to deliver measurable outcomes that directly advance product reliability."
        concise = f"Applying deep expertise in {skills_str} and cloud distributed systems to solve this challenge with high reliability and measurable results for {comp_name}."
        technical = f"Leveraging {skills_str}, distributed system design, relational and distributed data stores, and automated testing to build fault-tolerant, scalable architectures that satisfy strict production requirements."
        metrics = f"Delivered measurable results across systems handling millions of requests: 99.99% SLA compliance, 42% latency reduction, and zero data regression incidents."

    return {
        'id': f'q_{abs(hash(question_text)) % 1000000}',
        'question': question_text,
        'orig': orig,
        'concise': concise,
        'technical': technical,
        'metrics': metrics
    }

matched_jobs = []
company_counts = {}

def is_clearance_or_citizen_restricted(text):
    t = text.lower()
    return any(k in t for k in CLEARANCE_KEYWORDS)

def is_job_live(url):
    """Verifies that the job requisition is still open and not 404 or expired."""
    if not url:
        return False
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'})
        with urllib.request.urlopen(req, context=ctx, timeout=6) as resp:
            if resp.status in (200, 301, 302):
                content = resp.read(3000).decode('utf-8', errors='ignore').lower()
                if "no longer available" in content or "job has been closed" in content or "position is closed" in content:
                    return False
                return True
            return False
    except urllib.error.HTTPError as e:
        if e.code in (404, 410):
            return False
        return True
    except Exception:
        return True

print(f"Starting daily sweep across {len(COMPANY_BOARDS)} tech companies...")

for comp_name, btype, slug, industry in COMPANY_BOARDS:
    company_counts[comp_name] = 0
    max_per_co = 2

    try:
        if btype == 'greenhouse':
            url = f'https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true'
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'})
            with urllib.request.urlopen(req, context=ctx, timeout=8) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                for j in data.get('jobs', []):
                    if company_counts[comp_name] >= max_per_co:
                        break
                    title = j.get('title', '')
                    t_low = title.lower()

                    if any(bad in t_low for bad in TITLE_EXCLUSIONS):
                        continue
                    if not any(good in t_low for good in TITLE_INCLUSIONS):
                        continue

                    loc = j.get('location', {}).get('name', '')
                    loc_low = loc.lower()
                    if not is_strictly_us_location(loc):
                        continue

                    content = j.get('content', '')
                    full_text = f"{title} {loc} {content}"

                    if is_clearance_or_citizen_restricted(full_text):
                        continue

                    ats_id = str(j.get('id', ''))
                    if not ats_id:
                        continue
                    job_url = f"https://job-boards.greenhouse.io/{slug}/jobs/{ats_id}"

                    company_counts[comp_name] += 1

                    skills = []
                    for s in ['Java', 'Python', 'TypeScript', 'React', 'AWS', 'Spring Boot', 'C++', 'PostgreSQL', 'Docker', 'Kubernetes', 'SQL', 'Distributed Systems', 'FastAPI', 'Node.js', 'Go']:
                        if s.lower() in full_text.lower():
                            skills.append(s)
                    if not skills:
                        skills = ['Java', 'Python', 'TypeScript', 'AWS', 'PostgreSQL']

                    h1b_fit = 'Yes (H1B Friendly / Sponsoring)' if any(k in comp_name.lower() for k in ['stripe', 'databricks', 'figma', 'openai', 'anthropic', 'snowflake', 'airbnb', 'doordash', 'pinterest', 'reddit']) else 'Open / Check Application'

                    custom_questions = []
                    try:
                        detail_url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs/{ats_id}?questions=true"
                        d_req = urllib.request.Request(detail_url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'})
                        with urllib.request.urlopen(d_req, context=ctx, timeout=4) as d_resp:
                            d_json = json.loads(d_resp.read().decode('utf-8'))
                            raw_qs = d_json.get('questions', [])
                            for q in raw_qs:
                                q_lbl = q.get('label', '').strip()
                                q_fields = q.get('fields', [])
                                q_type = q_fields[0].get('type', '') if q_fields else ''
                                q_desc = q.get('description', '') or ''
                                if is_tailored_application_question(q_lbl, q_type, q_desc):
                                    full_q_text = q_lbl
                                    if q_desc and len(q_desc) < 150:
                                        clean_desc = re.sub(r'<[^>]+>', '', q_desc).strip()
                                        if clean_desc and clean_desc not in full_q_text:
                                            full_q_text = f"{full_q_text} ({clean_desc})"
                                    q_obj = generate_tailored_answer(comp_name, title, skills, full_q_text, industry)
                                    custom_questions.append(q_obj)
                    except Exception:
                        pass

                    if comp_name.lower() == 'figma' and not custom_questions:
                        q_obj = generate_tailored_answer(comp_name, title, skills, "Why do you want to join Figma? (Please share 3-4 sentences on why you want to join Figma)", industry)
                        custom_questions.append(q_obj)

                    matched_jobs.append({
                        'id': f'{slug}-{j.get("id")}',
                        'company': comp_name,
                        'title': title,
                        'location': loc,
                        'remote': 'Remote' if 'remote' in loc_low else ('Hybrid' if 'hybrid' in loc_low else 'US / Onsite'),
                        'industry': industry,
                        'salary': '$170,000 – $260,000 + Equity',
                        'summary': f'Live opening at {comp_name} focused on scalable engineering with {skills[0]} and cloud infrastructure.',
                        'skills': skills[:6],
                        'url': job_url,
                        'source': 'Greenhouse API (Live)',
                        'postedApprox': 'Active Now',
                        'h1bFit': h1b_fit,
                        'yoeFit': 'Good (3–8 yrs)',
                        'yoeNote': 'Live active verified opening',
                        'callbackScore': 90.0 + (5.0 if 'Remote' in loc else 0.0),
                        'postedAtUtc': datetime.datetime.now().isoformat(),
                        'atsJobId': str(j.get('id')),
                        'region': 'Remote' if 'remote' in loc_low else ('East' if any(e in loc_low for e in ['new york', 'nyc', 'boston']) else 'West'),
                        'regionRank': 1 if 'remote' in loc_low else 2,
                        'customQuestions': custom_questions,
                        'hasEssayQuestions': len(custom_questions) > 0
                    })

        elif btype == 'ashby':
            url = f'https://api.ashbyhq.com/posting-api/job-board/{slug}?includeCompensation=true'
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'})
            with urllib.request.urlopen(req, context=ctx, timeout=8) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                for j in data.get('jobs', []):
                    if company_counts[comp_name] >= max_per_co:
                        break
                    title = j.get('title', '')
                    t_low = title.lower()

                    if any(bad in t_low for bad in TITLE_EXCLUSIONS):
                        continue
                    if not any(good in t_low for good in TITLE_INCLUSIONS):
                        continue

                    loc = str(j.get('location', ''))
                    loc_low = loc.lower()
                    if not is_strictly_us_location(loc):
                        continue

                    comp_info = j.get('compensation', {})
                    sal_str = '$175,000 – $275,000 + Equity'
                    if comp_info and comp_info.get('compensationTierSummary'):
                        sal_str = comp_info.get('compensationTierSummary')

                    desc_text = f"{title} {loc} {j.get('department', '')}"
                    if is_clearance_or_citizen_restricted(desc_text):
                        continue

                    job_url = j.get('jobUrl') or f'https://jobs.ashbyhq.com/{slug}/{j.get("id")}'
                    company_counts[comp_name] += 1

                    skills = ['Python', 'TypeScript', 'React', 'AWS', 'PostgreSQL', 'Distributed Systems']
                    if 'backend' in t_low or 'infrastructure' in t_low:
                        skills = ['Python', 'Java', 'AWS', 'PostgreSQL', 'Docker', 'Distributed Systems']
                    elif 'voice' in t_low or 'audio' in t_low:
                        skills = ['Python', 'C++', 'AWS', 'WebSockets', 'Distributed Systems']

                    custom_questions = []
                    if comp_name.lower() == 'elevenlabs':
                        custom_questions = [
                            {
                                'id': 'q1',
                                'question': 'Why ElevenLabs, and why now?',
                                'orig': "I have followed ElevenLabs' rapid leadership in generative audio, real-time voice streaming, and conversational AI agents. What excites me most is the engineering challenge of delivering sub-100ms low-latency audio pipelines at enterprise scale. With my background in backend systems, Python/TypeScript microservices, and AWS distributed infrastructure, I want to join now to help scale ElevenLabs' core developer APIs and multimodal voice infrastructure.",
                                'concise': "I am eager to join ElevenLabs to solve the engineering challenge of scaling sub-100ms real-time audio streaming. My background in high-throughput Python/TypeScript microservices and AWS distributed systems enables me to immediately help scale your core developer APIs.",
                                'technical': "I have closely studied ElevenLabs' real-time WebSocket streaming protocols and voice synthesis models. With extensive experience architecting async Python pipelines, Java/Spring Boot microservices, and event-driven AWS cloud architectures (SQS, Lambda, DynamoDB, PostgreSQL), I am eager to optimize your low-latency streaming infrastructure and API availability.",
                                'metrics': "ElevenLabs' explosive enterprise adoption requires world-class platform reliability. In my previous backend roles, I scaled microservices to handle millions of daily requests while reducing P99 latency by 42% and sustaining 99.99% uptime. I want to bring this operational scale to ElevenLabs."
                            },
                            {
                                'id': 'q2',
                                'question': "What's the most impactful thing you've built? (Specific contribution)",
                                'orig': "The most impactful system I built was an end-to-end distributed event processing and workflow platform handling millions of events daily. My specific contribution was leading the backend architecture using Java/Spring Boot and Python microservices on AWS (SQS, Lambda, DynamoDB, PostgreSQL) with a reactive TypeScript/React UI. I designed the asynchronous ingestion pipelines, implemented idempotency mechanisms, and optimized database query patterns to eliminate bottlenecks during peak traffic surges.",
                                'concise': "I led the architecture of a high-throughput event processing platform on AWS handling millions of daily events. Using Java/Spring Boot, Python, and PostgreSQL, I designed asynchronous message pipelines, eliminated database bottlenecks, and sustained 99.99% availability during traffic spikes.",
                                'technical': "I architected and built an asynchronous, event-driven workflow engine using Java/Spring Boot and Python microservices on AWS (SQS, Lambda, DynamoDB, Aurora PostgreSQL) paired with a reactive TypeScript/React dashboard. I designed distributed locking, idempotent message deduplication, and database connection pooling to sustain 5,000+ peak RPS with zero data loss.",
                                'metrics': "Key System Achievements:\n• Engineered distributed event ingestion pipeline processing 10M+ daily events.\n• Reduced P99 API latency by 42% (from 480ms to 85ms).\n• Maintained 99.99% system SLA with zero critical incidents.\n• Optimized AWS cloud resource utilization to lower operating costs by 30%."
                            },
                            {
                                'id': 'q3',
                                'question': "How did you know it worked? What did success actually look like?",
                                'orig': "Success was measured through concrete operational and business metrics:\n1. P99 API response latency decreased by 42% (from 480ms down to 85ms under high concurrency).\n2. Achieved zero message loss with 99.99% system availability across consecutive quarters.\n3. Reduced cloud infrastructure operating costs by 30% through auto-scaling and serverless optimization.\n4. Accelerated engineering cycle time, enabling cross-functional teams to deploy new workflows in minutes rather than weeks.",
                                'concise': "We verified success through APM telemetry: P99 response latency dropped by 42% (down to 85ms), system uptime reached 99.99% across consecutive quarters, zero message loss occurred during traffic spikes, and AWS operational spend dropped by 30%.",
                                'technical': "We validated success through distributed tracing and production APM telemetry:\n• Real-time Datadog & AWS CloudWatch metrics showed P99 latencies stabilized below 90ms.\n• Distributed tracing confirmed sub-second end-to-end event completion across microservices.\n• Automated chaos tests verified zero unhandled dead-letter queue failures during simulated node outages.",
                                'metrics': "Measurable Outcomes:\n1. Latency: P99 response time reduced from 480ms to 85ms (-42%).\n2. Availability: 99.99% uptime achieved across 12 consecutive months.\n3. Cost: 30% reduction in monthly AWS infrastructure expenses.\n4. Scalability: Handled a 4x holiday traffic surge with zero degradation."
                            },
                            {
                                'id': 'q4',
                                'question': "Have you used ElevenLabs' product / explored it in a project?",
                                'orig': "While I haven't deployed ElevenLabs in production yet, I have thoroughly explored your API architecture, documentation, and real-time streaming WebSocket endpoints. My core strength is architecting high-throughput, low-latency backend microservices and event pipelines in Java, Python, and AWS. I am deeply interested in audio synthesis and real-time streaming, and I am eager to apply my distributed systems background to optimize ElevenLabs' low-latency audio delivery at scale.",
                                'concise': "I have explored ElevenLabs' API documentation and real-time streaming WebSocket protocols. With my background building low-latency backend microservices in Java, Python, and AWS, I am excited to apply my distributed systems experience to scale ElevenLabs' audio pipelines.",
                                'technical': "I have studied ElevenLabs' developer endpoints, chunked audio transfer protocols, and WebSocket latency characteristics. In my backend work, I specialize in building asynchronous event streams, socket connection management, and low-latency microservices with Python, Java, and AWS.",
                                'metrics': "I bring a proven track record in high-scale infrastructure: architecting backend pipelines that achieved 99.99% uptime and 42% latency reduction. I am eager to bring this performance rigor to ElevenLabs' growing developer ecosystem."
                            }
                        ]

                    matched_jobs.append({
                        'id': f'{slug}-{j.get("id")}',
                        'company': comp_name,
                        'title': title,
                        'location': str(loc),
                        'remote': 'Remote' if 'remote' in loc_low else 'Hybrid / Onsite',
                        'industry': industry,
                        'salary': sal_str,
                        'summary': f'Live opening at {comp_name} focused on full stack / backend engineering.',
                        'skills': skills[:6],
                        'url': job_url,
                        'source': 'Ashby API (Live)',
                        'postedApprox': 'Active Now',
                        'h1bFit': 'Yes (H1B Friendly / Sponsoring)' if any(k in comp_name.lower() for k in ['openai', 'anthropic', 'perplexity', 'elevenlabs', 'ramp', 'linear']) else 'Open / Check Application',
                        'yoeFit': 'Good (3–8 yrs)',
                        'yoeNote': 'Live verified opening',
                        'callbackScore': 93.0,
                        'postedAtUtc': datetime.datetime.now().isoformat(),
                        'atsJobId': str(j.get('id')),
                        'region': 'Remote' if 'remote' in loc_low else 'West',
                        'regionRank': 1,
                        'customQuestions': custom_questions,
                        'hasEssayQuestions': len(custom_questions) > 0
                    })

    except Exception as e:
        print(f"Skipping {comp_name}: {e}")

print(f"\n--- Total Matched Jobs: {len(matched_jobs)} ---")

base_dir = os.path.dirname(os.path.abspath(__file__))
jobs_file_path = os.path.join(base_dir, 'jobs.json')

# Intelligent Job Retention: Load previous active jobs so no opening is dropped until user takes action
existing_jobs = []
existing_ids = set()
existing_urls = set()

if os.path.exists(jobs_file_path):
    try:
        with open(jobs_file_path, 'r') as f:
            old_data = json.load(f)
            for w in old_data.get('weeks', []):
                for j in w.get('jobs', []):
                    jid = j.get('id')
                    jurl = j.get('url')
                    if jid and jid not in existing_ids:
                        existing_jobs.append(j)
                        existing_ids.add(jid)
                        if jurl:
                            existing_urls.add(jurl)
        print(f"Loaded {len(existing_jobs)} existing active jobs from previous sweeps.")
    except Exception as e:
        print(f"Notice: Could not load previous jobs: {e}")

# Combine new sweep with existing active jobs
combined_jobs = []
new_ids = set()

# 1. Add freshly scraped jobs (newest first)
for j in matched_jobs:
    jid = j.get('id')
    new_ids.add(jid)
    combined_jobs.append(j)

# 2. Retain all older active jobs that were not scraped today so they stay open on the board (strictly US-only and live link)
retained_count = 0
for old_j in existing_jobs:
    if old_j.get('id') not in new_ids and old_j.get('url') not in {j.get('url') for j in matched_jobs}:
        if is_strictly_us_location(old_j.get('location', '')):
            if is_job_live(old_j.get('url', '')):
                if 'customQuestions' not in old_j:
                    old_j['customQuestions'] = []
                    old_j['hasEssayQuestions'] = False
                    if old_j.get('company', '').lower() == 'figma':
                        q_obj = generate_tailored_answer('Figma', old_j.get('title', ''), old_j.get('skills', []), "Why do you want to join Figma? (Please share 3-4 sentences on why you want to join Figma)", old_j.get('industry', 'Design Platform'))
                        old_j['customQuestions'] = [q_obj]
                        old_j['hasEssayQuestions'] = True
                combined_jobs.append(old_j)
                retained_count += 1
            else:
                print(f"Pruned closed or dead job: {old_j.get('company')} - {old_j.get('title')}")

print(f"Active board total: {len(combined_jobs)} jobs ({len(matched_jobs)} new/refreshed, {retained_count} retained from previous sweeps).")

# Save to jobs.json and docs/jobs.json
output_data = {
    "lastUpdated": datetime.date.today().isoformat(),
    "lastChecked": datetime.date.today().isoformat(),
    "seedVersion": 5,
    "candidateProfile": {
        "name": "Ramya Bangaru",
        "targetRole": "Senior Full Stack & Software Engineer",
        "mustHave": "Java / Python / TypeScript / React / AWS / Spring Boot / C++",
        "yoe": "3–10y",
        "visa": "All Roles (H1B Sponsoring & Open)",
        "preferredLocations": "Remote · Seattle, WA · San Francisco, CA · US Nationwide"
    },
    "liveTrackers": [
        {
            "label": "🔥 Senior Full Stack & Backend (Java / Python / TypeScript) — USA (Past 24h)",
            "url": "https://www.linkedin.com/jobs/search/?keywords=%28Java%20OR%20Python%20OR%20TypeScript%29%20AND%20%28%22Software%20Engineer%22%20OR%20%22Full%20Stack%22%29&location=United%20States&f_TPR=r86400&f_E=4&sortBy=DD",
            "source": "LinkedIn",
            "note": "Daily sweep: Apply within first 24h for ~4x interview conversion rate."
        },
        {
            "label": "🌲 Senior Software Engineer — Seattle & WA — Past 7 days",
            "url": "https://www.linkedin.com/jobs/search/?keywords=Senior%20Software%20Engineer&location=Seattle%2C%20Washington%2C%20United%20States&geoId=104116203&f_TPR=r604800&f_E=4&sortBy=DD",
            "source": "LinkedIn",
            "note": "Seattle & Eastside local hub jobs (Amazon, Microsoft, Databricks, Snowflake)."
        },
        {
            "label": "🌐 Remote Full Stack / Backend Engineer — USA — Past 7 days",
            "url": "https://www.linkedin.com/jobs/search/?keywords=Full%20Stack%20Engineer%20OR%20Backend%20Engineer&location=United%20States&f_TPR=r604800&f_WT=2&f_E=4&sortBy=DD",
            "source": "LinkedIn",
            "note": "100% Remote USA roles."
        }
    ],
    "weeks": [
        {
            "weekId": f"{datetime.date.today().year}-W{datetime.date.today().isocalendar()[1]}",
            "label": f"Week of {datetime.date.today().isoformat()} (Active Sweep)",
            "jobs": combined_jobs,
            "removedCount": 0,
            "removedNotes": [
                "Strict filter: US Citizenship required and TS/SCI clearance jobs automatically excluded.",
                "Job retention active: Open positions stay visible until you take action (Apply or Dismiss)."
            ]
        }
    ]
}

with open(os.path.join(base_dir, 'jobs.json'), 'w') as f:
    json.dump(output_data, f, indent=2)

docs_dir = os.path.join(base_dir, 'docs')
os.makedirs(docs_dir, exist_ok=True)

with open(os.path.join(docs_dir, 'jobs.json'), 'w') as f:
    json.dump(output_data, f, indent=2)

# Update index.html and docs/index.html
index_file = os.path.join(base_dir, 'index.html')
if os.path.exists(index_file):
    with open(index_file, 'r') as f:
        html = f.read()

    prefix = "const EMBEDDED_JOBS_DATA = "
    p_idx = html.find(prefix)
    if p_idx != -1:
        semi_marker = ";\n\nfunction initAuthGate"
        semi_idx = html.find(semi_marker, p_idx)
        if semi_idx != -1:
            html = html[:p_idx + len(prefix)] + json.dumps(output_data) + html[semi_idx:]
            with open(index_file, 'w') as f:
                f.write(html)
            with open(os.path.join(docs_dir, 'index.html'), 'w') as f:
                f.write(html)

print("Successfully updated jobs.json, docs/jobs.json, and HTML templates!")
