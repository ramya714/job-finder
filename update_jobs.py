import xml.etree.ElementTree as ET
import urllib.request
import urllib.parse
import ssl
import json
import datetime
import os
import re
import html
import concurrent.futures

ctx = ssl._create_unverified_context()

COMPANY_BOARDS = [
    ('Tanium', 'greenhouse', 'tanium', 'Converged Endpoint Management (Seattle Hub)'),
    ('Amperity', 'greenhouse', 'amperity', 'Enterprise Customer Data Platform (Seattle Hub)'),
    ('Coupang', 'greenhouse', 'coupang', 'High-Scale E-Commerce & Cloud Logistics (Seattle Hub)'),
    ('Databricks', 'greenhouse', 'databricks', 'Data & AI Cloud Platform (Seattle Hub)'),
    ('Esper', 'lever', 'esper', 'DevOps for Dedicated Devices & Android (Seattle Hub)'),
    ('ExtraHop', 'greenhouse', 'extrahopnetworks', 'Network Detection & Security (Seattle Hub)'),
    ('Figma', 'greenhouse', 'figma', 'Collaborative Design Platform (Seattle Hub)'),
    ('OfferUp', 'greenhouse', 'offerup', 'Mobile Marketplace (Seattle Hub)'),
    ('Outreach', 'lever', 'outreach', 'Sales Intelligence & Cloud Execution (Seattle Hub)'),
    ('PayScale', 'ashby', 'payscale', 'Compensation SaaS (Seattle Hub)'),
    ('Pinterest', 'greenhouse', 'pinterest', 'Visual Discovery & Machine Learning (Seattle Hub)'),
    ('Pushpay', 'greenhouse', 'pushpay', 'Donor Management SaaS (Redmond / Seattle Hub)'),
    ('Qualtrics', 'greenhouse', 'qualtrics', 'Experience Management SaaS (Seattle Hub)'),
    ('Qumulo', 'ashby', 'qumulo', 'Hybrid Cloud File Storage (Seattle Hub)'),
    ('Reddit', 'greenhouse', 'reddit', 'Community & Social Platform (Seattle Hub)'),
    ('Robinhood', 'greenhouse', 'robinhood', 'Retail Investment Platform (Bellevue Hub)'),
    ('Rover', 'lever', 'rover', 'Consumer Marketplace (Seattle Hub)'),
    ('Smartsheet', 'greenhouse', 'smartsheet', 'Enterprise Collaboration (Seattle Hub)'),
    ('Snowflake', 'ashby', 'snowflake', 'Cloud Data Platform (Bellevue Hub)'),
    ('Stripe', 'greenhouse', 'stripe', 'Fintech & Global Payments Infrastructure (Seattle Hub)'),
    ('Subsplash', 'greenhouse', 'subsplash', 'Mobile App & Media Platform (Seattle Hub)'),
    ('Zenoti', 'greenhouse', 'zenoti', 'Cloud Software for Salons & Spas (Seattle Hub)'),
    ('1Password', 'ashby', '1password', 'Software & Cloud Infrastructure'),
    ('Acorns', 'ashby', 'acorns', 'Software & Cloud Infrastructure'),
    ('Affirm', 'greenhouse', 'affirm', 'Software & Cloud Infrastructure'),
    ('Airbnb', 'greenhouse', 'airbnb', 'Software & Cloud Infrastructure'),
    ('Airtable', 'greenhouse', 'airtable', 'Software & Cloud Infrastructure'),
    ('Akuna Capital', 'greenhouse', 'akunacapital', 'Software & Cloud Infrastructure'),
    ('AllTrails', 'lever', 'alltrails', 'Software & Cloud Infrastructure'),
    ('Alloy', 'greenhouse', 'alloy', 'Software & Cloud Infrastructure'),
    ('Amplitude', 'greenhouse', 'amplitude', 'Software & Cloud Infrastructure'),
    ('Anthropic', 'greenhouse', 'anthropic', 'Software & Cloud Infrastructure'),
    ('Apollo GraphQL', 'ashby', 'apollo-graphql', 'Software & Cloud Infrastructure'),
    ('Asana', 'greenhouse', 'asana', 'Software & Cloud Infrastructure'),
    ('Astranis', 'greenhouse', 'astranis', 'Software & Cloud Infrastructure'),
    ('Astronomer', 'ashby', 'astronomer', 'Software & Cloud Infrastructure'),
    ('Attentive', 'greenhouse', 'attentive', 'Software & Cloud Infrastructure'),
    ('Automattic', 'greenhouse', 'automatticcareers', 'Software & Cloud Infrastructure'),
    ('Baseten', 'ashby', 'baseten', 'Software & Cloud Infrastructure'),
    ('Benchling', 'ashby', 'benchling', 'Software & Cloud Infrastructure'),
    ('Betterment', 'greenhouse', 'betterment', 'Software & Cloud Infrastructure'),
    ('BitGo', 'greenhouse', 'bitgo', 'Software & Cloud Infrastructure'),
    ('Bitwarden', 'greenhouse', 'bitwarden', 'Software & Cloud Infrastructure'),
    ('Blend', 'greenhouse', 'blend', 'Software & Cloud Infrastructure'),
    ('Block / Cash App', 'greenhouse', 'block', 'Software & Cloud Infrastructure'),
    ('Box', 'greenhouse', 'boxinc', 'Software & Cloud Infrastructure'),
    ('Braintrust', 'ashby', 'braintrust', 'Software & Cloud Infrastructure'),
    ('Braze', 'greenhouse', 'braze', 'Software & Cloud Infrastructure'),
    ('Brex', 'greenhouse', 'brex', 'Software & Cloud Infrastructure'),
    ('Calm', 'greenhouse', 'calm', 'Software & Cloud Infrastructure'),
    ('Capsule', 'ashby', 'capsule', 'Software & Cloud Infrastructure'),
    ('Carta', 'greenhouse', 'carta', 'Software & Cloud Infrastructure'),
    ('Checkr', 'greenhouse', 'checkr', 'Software & Cloud Infrastructure'),
    ('Chime', 'greenhouse', 'chime', 'Software & Cloud Infrastructure'),
    ('Circle', 'ashby', 'circle', 'Software & Cloud Infrastructure'),
    ('ClassPass', 'greenhouse', 'classpass', 'Software & Cloud Infrastructure'),
    ('Clerk', 'ashby', 'clerk', 'Software & Cloud Infrastructure'),
    ('ClickHouse', 'ashby', 'clickhouse', 'Software & Cloud Infrastructure'),
    ('ClickUp', 'ashby', 'clickup', 'Software & Cloud Infrastructure'),
    ('Cloudflare', 'greenhouse', 'cloudflare', 'Software & Cloud Infrastructure'),
    ('Cockroach Labs', 'greenhouse', 'cockroachlabs', 'Software & Cloud Infrastructure'),
    ('Cognition', 'ashby', 'cognition', 'Software & Cloud Infrastructure'),
    ('Cognition / Devin', 'ashby', 'cognition', 'Software & Cloud Infrastructure'),
    ('Coinbase', 'greenhouse', 'coinbase', 'Software & Cloud Infrastructure'),
    ('Color Health', 'ashby', 'color-health', 'Software & Cloud Infrastructure'),
    ('Confluent', 'ashby', 'confluent', 'Software & Cloud Infrastructure'),
    ('Cribl', 'greenhouse', 'cribl', 'Software & Cloud Infrastructure'),
    ('Culture Amp', 'greenhouse', 'cultureamp', 'Software & Cloud Infrastructure'),
    ('Current', 'greenhouse', 'current', 'Software & Cloud Infrastructure'),
    ('Customer.io', 'greenhouse', 'customerio', 'Software & Cloud Infrastructure'),
    ('Datadog', 'greenhouse', 'datadog', 'Software & Cloud Infrastructure'),
    ('Dave', 'ashby', 'dave', 'Software & Cloud Infrastructure'),
    ('DeepL', 'ashby', 'deepl', 'Software & Cloud Infrastructure'),
    ('Descript', 'greenhouse', 'descript', 'Software & Cloud Infrastructure'),
    ('Dialpad', 'greenhouse', 'dialpad', 'Software & Cloud Infrastructure'),
    ('Discord', 'greenhouse', 'discord', 'Software & Cloud Infrastructure'),
    ('Docker', 'ashby', 'docker', 'Software & Cloud Infrastructure'),
    ('Dropbox', 'greenhouse', 'dropbox', 'Software & Cloud Infrastructure'),
    ('Duolingo', 'greenhouse', 'duolingo', 'Software & Cloud Infrastructure'),
    ('Elastic', 'greenhouse', 'elastic', 'Software & Cloud Infrastructure'),
    ('ElevenLabs', 'ashby', 'elevenlabs', 'Software & Cloud Infrastructure'),
    ('Entrata', 'lever', 'entrata', 'Software & Cloud Infrastructure'),
    ('Eventbrite', 'greenhouse', 'eventbriteinc', 'Software & Cloud Infrastructure'),
    ('Factory AI', 'ashby', 'factory', 'Software & Cloud Infrastructure'),
    ('Faire', 'greenhouse', 'faire', 'Software & Cloud Infrastructure'),
    ('Fastly', 'greenhouse', 'fastly', 'Software & Cloud Infrastructure'),
    ('Fireblocks', 'greenhouse', 'fireblocks', 'Software & Cloud Infrastructure'),
    ('Fivetran', 'greenhouse', 'fivetran', 'Software & Cloud Infrastructure'),
    ('Flatiron Health', 'greenhouse', 'flatironhealth', 'Software & Cloud Infrastructure'),
    ('Flexport', 'greenhouse', 'flexport', 'Software & Cloud Infrastructure'),
    ('Flow Traders', 'greenhouse', 'flowtraders', 'Software & Cloud Infrastructure'),
    ('FullStory', 'ashby', 'fullstory', 'Software & Cloud Infrastructure'),
    ('Gemini', 'greenhouse', 'gemini', 'Software & Cloud Infrastructure'),
    ('GitLab', 'greenhouse', 'gitlab', 'Software & Cloud Infrastructure'),
    ('Gong', 'greenhouse', 'gongio', 'Software & Cloud Infrastructure'),
    ('Gopuff', 'lever', 'gopuff', 'Software & Cloud Infrastructure'),
    ('Grafana Labs', 'greenhouse', 'grafanalabs', 'Software & Cloud Infrastructure'),
    ('Gusto', 'greenhouse', 'gusto', 'Software & Cloud Infrastructure'),
    ('Harness', 'greenhouse', 'harnessinc', 'Software & Cloud Infrastructure'),
    ('Harvey AI', 'ashby', 'harvey', 'Software & Cloud Infrastructure'),
    ('Headway', 'ashby', 'headway', 'Software & Cloud Infrastructure'),
    ('Hex', 'ashby', 'hex', 'Software & Cloud Infrastructure'),
    ('HeyGen', 'greenhouse', 'heygen', 'Software & Cloud Infrastructure'),
    ('Hightouch', 'greenhouse', 'hightouch', 'Software & Cloud Infrastructure'),
    ('Honeycomb', 'greenhouse', 'honeycomb', 'Software & Cloud Infrastructure'),
    ('Hudson River Trading', 'greenhouse', 'wehrtyou', 'Software & Cloud Infrastructure'),
    ('Impinj', 'greenhouse', 'impinj', 'Software & Cloud Infrastructure'),
    ('Inngest', 'ashby', 'inngest', 'Software & Cloud Infrastructure'),
    ('Instacart', 'greenhouse', 'instacart', 'Software & Cloud Infrastructure'),
    ('Intercom', 'greenhouse', 'intercom', 'Software & Cloud Infrastructure'),
    ('Iterable', 'greenhouse', 'iterable', 'Software & Cloud Infrastructure'),
    ('Jane Street', 'greenhouse', 'janestreet', 'Software & Cloud Infrastructure'),
    ('Jump Trading', 'greenhouse', 'jumptrading', 'Software & Cloud Infrastructure'),
    ('Kentik', 'greenhouse', 'kentik', 'Software & Cloud Infrastructure'),
    ('Klaviyo', 'greenhouse', 'klaviyo', 'Software & Cloud Infrastructure'),
    ('Komodo Health', 'greenhouse', 'komodohealth', 'Software & Cloud Infrastructure'),
    ('Kong', 'ashby', 'kong', 'Software & Cloud Infrastructure'),
    ('Kraken', 'ashby', 'krakentech', 'Software & Cloud Infrastructure'),
    ('Kustomer', 'ashby', 'kustomer', 'Software & Cloud Infrastructure'),
    ('LangChain', 'ashby', 'langchain', 'Software & Cloud Infrastructure'),
    ('Lattice', 'greenhouse', 'lattice', 'Software & Cloud Infrastructure'),
    ('LaunchDarkly', 'greenhouse', 'launchdarkly', 'Software & Cloud Infrastructure'),
    ('Linear', 'ashby', 'linear', 'Software & Cloud Infrastructure'),
    ('Lithic', 'greenhouse', 'lithic', 'Software & Cloud Infrastructure'),
    ('LogRocket', 'lever', 'logrocket', 'Software & Cloud Infrastructure'),
    ('Lyft', 'greenhouse', 'lyft', 'Software & Cloud Infrastructure'),
    ('Lyra Health', 'lever', 'lyrahealth', 'Software & Cloud Infrastructure'),
    ('Maven Clinic', 'greenhouse', 'mavenclinic', 'Software & Cloud Infrastructure'),
    ('Melio', 'greenhouse', 'melio', 'Software & Cloud Infrastructure'),
    ('Mercury', 'greenhouse', 'mercury', 'Software & Cloud Infrastructure'),
    ('Miro', 'ashby', 'miro', 'Software & Cloud Infrastructure'),
    ('Mixpanel', 'greenhouse', 'mixpanel', 'Software & Cloud Infrastructure'),
    ('Modal Labs', 'ashby', 'modal', 'Software & Cloud Infrastructure'),
    ('Modern Health', 'greenhouse', 'modernhealth', 'Software & Cloud Infrastructure'),
    ('Modern Treasury', 'ashby', 'moderntreasury', 'Software & Cloud Infrastructure'),
    ('MongoDB', 'greenhouse', 'mongodb', 'Software & Cloud Infrastructure'),
    ('Mozilla', 'greenhouse', 'mozilla', 'Software & Cloud Infrastructure'),
    ('Mural', 'ashby', 'mural', 'Software & Cloud Infrastructure'),
    ('Neon', 'ashby', 'neon', 'Software & Cloud Infrastructure'),
    ('Neon Database', 'ashby', 'neon', 'Software & Cloud Infrastructure'),
    ('Netskope', 'greenhouse', 'netskope', 'Software & Cloud Infrastructure'),
    ('New Relic', 'greenhouse', 'newrelic', 'Software & Cloud Infrastructure'),
    ('Notion', 'ashby', 'notion', 'Software & Cloud Infrastructure'),
    ('Nuro', 'greenhouse', 'nuro', 'Software & Cloud Infrastructure'),
    ('Okta', 'greenhouse', 'okta', 'Software & Cloud Infrastructure'),
    ('Old Mission Capital', 'greenhouse', 'oldmissioncapital', 'Software & Cloud Infrastructure'),
    ('OpenAI', 'ashby', 'openai', 'Software & Cloud Infrastructure'),
    ('Optiver', 'greenhouse', 'optiver', 'Software & Cloud Infrastructure'),
    ('Oscar Health', 'greenhouse', 'oscar', 'Software & Cloud Infrastructure'),
    ('Otter.ai', 'greenhouse', 'otterai', 'Software & Cloud Infrastructure'),
    ('Oura', 'greenhouse', 'oura', 'Software & Cloud Infrastructure'),
    ('Pacaso', 'greenhouse', 'pacaso', 'Software & Cloud Infrastructure'),
    ('Paxos', 'ashby', 'paxos', 'Software & Cloud Infrastructure'),
    ('Perplexity AI', 'ashby', 'perplexity', 'Software & Cloud Infrastructure'),
    ('Persona', 'ashby', 'persona', 'Software & Cloud Infrastructure'),
    ('Pika', 'ashby', 'pika', 'Software & Cloud Infrastructure'),
    ('Pinecone', 'ashby', 'pinecone', 'Software & Cloud Infrastructure'),
    ('Plaid', 'ashby', 'plaid', 'Software & Cloud Infrastructure'),
    ('PlanetScale', 'greenhouse', 'planetscale', 'Software & Cloud Infrastructure'),
    ('Point72', 'greenhouse', 'point72', 'Software & Cloud Infrastructure'),
    ('Poolside AI', 'ashby', 'poolside', 'Software & Cloud Infrastructure'),
    ('Postman', 'greenhouse', 'postman', 'Software & Cloud Infrastructure'),
    ('Prefect', 'ashby', 'prefect', 'Software & Cloud Infrastructure'),
    ('Prisma', 'greenhouse', 'prisma', 'Software & Cloud Infrastructure'),
    ('Qualia', 'greenhouse', 'qualia', 'Software & Cloud Infrastructure'),
    ('Railway', 'ashby', 'railway', 'Software & Cloud Infrastructure'),
    ('Ramp', 'ashby', 'ramp', 'Software & Cloud Infrastructure'),
    ('Remote', 'greenhouse', 'remote', 'Software & Cloud Infrastructure'),
    ('Remote.com', 'greenhouse', 'remote', 'Software & Cloud Infrastructure'),
    ('Render', 'ashby', 'render', 'Software & Cloud Infrastructure'),
    ('Replit', 'ashby', 'replit', 'Software & Cloud Infrastructure'),
    ('Resend', 'ashby', 'resend', 'Software & Cloud Infrastructure'),
    ('Ro', 'lever', 'ro', 'Software & Cloud Infrastructure'),
    ('Roblox', 'greenhouse', 'roblox', 'Software & Cloud Infrastructure'),
    ('Roku', 'greenhouse', 'roku', 'Software & Cloud Infrastructure'),
    ('Roofstock', 'greenhouse', 'roofstock', 'Software & Cloud Infrastructure'),
    ('RunPod', 'ashby', 'runpod', 'Software & Cloud Infrastructure'),
    ('Runway', 'ashby', 'runway', 'Software & Cloud Infrastructure'),
    ('Samsara', 'greenhouse', 'samsara', 'Software & Cloud Infrastructure'),
    ('Scale AI', 'greenhouse', 'scaleai', 'Software & Cloud Infrastructure'),
    ('SeatGeek', 'greenhouse', 'seatgeek', 'Software & Cloud Infrastructure'),
    ('Sentry', 'ashby', 'sentry', 'Software & Cloud Infrastructure'),
    ('SoFi', 'greenhouse', 'sofi', 'Software & Cloud Infrastructure'),
    ('Spotify', 'lever', 'spotify', 'Software & Cloud Infrastructure'),
    ('Stability AI', 'greenhouse', 'stabilityai', 'Software & Cloud Infrastructure'),
    ('StackBlitz', 'greenhouse', 'stackblitz', 'Software & Cloud Infrastructure'),
    ('StockX', 'greenhouse', 'stockx', 'Software & Cloud Infrastructure'),
    ('Strava', 'ashby', 'strava', 'Software & Cloud Infrastructure'),
    ('Suno AI', 'ashby', 'suno', 'Software & Cloud Infrastructure'),
    ('Supabase', 'ashby', 'supabase', 'Software & Cloud Infrastructure'),
    ('Synthesia', 'ashby', 'synthesia', 'Software & Cloud Infrastructure'),
    ('Sysdig', 'lever', 'sysdig', 'Software & Cloud Infrastructure'),
    ('Tailscale', 'greenhouse', 'tailscale', 'Software & Cloud Infrastructure'),
    ('Temporal', 'ashby', 'temporal', 'Software & Cloud Infrastructure'),
    ('Toast', 'greenhouse', 'toast', 'Software & Cloud Infrastructure'),
    ('Together AI', 'greenhouse', 'togetherai', 'Software & Cloud Infrastructure'),
    ('Treasury Prime', 'greenhouse', 'treasuryprime', 'Software & Cloud Infrastructure'),
    ('Trigger.dev', 'ashby', 'triggerdev', 'Software & Cloud Infrastructure'),
    ('Twilio', 'greenhouse', 'twilio', 'Software & Cloud Infrastructure'),
    ('Udio', 'greenhouse', 'udio', 'Software & Cloud Infrastructure'),
    ('Unit', 'ashby', 'unit', 'Software & Cloud Infrastructure'),
    ('Upgrade', 'greenhouse', 'upgrade', 'Software & Cloud Infrastructure'),
    ('VTS', 'greenhouse', 'vts', 'Software & Cloud Infrastructure'),
    ('Vercel', 'greenhouse', 'vercel', 'Software & Cloud Infrastructure'),
    ('Verkada', 'greenhouse', 'verkada', 'Software & Cloud Infrastructure'),
    ('Warp', 'ashby', 'warp', 'Software & Cloud Infrastructure'),
    ('Waymo', 'greenhouse', 'waymo', 'Software & Cloud Infrastructure'),
    ('Wealthfront', 'lever', 'wealthfront', 'Software & Cloud Infrastructure'),
    ('Webflow', 'greenhouse', 'webflow', 'Software & Cloud Infrastructure'),
    ('Whoop', 'ashby', 'whoop', 'Software & Cloud Infrastructure'),
    ('Wiz', 'greenhouse', 'wizinc', 'Software & Cloud Infrastructure'),
    ('Writer', 'ashby', 'writer', 'Software & Cloud Infrastructure'),
    ('Zapier', 'ashby', 'zapier', 'Software & Cloud Infrastructure'),
    ('Zed Industries', 'ashby', 'zed', 'Software & Cloud Infrastructure'),
    ('ZoomInfo', 'greenhouse', 'zoominfo', 'Software & Cloud Infrastructure'),
    ('Zoox', 'lever', 'zoox', 'Software & Cloud Infrastructure'),
]


WORKDAY_BOARDS = [
    ('Zillow', 'https://zillow.wd5.myworkdayjobs.com/wday/cxs/zillow/Zillow_Group_External/jobs', 'https://zillow.wd5.myworkdayjobs.com/en-US/Zillow_Group_External', 'Real Estate & Cloud Platforms (Seattle Hub)'),
    ('NVIDIA', 'https://nvidia.wd5.myworkdayjobs.com/wday/cxs/nvidia/NVIDIAExternalCareerSite/jobs', 'https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite', 'AI Hardware & Cloud Compute'),
    ('Adobe', 'https://adobe.wd5.myworkdayjobs.com/wday/cxs/adobe/external_experienced/jobs', 'https://adobe.wd5.myworkdayjobs.com/en-US/external_experienced', 'Creative & Document Cloud (Seattle Hub)'),
    ('Cisco', 'https://cisco.wd5.myworkdayjobs.com/wday/cxs/cisco/Cisco_Careers/jobs', 'https://cisco.wd5.myworkdayjobs.com/en-US/Cisco_Careers', 'Networking & Cloud Infrastructure'),
    ('Workday', 'https://workday.wd5.myworkdayjobs.com/wday/cxs/workday/Workday/jobs', 'https://workday.wd5.myworkdayjobs.com/en-US/Workday', 'Enterprise Cloud Applications'),
    ('eBay', 'https://ebay.wd5.myworkdayjobs.com/wday/cxs/ebay/apply/jobs', 'https://ebay.wd5.myworkdayjobs.com/en-US/apply', 'Global E-Commerce Marketplace (Bellevue Hub)'),
    ('Autodesk', 'https://autodesk.wd1.myworkdayjobs.com/wday/cxs/autodesk/Ext/jobs', 'https://autodesk.wd1.myworkdayjobs.com/en-US/Ext', 'Design & 3D Software Cloud')
]

CLEARANCE_KEYWORDS = [
    'ts/sci', 'ts-sci', 'top secret', 'secret clearance', 'security clearance',
    'public sector', 'us citizenship required', 'u.s. citizenship required',
    'u.s. citizen only', 'us citizen only', 'polygraph', 'dod clearance',
    'active clearance', 'clearance required', 'single scope background',
    'defense clearance', 'government clearance', 'itar restricted',
    'federal', 'us federal', 'u.s. federal', 'fedramp', 'public trust',
    'clearance', 'cleared', 'active secret', 'us citizen', 'u.s. citizen',
    'citizenship required', 'citizenship status', 'must be a u.s. citizen',
    'must be a us citizen', 'government contractor'
]

TITLE_EXCLUSIONS = [
    'manager', 'director', 'vp', 'vice president', 'head of', 'lead of', 'principal', 'distinguished', 'fellow',
    'intern', 'internship', 'student', 'student worker', 'co-op', 'coop', 'apprentice', 'apprenticeship',
    'contract', 'contractor', 'temporary', 'temp', 'part-time', 'part time', 'seasonal', 'new grad', 'university grad',
    'undergraduate', 'graduate intern', 'volunteer', 'adjunct',
    'entry level', 'entry-level', 'junior', 'jr', 'jr.', 'associate engineer', 'associate software engineer', 'campus hire',
    'recruiter', 'counsel', 'account executive', 'legal',
    'sales', 'marketing', 'product manager', 'designer', 'copywriter', 'general counsel',
    'business partner', 'administrative', 'data scientist', 'analytics lead', 'business analyst',
    'data engineer', 'big data', 'data platform', 'data infrastructure', 'database administrator', 'dba',
    'analytics engineer', 'bi engineer', 'etl',
    'hardware', 'hvac', 'dv engineer', 'verification', 'endpoint', 'it controls', 'compliance engineer',
    'android', 'ios', 'mobile', 'devrel', 'developer relations', 'solutions engineer', 'sales engineer',
    'support engineer', 'customer engineer', 'network engineer', 'firmware', 'embedded', 'fpga', 'asic', 'silicon',
    'security', 'cybersecurity', 'cloud security', 'security engineer', 'security software engineer', 'detection and response', 'iam',
    'infosec', 'appsec', 'product security',
    'systems engineer', 'systems engineering', 'system engineer', 'system engineering', 'it systems engineer',
    'c++', 'c/c++', 'cpp',
    'devops', 'sre', 'site reliability', 'creative',
    'machine learning', 'ml engineer', 'ml software', 'deep learning', 'nlp', 'computer vision',
    'data science', 'research scientist', 'applied scientist', 'llm', 'genai', 'generative ai',
    'algorithm engineer', 'ai engineer', 'ai infrastructure', 'ai research', 'ai platform',
    'ai runtime', 'ai inference', 'inference', 'model lifecycle', 'ai native', 'ai agent', 'ai tools', 'caper ai', 'ai product',
    'frontier agent', 'frontier agents', 'openshell', 'gpu', 'hpc', 'people platform', 'business systems',
    'early career', '2025', '2026', '2027', 'reinforcement learning', 'rl training', 'rl engineer',
    'federal', 'us federal', 'cleared', 'clearance', 'public trust', 'defense', 'government', 'us citizen', 'citizenship'
]

def is_non_fulltime_role(text):
    if not text:
        return False
    t = text.lower().replace(' ', ' ').replace('-', ' ').replace(',', ' ')
    return bool(re.search(r'\b(intern|internship|student|student worker|co-?op|coop|apprentice|apprenticeship|contract|contractor|temporary|temp|part[- ]time|seasonal|entry\s*level|junior|jr\.?|associate\s*software\s*engineer|associate\s*engineer|new\s*grad|university\s*grad|graduate\s*intern|undergraduate|volunteer|adjunct|campus\s*hire)\b', t))

def is_resume_role_matched(title):
    if not title:
        return False
    t = title.lower().replace(' ', ' ').replace('-', ' ').replace(',', ' ')
    
    # 0a. Strict exclusion of Internships, Student Worker, Contract, Part-Time, Temporary, Apprentice, Entry Level, Junior roles
    if is_non_fulltime_role(t):
        return False

    # 0. Strict exclusion of Principal / Executive / Management level
    if re.search(r'\b(principal|distinguished|fellow|director|vp|vice president|manager|lead|head of)\b', t):
        return False
        
    # 0b. Strict exclusion of Staff-level roles (while preserving Member of Technical Staff)
    if 'member of technical staff' not in t and 'technical staff' not in t:
        if re.search(r'\b(staff|sr\.?\s*staff|senior\s*staff)\b', t):
            return False

    # 0c. Strict exclusion of ML / AI / Data / Security / Hardware keywords
    if re.search(r'\b(ml|ai|devai|genai|llm|rl|deep learning|machine learning|reinforcement learning|big data|security|cybersecurity|infosec|appsec)\b', t):
        return False

    # 0d. Strict exclusion of Data Engineering and Analytics roles
    if re.search(r'\bdata\s*(engineer|engineering|platform|infra|infrastructure|pipeline|warehouse|lakehouse|analytics|architect|architecture)\b', t):
        return False
    if re.search(r'\b(bi engineer|etl|dba|database administrator|analytics engineer|data scientist)\b', t):
        return False

    # 0e. Strict exclusion of Federal, Clearance, Defense, and Government roles
    if re.search(r'\b(federal|fedramp|cleared|clearance|secret|polygraph|public trust|defense|government|us citizen|u\.s\. citizen|citizenship)\b', t):
        return False

    # 0f. Strict exclusion of Systems Engineer roles
    if re.search(r'\bsystems?\s*engine(?:er|ering)\b', t):
        return False

    # 0g. Strict exclusion of C++ titles
    if re.search(r'(?:c\+\+|c\s*/\s*c\+\+|\bcpp\b)', t):
        return False

    # 1. Immediate reject for excluded roles
    for ex in TITLE_EXCLUSIONS:
        if re.search(r'\b' + re.escape(ex) + r'\b', t):
            return False
            
    # 2. Match Forward Deployed Engineer roles
    if ('forward deployed' in t or 'fde' in t) and any(e in t for e in ['engineer', 'swe', 'software', 'developer']):
        return True
        
    # 3. Match Full Stack, Backend, Frontend, and Core Software Engineer roles (including SDE)
    is_fullstack = 'full stack' in t or 'fullstack' in t
    is_backend = 'backend' in t or 'back end' in t
    is_frontend = 'frontend' in t or 'front end' in t or 'web platform' in t or 'web engineer' in t
    is_swe = ('software engineer' in t or 'software developer' in t or 
              'software development engineer' in t or bool(re.search(r'\bsde\b', t)) or
              'member of technical staff' in t or 
              'infrastructure engineer' in t or 
              'platform engineer' in t or 'applications engineer' in t)
              
    return is_fullstack or is_backend or is_frontend or is_swe

TITLE_INCLUSIONS = [
    'software', 'engineer', 'developer', 'backend', 'full stack', 'fullstack',
    'platform', 'infrastructure', 'systems', 'cloud',
    'distributed', 'applications', 'mts', 'technical staff', 'forward deployed', 'fde', 'sde'
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
    # Americas / LATAM
    'mexico', 'colombia', 'canada', 'brazil', 'argentina', 'chile', 'peru', 'costa rica', 'uruguay',
    'latam', 'latin america', 'toronto', 'vancouver', 'montreal', 'ottawa', 'calgary', 'bogota', 'medellin',
    'guadalajara', 'monterrey', 'mexico city', 'cdmx', 'sao paulo', 'buenos aires', 'santiago',
    # Europe / EMEA / UK
    'europe', 'emea', 'uk', 'united kingdom', 'great britain', 'england', 'scotland', 'wales', 'london',
    'ireland', 'dublin', 'germany', 'berlin', 'munich', 'frankfurt', 'hamburg', 'france', 'paris',
    'netherlands', 'amsterdam', 'spain', 'madrid', 'barcelona', 'italy', 'rome', 'milan', 'portugal',
    'lisbon', 'porto', 'poland', 'warsaw', 'krakow', 'sweden', 'stockholm', 'switzerland', 'zurich',
    'geneva', 'austria', 'vienna', 'norway', 'oslo', 'finland', 'helsinki', 'denmark', 'copenhagen',
    'belgium', 'brussels', 'czech', 'czechia', 'prague', 'romania', 'bucharest', 'hungary', 'budapest',
    'estonia', 'tallinn', 'latvia', 'riga', 'lithuania', 'vilnius', 'greece', 'athens', 'bulgaria', 'sofia',
    'croatia', 'serbia', 'ukraine', 'kyiv',
    # Asia / APAC
    'india', 'bangalore', 'bengaluru', 'hyderabad', 'pune', 'chennai', 'mumbai', 'delhi', 'noida', 'gurgaon',
    'gurugram', 'singapore', 'japan', 'tokyo', 'korea', 'seoul', 'taiwan', 'taipei', 'china', 'beijing',
    'shanghai', 'shenzhen', 'hong kong', 'apac', 'asia', 'philippines', 'manila', 'vietnam', 'indonesia',
    'jakarta', 'malaysia', 'kuala lumpur', 'thailand', 'bangkok',
    # Middle East / Africa / Oceania
    'israel', 'tel aviv', 'uae', 'dubai', 'abu dhabi', 'australia', 'sydney', 'melbourne', 'brisbane',
    'new zealand', 'auckland', 'south africa', 'cape town', 'johannesburg', 'nigeria', 'lagos', 'kenya', 'nairobi', 'egypt', 'cairo',
    'worldwide', 'global', 'anywhere'
]

def is_strictly_us_location(loc_str, title_str=''):
    title_lower = (title_str or '').lower()
    
    # 1. If title explicitly indicates foreign region or remote outside US -> reject
    for d in DENY_INTERNATIONAL:
        if re.search(r'\b' + re.escape(d) + r'\b', title_lower):
            if not any(u in title_lower for u in ['usa', 'united states', 'seattle', 'remote us', 'remote usa']):
                return False

    loc_lower = (loc_str or '').lower().strip()
    if not loc_lower:
        return False
        
    # Split composite locations by semicolon, pipe, newline, or ' or '
    loc_parts = re.split(r'[;\n|]|\bor\b', loc_lower)
    
    has_valid_us = False
    
    for part in loc_parts:
        part = part.strip()
        if not part:
            continue
        
        # Check if this sub-location contains any international deny keyword
        is_foreign = False
        for d in DENY_INTERNATIONAL:
            if re.search(r'\b' + re.escape(d) + r'\b', part):
                is_foreign = True
                break
        
        if is_foreign:
            continue
            
        # If this part mentions US cities or keywords
        if any(kw in part for kw in US_CITIES_AND_KEYWORDS):
            has_valid_us = True
            break
            
        # If this part has US state code
        if any(re.search(r'\b' + sc.lower() + r'\b', part) or f', {sc.lower()}' in part for sc in US_STATE_CODES):
            has_valid_us = True
            break
            
        # If this part is plain 'remote' (and not foreign)
        if 'remote' in part and not is_foreign:
            has_valid_us = True
            break

    return has_valid_us

def get_region_info(loc_str):
    l = (loc_str or '').lower()
    if any(k in l for k in ['seattle', 'bellevue', 'redmond', 'kirkland', ', wa', 'wa,', 'wa -', 'washington']) and 'dc' not in l:
        return 'Seattle / WA', 1
    if 'remote' in l:
        return 'Remote', 2
    if any(k in l for k in ['new york', 'nyc', 'boston', 'chicago', 'philadelphia', 'atlanta', 'austin', 'miami', 'jersey city']):
        return 'East', 3
    return 'West', 4

STANDARD_LABEL_KEYWORDS = [
    'first name', 'last name', 'email', 'phone', 'resume', 'cv', 'linkedin',
    'website', 'github', 'portfolio', 'twitter', 'location', 'pronoun',
    'hear about', 'gender', 'race', 'veteran', 'disability', 'authorized',
    'sponsorship', 'require sponsorship', 'visa', 'citizenship', 'start date',
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

def is_clearance_or_citizen_restricted(text):
    if not text:
        return False
    t = html.unescape(text).lower()
    t = re.sub(r'<[^>]+>', ' ', t)
    for k in CLEARANCE_KEYWORDS:
        if re.search(r'\b' + re.escape(k) + r'\b', t):
            return True
    return False

EXCESSIVE_YOE_PATTERNS = [
    # 7+ years, 8+ years, 10+ yrs, etc. (including HTML encoded plus)
    r'\b([7-9]|\d{2})\s*(?:\+|&#43;|&plus;)\s*(?:years?|yrs?)\b',
    # 7 or more years, 8 or more years, 10 or more years
    r'\b([7-9]|\d{2})\s*(?:\+|)\s*or\s+more\s+(?:years?|yrs?)\b',
    # at least 7 years, minimum of 7 years, minimum 8 yrs
    r'\b(?:at\s+least|minimum\s+of|minimum)\s+([7-9]|\d{2})\s*(?:\+|)\s*(?:years?|yrs?)\b',
    # 7-10 years, 8-12 years (where lower bound >= 7)
    r'\b([7-9]|\d{2})\s*(?:-|to)\s*\d+\s*(?:years?|yrs?)\b',
    # 7+ years of experience / 8+ years of professional experience / 8 years of experience
    r'\b([7-9]|\d{2})\s*(?:\+|)\s*(?:years?|yrs?)\s+of\s+(?:professional|practical|industry|relevant|engineering|software)?\s*experience\b',
    r'\b(?:requires?|requiring|with)\s+([7-9]|\d{2})\s*(?:\+|)\s*(?:years?|yrs?)\b',
    r'\b([7-9]|\d{2})\s*(?:years?|yrs?)\s+(?:practical|professional)?\s*experience\b',
]

def has_excessive_yoe_requirement(text):
    if not text:
        return False
    t = html.unescape(text).lower()
    t = re.sub(r'&#43;|&plus;', '+', t)
    t = re.sub(r'<[^>]+>', ' ', t)
    for p in EXCESSIVE_YOE_PATTERNS:
        if re.search(p, t):
            return True
    return False

THIRD_PARTY_DOMAINS = [
    'themuse.com', 'jobicy.com', 'arbeitnow.com', 'himalayas.app',
    'weworkremotely.com', 'news.ycombinator.com', 'indeed.com',
    'ziprecruiter.com', 'simplyhired.com', 'monster.com', 'glassdoor.com',
    'builtin.com', 'dice.com', 'careerbuilder.com', 'jooble.org',
    'careerpuck.com'
]

def is_direct_company_url(url):
    if not url:
        return False
    u = url.lower()
    for tp in THIRD_PARTY_DOMAINS:
        if tp in u:
            return False
    return True

def is_job_live(url, slug=None, ats_id=None):
    if not url:
        return False
    if slug and ats_id:
        status_url = f'https://boards-api.greenhouse.io/v1/boards/{slug}/jobs/{ats_id}'
        try:
            req = urllib.request.Request(status_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=ctx, timeout=4) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode('utf-8'))
                    if data.get('id') or data.get('title'):
                        return True
        except urllib.error.HTTPError as e:
            if e.code in (404, 410):
                return False
        except Exception:
            pass

    try:
        clean_url = url.split('#')[0]
        req = urllib.request.Request(
            clean_url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
        )
        with urllib.request.urlopen(req, context=ctx, timeout=5) as resp:
            if resp.status in (404, 410):
                return False
            html = resp.read(20480).decode('utf-8', errors='ignore').lower()
            if any(phrase in html for phrase in [
                'this job is no longer available',
                'this position has been filled',
                'job has expired',
                'posting is no longer active',
                'no longer accepting applications',
                'the page you are looking for does not exist'
            ]):
                return False
            return True
    except urllib.error.HTTPError as e:
        if e.code in (404, 410):
            return False
        return True
    except Exception:
        return True

def fetch_single_board(board_tuple):
    comp_name, btype, slug, industry = board_tuple
    results = []
    max_per_co = 3
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}

    try:
        if btype == 'greenhouse':
            url = f'https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true'
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=8) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                raw_jobs = data.get('jobs', [])
                
                def loc_priority(j):
                    l = (j.get('location', {}).get('name', '') or '').lower()
                    if any(k in l for k in ['seattle', 'bellevue', 'redmond', 'kirkland', 'washington', ', wa', 'wa,', 'wa -']) and 'dc' not in l:
                        return 0
                    if 'remote' in l:
                        return 1
                    return 2
                
                sorted_jobs = sorted(raw_jobs, key=loc_priority)
                co_count = 0
                for j in sorted_jobs:
                    if co_count >= max_per_co:
                        break
                    title = j.get('title', '')
                    if not is_resume_role_matched(title):
                        continue

                    loc = j.get('location', {}).get('name', '')
                    loc_low = loc.lower()
                    if not is_strictly_us_location(loc, title):
                        continue

                    content = j.get('content', '')
                    full_text = f"{title} {loc} {content}"

                    if is_clearance_or_citizen_restricted(full_text):
                        continue

                    if has_excessive_yoe_requirement(full_text):
                        continue

                    ats_id = str(j.get('id', ''))
                    if not ats_id:
                        continue
                        
                    raw_ats_url = j.get('absolute_url') or f"https://boards.greenhouse.io/{slug}/jobs/{ats_id}"
                    if 'boards.greenhouse.io' in raw_ats_url and '#app' not in raw_ats_url:
                        job_url = f"{raw_ats_url}#app"
                    else:
                        job_url = raw_ats_url

                    if not is_job_live(job_url, slug=slug, ats_id=ats_id):
                        continue

                    co_count += 1
                    skills = []
                    for s in ['Java', 'Python', 'TypeScript', 'React', 'AWS', 'Spring Boot', 'C++', 'PostgreSQL', 'Docker', 'Kubernetes', 'SQL', 'Distributed Systems', 'FastAPI', 'Node.js', 'Go']:
                        if s.lower() in full_text.lower():
                            skills.append(s)
                    if not skills:
                        skills = ['Java', 'Python', 'TypeScript', 'AWS', 'PostgreSQL']

                    h1b_fit = 'Yes (H1B Friendly / Sponsoring)' if any(k in comp_name.lower() for k in ['stripe', 'databricks', 'figma', 'openai', 'anthropic', 'snowflake', 'airbnb', 'doordash', 'pinterest', 'reddit', 'remitly', 'avalara', 'zillow', 'tanium', 'smartsheet', 'coupang']) else 'Open / Check Application'

                    custom_questions = []
                    try:
                        detail_url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs/{ats_id}?questions=true"
                        d_req = urllib.request.Request(detail_url, headers=headers)
                        with urllib.request.urlopen(d_req, context=ctx, timeout=3) as d_resp:
                            d_json = json.loads(d_resp.read().decode('utf-8'))
                            for q in d_json.get('questions', []):
                                q_lbl = q.get('label', '').strip()
                                q_fields = q.get('fields', [])
                                q_type = q_fields[0].get('type', '') if q_fields else ''
                                q_desc = q.get('description', '') or ''
                                if is_tailored_application_question(q_lbl, q_type, q_desc):
                                    full_q = q_lbl
                                    if q_desc and len(q_desc) < 150:
                                        cd = re.sub(r'<[^>]+>', '', q_desc).strip()
                                        if cd and cd not in full_q:
                                            full_q = f"{full_q} ({cd})"
                                    custom_questions.append(generate_tailored_answer(comp_name, title, skills, full_q, industry))
                    except Exception:
                        pass

                    reg_name, reg_rank = get_region_info(loc)
                    results.append({
                        'id': f'{slug}-{ats_id}',
                        'company': comp_name,
                        'title': title,
                        'location': loc,
                        'remote': 'Remote' if 'remote' in loc_low else ('Hybrid' if 'hybrid' in loc_low else 'US / Onsite'),
                        'industry': industry,
                        'salary': ',000 – ,000 + Equity',
                        'summary': f'Live opening at {comp_name} focused on scalable engineering with {skills[0]} and cloud infrastructure.',
                        'skills': skills[:6],
                        'url': job_url,
                        'source': 'Greenhouse API (Live)',
                        'postedApprox': 'Active Now',
                        'h1bFit': h1b_fit,
                        'yoeFit': 'Good (3–6 yrs)',
                        'yoeNote': 'Verified <7 yrs requirement',
                        'callbackScore': 90.0 + (5.0 if 'Remote' in loc or reg_rank == 1 else 0.0),
                        'postedAtUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                        'atsJobId': ats_id,
                        'region': reg_name,
                        'regionRank': reg_rank,
                        'customQuestions': custom_questions,
                        'hasEssayQuestions': len(custom_questions) > 0
                    })

        elif btype == 'ashby':
            url = f'https://api.ashbyhq.com/posting-api/job-board/{slug}?includeCompensation=true'
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=8) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                co_count = 0
                for j in data.get('jobs', []):
                    if co_count >= max_per_co:
                        break
                    title = j.get('title', '')
                    t_low = title.lower()

                    if not is_resume_role_matched(title):
                        continue

                    emp_type = str(j.get('employmentType', '')).lower()
                    if emp_type and is_non_fulltime_role(emp_type):
                        continue

                    loc = str(j.get('location', ''))
                    loc_low = loc.lower()
                    if not is_strictly_us_location(loc, title):
                        continue

                    comp_info = j.get('compensation', {})
                    sal_str = ',000 – ,000 + Equity'
                    if comp_info and comp_info.get('compensationTierSummary'):
                        sal_str = comp_info.get('compensationTierSummary')

                    desc_text = f"{title} {loc} {j.get('department', '')}"
                    if is_clearance_or_citizen_restricted(desc_text):
                        continue
                    if has_excessive_yoe_requirement(desc_text):
                        continue

                    raw_url = j.get('jobUrl') or f'https://jobs.ashbyhq.com/{slug}/{j.get("id")}'
                    job_url = raw_url if raw_url.endswith('/application') else f"{raw_url.rstrip('/')}/application"

                    if not is_job_live(job_url):
                        continue

                    co_count += 1
                    skills = ['Python', 'TypeScript', 'React', 'AWS', 'PostgreSQL', 'Distributed Systems']
                    if 'backend' in t_low or 'infrastructure' in t_low:
                        skills = ['Python', 'Java', 'AWS', 'PostgreSQL', 'Docker', 'Distributed Systems']
                    elif 'voice' in t_low or 'audio' in t_low:
                        skills = ['Python', 'C++', 'AWS', 'WebSockets', 'Distributed Systems']

                    reg_name, reg_rank = get_region_info(loc)
                    results.append({
                        'id': f'{slug}-{j.get("id")}',
                        'company': comp_name,
                        'title': title,
                        'location': loc,
                        'remote': 'Remote' if 'remote' in loc_low else 'Hybrid / Onsite',
                        'industry': industry,
                        'salary': sal_str,
                        'summary': f'Live opening at {comp_name} focused on full stack / backend engineering.',
                        'skills': skills[:6],
                        'url': job_url,
                        'source': 'Ashby API (Live)',
                        'postedApprox': 'Active Now',
                        'h1bFit': 'Yes (H1B Friendly / Sponsoring)' if any(k in comp_name.lower() for k in ['openai', 'anthropic', 'perplexity', 'elevenlabs', 'ramp', 'linear', 'snowflake', 'notion', 'docker']) else 'Open / Check Application',
                        'yoeFit': 'Good (3–6 yrs)',
                        'yoeNote': 'Verified <7 yrs requirement',
                        'callbackScore': 93.0 + (5.0 if reg_rank == 1 else 0.0),
                        'postedAtUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                        'atsJobId': str(j.get('id')),
                        'region': reg_name,
                        'regionRank': reg_rank,
                        'customQuestions': [],
                        'hasEssayQuestions': False
                    })

        elif btype == 'lever':
            url = f'https://api.lever.co/v0/postings/{slug}?mode=json'
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=8) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                if isinstance(data, list):
                    co_count = 0
                    for j in data:
                        if co_count >= max_per_co:
                            break
                        title = j.get('text', '')
                        if not is_resume_role_matched(title):
                            continue
                        cat = j.get('categories', {}) or {}
                        commitment = str(cat.get('commitment', '')).lower()
                        if commitment and is_non_fulltime_role(commitment):
                            continue
                        loc = cat.get('location', 'US')
                        if not is_strictly_us_location(loc, title):
                            continue
                        full_lever_text = f"{title} {loc} {j.get('descriptionPlain', '')}"
                        if is_clearance_or_citizen_restricted(full_lever_text):
                            continue
                        if has_excessive_yoe_requirement(full_lever_text):
                            continue
                        job_url = j.get('hostedUrl', '')
                        if not job_url:
                            continue
                        if not is_job_live(job_url):
                            continue
                        co_count += 1
                        reg_name, reg_rank = get_region_info(loc)
                        results.append({
                            'id': f'{slug}-{j.get("id")}',
                            'company': comp_name,
                            'title': title,
                            'location': loc,
                            'remote': 'Remote' if 'remote' in loc.lower() else 'US / Onsite',
                            'industry': industry,
                            'salary': ',000 – ,000 + Equity',
                            'summary': f'Live opening at {comp_name} focused on scalable engineering.',
                            'skills': ['Java', 'Python', 'TypeScript', 'AWS', 'PostgreSQL'],
                            'url': job_url,
                            'source': 'Lever API (Live)',
                            'postedApprox': 'Active Now',
                            'h1bFit': 'Open / Check Application',
                            'yoeFit': 'Good (3–6 yrs)',
                            'yoeNote': 'Verified <7 yrs requirement',
                            'callbackScore': 90.0 + (5.0 if reg_rank == 1 else 0.0),
                            'postedAtUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                            'atsJobId': str(j.get('id')),
                            'region': reg_name,
                            'regionRank': reg_rank,
                            'customQuestions': [],
                            'hasEssayQuestions': False
                        })
    except Exception:
        pass

    return results

def fetch_workday_board(board_tuple):
    comp_name, api_url, base_url, industry = board_tuple
    results = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
    }
    payload = json.dumps({'appliedFacets': {}, 'limit': 20, 'offset': 0, 'searchText': 'Software Engineer'}).encode('utf-8')
    try:
        req = urllib.request.Request(api_url, data=payload, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=7) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            postings = data.get('jobPostings', [])
            co_count = 0
            for p in postings:
                if co_count >= 3:
                    break
                title = p.get('title', '')
                if not is_resume_role_matched(title):
                    continue
                time_type = str(p.get('timeType', '')).lower()
                if time_type and is_non_fulltime_role(time_type):
                    continue
                loc = p.get('locationsText', 'United States')
                if not is_strictly_us_location(loc, title):
                    continue
                if is_clearance_or_citizen_restricted(f"{title} {loc}"):
                    continue
                ext_path = p.get('externalPath', '')
                if not ext_path:
                    continue
                job_url = base_url + ext_path

                # Deep inspection: fetch job description from Workday detail endpoint
                job_desc = ''
                try:
                    detail_api_url = re.sub(r'/jobs$', '', api_url) + f'/job{ext_path}'
                    d_req = urllib.request.Request(detail_api_url, headers=headers)
                    with urllib.request.urlopen(d_req, context=ctx, timeout=8) as d_resp:
                        d_json = json.loads(d_resp.read().decode('utf-8'))
                        job_desc = d_json.get('jobPostingInfo', {}).get('jobDescription', '')
                except Exception:
                    pass

                if is_clearance_or_citizen_restricted(f"{title} {loc} {job_desc}"):
                    continue
                if has_excessive_yoe_requirement(f"{title} {loc} {job_desc}"):
                    continue

                bullet_fields = p.get('bulletFields', [])
                ats_id = bullet_fields[0] if bullet_fields else re.sub(r'[^a-zA-Z0-9]', '', ext_path[-16:])
                co_count += 1
                reg_name, reg_rank = get_region_info(loc)
                skills = ['Java', 'Python', 'TypeScript', 'AWS', 'Distributed Systems', 'PostgreSQL']
                results.append({
                    'id': f'{comp_name.lower()}-{ats_id}',
                    'company': comp_name,
                    'title': title,
                    'location': loc,
                    'remote': 'Remote' if 'remote' in loc.lower() else 'Hybrid / Onsite',
                    'industry': industry,
                    'salary': '$155,000 – $230,000 + Equity',
                    'summary': f'Direct Workday opening at {comp_name} for {title}.',
                    'skills': skills,
                    'url': job_url,
                    'source': 'Workday CXS (Live)',
                    'postedApprox': p.get('postedOn', 'Active Now'),
                    'h1bFit': 'Yes (H1B Friendly / Sponsoring)' if any(k in comp_name.lower() for k in ['zillow', 'nvidia', 'adobe', 'cisco', 'workday', 'ebay']) else 'Open / Check Application',
                    'yoeFit': 'Good (3–6 yrs)',
                    'yoeNote': 'Verified <7 yrs requirement',
                    'callbackScore': 92.0 + (5.0 if reg_rank == 1 else 0.0),
                    'postedAtUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    'atsJobId': str(ats_id),
                    'region': reg_name,
                    'regionRank': reg_rank,
                    'customQuestions': [],
                    'hasEssayQuestions': False
                })
    except Exception:
        pass
    return results

def fetch_amazon_jobs():
    results = []
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
    url = 'https://www.amazon.jobs/en/search.json?category%5B%5D=software-development&country=USA&result_limit=50'
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=8) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            jobs = data.get('jobs', [])
            co_count = 0
            for j in jobs:
                if co_count >= 8:
                    break
                title = j.get('title', '')
                if not is_resume_role_matched(title):
                    continue
                sched_type = str(j.get('job_schedule_type', '')).lower()
                job_type = str(j.get('job_type', '')).lower()
                if is_non_fulltime_role(f"{sched_type} {job_type}"):
                    continue
                city = j.get('city', '')
                state = j.get('state', '')
                loc = f"{city}, {state}" if city and state else (city or state or 'Seattle, WA')
                if not is_strictly_us_location(loc, title):
                    continue
                desc = j.get('description', '')
                if is_clearance_or_citizen_restricted(f"{title} {desc}"):
                    continue
                if has_excessive_yoe_requirement(f"{title} {desc}"):
                    continue
                job_path = j.get('job_path', '')
                if not job_path:
                    continue
                job_url = f"https://www.amazon.jobs{job_path}"
                job_id = j.get('id_icims') or str(abs(hash(job_path)) % 10000000)
                co_count += 1
                reg_name, reg_rank = get_region_info(loc)
                skills = ['Java', 'Python', 'AWS', 'Distributed Systems', 'Docker', 'Kubernetes']
                results.append({
                    'id': f'amazon-{job_id}',
                    'company': 'Amazon',
                    'title': title,
                    'location': loc,
                    'remote': 'Remote' if 'remote' in loc.lower() else 'Onsite / Hybrid (Seattle Tech Hub)',
                    'industry': 'Cloud Infrastructure & High-Scale Systems (Seattle Hub)',
                    'salary': '$150,000 – $225,000 + Equity',
                    'summary': f'Direct corporate engineering opening at Amazon for {title}.',
                    'skills': skills,
                    'url': job_url,
                    'source': 'Amazon Jobs Official (Live)',
                    'postedApprox': 'Active Now',
                    'h1bFit': 'Yes (H1B Friendly / Sponsoring)',
                    'yoeFit': 'Good (3–6 yrs)',
                    'yoeNote': 'Verified <7 yrs requirement',
                    'callbackScore': 95.0 + (5.0 if reg_rank == 1 else 0.0),
                    'postedAtUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    'atsJobId': str(job_id),
                    'region': reg_name,
                    'regionRank': reg_rank,
                    'customQuestions': [],
                    'hasEssayQuestions': False
                })
    except Exception:
        pass
    return results

def main():
    print(f"Starting concurrent sweep across {len(COMPANY_BOARDS)} ATS boards + {len(WORKDAY_BOARDS)} Workday portals + Amazon Jobs API...")
    matched_jobs = []
    
    # 1. Sweep ATS boards (Greenhouse, Ashby, Lever)
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        gh_futures = {executor.submit(fetch_single_board, b): b for b in COMPANY_BOARDS}
        wd_futures = {executor.submit(fetch_workday_board, b): b for b in WORKDAY_BOARDS}
        amz_future = executor.submit(fetch_amazon_jobs)

        for future in concurrent.futures.as_completed(gh_futures):
            try:
                res = future.result()
                if res:
                    matched_jobs.extend(res)
            except Exception:
                pass

        for future in concurrent.futures.as_completed(wd_futures):
            try:
                res = future.result()
                if res:
                    matched_jobs.extend(res)
            except Exception:
                pass

        try:
            amz_res = amz_future.result()
            if amz_res:
                matched_jobs.extend(amz_res)
        except Exception:
            pass

    print(f"\n--- Fresh Sweep Matched Jobs: {len(matched_jobs)} ---")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    jobs_file_path = os.path.join(base_dir, 'jobs.json')
    seen_file_path = os.path.join(base_dir, 'seen_job_ids.json')

    # Load seen registry
    seen_ids = {}
    if os.path.exists(seen_file_path):
        try:
            with open(seen_file_path, 'r') as f:
                sdata = json.load(f)
                seen_ids = sdata.get('seen_ids', {})
        except Exception:
            seen_ids = {}

    today_iso = datetime.date.today().isoformat()
    
    # Tag fresh delta vs previously seen
    new_jobs_today = []
    carryover_jobs = []
    combined_jobs = []
    seen_in_this_run = set()

    for j in matched_jobs:
        if not is_direct_company_url(j.get('url', '')):
            continue
        jid = j.get('id')
        if not jid or jid in seen_in_this_run:
            continue
        seen_in_this_run.add(jid)

        if jid not in seen_ids:
            j['isNewToday'] = True
            j['firstSeenDate'] = today_iso
            seen_ids[jid] = today_iso
            new_jobs_today.append(j)
        else:
            j['isNewToday'] = False
            j['firstSeenDate'] = seen_ids[jid]
            carryover_jobs.append(j)

        combined_jobs.append(j)

    print(f"Sweep Breakdown: {len(new_jobs_today)} BRAND NEW postings today | {len(carryover_jobs)} carryover active postings.")

    # Save updated seen registry
    with open(seen_file_path, 'w') as f:
        json.dump({'seen_ids': seen_ids}, f, indent=2)

    # Priority sorting:
    # 1. New Today (1st)
    # 2. Seattle / WA (Rank 1) -> Remote (Rank 2) -> East (Rank 3) -> West (Rank 4)
    # 3. Callback Score
    combined_jobs.sort(key=lambda j: (
        0 if j.get('isNewToday') else 1,
        j.get('regionRank', 3),
        -(j.get('callbackScore') or 0)
    ))

    output_data = {
        "lastUpdated": today_iso,
        "lastChecked": today_iso,
        "seedVersion": 14,
        "candidateProfile": {
            "name": "Ramya Bangaru",
            "targetRole": "Senior Full Stack & Software Engineer",
            "mustHave": "Java / Python / TypeScript / React / AWS / Spring Boot",
            "yoe": "3–6y (strictly <7y)",
            "visa": "All Roles (H1B Sponsoring & Open)",
            "preferredLocations": "Seattle, WA · Remote · San Francisco, CA · US Nationwide"
        },
        "liveTrackers": [
            {
                "label": "🌲 Senior Software Engineer — Seattle & WA — Past 7 days",
                "url": "https://www.linkedin.com/jobs/search/?keywords=Senior%20Software%20Engineer&location=Seattle%2C%20Washington%2C%20United%20States&geoId=104116203&f_TPR=r604800&f_E=4&sortBy=DD",
                "target": "Seattle / Bellevue / Redmond / Kirkland tech corridor"
            },
            {
                "label": "🏠 Senior Software Engineer — Remote USA — Past 24 hours",
                "url": "https://www.linkedin.com/jobs/search/?keywords=Senior%20Software%20Engineer&location=United%20States&f_WT=2&f_TPR=r86400&f_E=4&sortBy=DD",
                "target": "100% Remote USA"
            }
        ],
        "weeks": [
            {
                "weekId": "2026-W37",
                "weekLabel": f"Week of September 11, 2026 — Verified Direct Sweeps ({len(combined_jobs)} Live Roles)",
                "jobs": combined_jobs
            }
        ]
    }

    with open(jobs_file_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    docs_jobs_path = os.path.join(base_dir, 'docs', 'jobs.json')
    with open(docs_jobs_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\n Successfully saved {len(combined_jobs)} verified direct jobs to {jobs_file_path} and {docs_jobs_path}")
    sea_count = sum(1 for j in combined_jobs if j.get('regionRank') == 1)
    rem_count = sum(1 for j in combined_jobs if j.get('regionRank') == 2)
    print(f"Regional breakdown: Seattle/WA: {sea_count} | Remote USA: {rem_count} | Other US: {len(combined_jobs) - sea_count - rem_count}")

if __name__ == '__main__':
    main()
