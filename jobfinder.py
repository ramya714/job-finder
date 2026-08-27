#!/usr/bin/env python3
from __future__ import annotations
"""
JobFinder: Automated Daily Job Search Engine
Fetches, filters, and reports unseen jobs from 150+ public job boards (Greenhouse, Ashby, Lever).
Zero external dependencies (pure standard library Python 3).
"""

import argparse
import concurrent.futures
import html
import hashlib
import json
import os
import platform
import re
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

# Global socket timeout for non-blocking HTTP requests
socket.setdefaulttimeout(5)
from datetime import datetime
from pathlib import Path

VERSION = "1.0.0"

# Built-in directory of 150+ top tech, AI, fintech, and high-growth companies
COMPANIES = [
    # Top AI & Machine Learning Labs
    ("Anthropic", "greenhouse", "anthropic"),
    ("OpenAI", "ashby", "openai"),
    ("Perplexity AI", "ashby", "perplexity"),
    ("Scale AI", "greenhouse", "scaleai"),
    ("Mistral AI", "ashby", "mistralai"),
    ("ElevenLabs", "ashby", "elevenlabs"),
    ("Cursor / Anysphere", "ashby", "anysphere"),
    ("Together AI", "ashby", "togetherai"),
    ("Runway", "greenhouse", "runwayml"),
    ("Stability AI", "greenhouse", "stabilityai"),
    ("Hugging Face", "greenhouse", "huggingface"),
    ("Weights & Biases", "greenhouse", "wandb"),
    ("Character.ai", "greenhouse", "character"),
    ("Pinecone", "greenhouse", "pinecone"),
    ("Groq", "greenhouse", "groq"),
    ("Replicate", "ashby", "replicate"),
    ("Modal Labs", "ashby", "modal"),
    ("Writer", "ashby", "writer"),
    ("LangChain", "ashby", "langchain"),
    ("Braintrust", "ashby", "braintrust"),
    ("Harvey AI", "ashby", "harvey"),
    ("Poolside AI", "ashby", "poolside"),
    ("Decart AI", "ashby", "decart"),
    ("Magic.dev", "ashby", "magic"),
    ("Cognition / Devin", "ashby", "cognition"),
    ("Codeium", "ashby", "codeium"),
    ("Fireworks AI", "ashby", "fireworksai"),
    ("Baseten", "ashby", "baseten"),
    ("RunPod", "ashby", "runpod"),
    ("DeepL", "greenhouse", "deepl"),
    ("Glean", "greenhouse", "glean"),
    ("Descript", "greenhouse", "descript"),
    ("Synthesia", "greenhouse", "synthesia"),
    ("HeyGen", "ashby", "heygen"),
    ("Pika", "ashby", "pika"),
    ("Suno AI", "ashby", "suno"),
    ("Udio", "ashby", "udio"),
    ("Augment Code", "ashby", "augmentcode"),
    ("Factory AI", "ashby", "factory"),
    ("Tabnine", "greenhouse", "tabnine"),
    ("Otter.ai", "greenhouse", "otterai"),

    # High Frequency Trading & Quantitative Finance
    ("Hudson River Trading", "greenhouse", "wehrtyou"),  # Note: HRT uses 'wehrtyou' slug
    ("Jane Street", "greenhouse", "janestreet"),
    ("Citadel", "greenhouse", "citadel"),
    ("Two Sigma", "greenhouse", "twosigma"),
    ("Jump Trading", "greenhouse", "jumptrading"),
    ("DRW", "greenhouse", "drw"),
    ("Optiver", "greenhouse", "optiver"),
    ("Point72", "greenhouse", "point72"),
    ("Flow Traders", "greenhouse", "flowtraders"),

    # Fintech, Payments & Neobanks
    ("Stripe", "greenhouse", "stripe"),
    ("Ramp", "greenhouse", "ramp"),
    ("Brex", "greenhouse", "brex"),
    ("Plaid", "greenhouse", "plaid"),
    ("Robinhood", "greenhouse", "robinhood"),
    ("Coinbase", "greenhouse", "coinbase"),
    ("Carta", "greenhouse", "carta"),
    ("Affirm", "greenhouse", "affirm"),
    ("Toast", "greenhouse", "toast"),
    ("Chime", "greenhouse", "chime"),
    ("Deel", "greenhouse", "deel"),
    ("Rippling", "greenhouse", "rippling"),
    ("Gusto", "greenhouse", "gusto"),
    ("Remote", "greenhouse", "remote"),
    ("Klarna", "greenhouse", "klarna"),
    ("Marqeta", "greenhouse", "marqeta"),

    # Developer Tools, Cloud, Infrastructure & Data
    ("Vercel", "greenhouse", "vercel"),
    ("Supabase", "ashby", "supabase"),
    ("Linear", "ashby", "linear"),
    ("Retool", "greenhouse", "retool"),
    ("Datadog", "greenhouse", "datadog"),
    ("Snowflake", "greenhouse", "snowflake"),
    ("Databricks", "greenhouse", "databricks"),
    ("Figma", "greenhouse", "figma"),
    ("Notion", "greenhouse", "notion"),
    ("Airtable", "greenhouse", "airtable"),
    ("Discord", "greenhouse", "discord"),
    ("GitLab", "greenhouse", "gitlab"),
    ("HashiCorp", "greenhouse", "hashicorp"),
    ("Docker", "greenhouse", "docker"),
    ("Postman", "greenhouse", "postman"),
    ("Grafana Labs", "greenhouse", "grafanalabs"),
    ("MongoDB", "greenhouse", "mongodb"),
    ("ClickHouse", "greenhouse", "clickhouse"),
    ("Temporal", "ashby", "temporal"),
    ("PlanetScale", "ashby", "planetscale"),
    ("Neon Database", "ashby", "neon"),
    ("Sentry", "greenhouse", "sentry"),
    ("Fly.io", "greenhouse", "flyio"),
    ("Render", "ashby", "render"),
    ("Railway", "ashby", "railway"),
    ("Warp", "ashby", "warp"),
    ("Sourcegraph", "greenhouse", "sourcegraph"),
    ("Cockroach Labs", "greenhouse", "cockroachlabs"),
    ("Elastic", "greenhouse", "elastic"),
    ("Confluent", "greenhouse", "confluent"),
    ("Twilio", "greenhouse", "twilio"),
    ("dbt Labs", "greenhouse", "dbtlabs"),
    ("Fivetran", "greenhouse", "fivetran"),
    ("Census", "greenhouse", "census"),
    ("Hex", "greenhouse", "hex"),
    ("Monte Carlo", "greenhouse", "montecarlodata"),
    ("Amplitude", "greenhouse", "amplitude"),
    ("Mixpanel", "greenhouse", "mixpanel"),
    ("LaunchDarkly", "greenhouse", "launchdarkly"),
    ("Harness", "greenhouse", "harness"),
    ("Sysdig", "greenhouse", "sysdig"),
    ("Snyk", "greenhouse", "snyk"),
    ("Wiz", "greenhouse", "wiz"),
    ("SentinelOne", "greenhouse", "sentinelone"),
    ("CrowdStrike", "greenhouse", "crowdstrike"),
    ("Netskope", "greenhouse", "netskope"),
    ("Okta", "greenhouse", "okta"),
    ("1Password", "greenhouse", "1password"),
    ("Bitwarden", "greenhouse", "bitwarden"),
    ("Tailscale", "greenhouse", "tailscale"),
    ("Clerk", "ashby", "clerk"),
    ("Resend", "ashby", "resend"),
    ("Inngest", "ashby", "inngest"),
    ("Trigger.dev", "ashby", "triggerdev"),
    ("Cal.com", "ashby", "calcom"),
    ("Dub.co", "ashby", "dub"),
    ("Automattic", "greenhouse", "automattic"),
    ("Mozilla", "greenhouse", "mozilla"),
    ("Fastly", "greenhouse", "fastly"),
    ("DigitalOcean", "greenhouse", "digitalocean"),
    ("Lambda Labs", "greenhouse", "lambdalabs"),
    ("Coda", "greenhouse", "coda"),
    ("Gitpod", "greenhouse", "gitpod"),
    ("CodeSandbox", "ashby", "codesandbox"),
    ("StackBlitz", "ashby", "stackblitz"),
    ("Replit", "greenhouse", "replit"),
    ("Zed Industries", "ashby", "zed"),

    # Consumer, Mobility, Hardware & Robotics
    ("Reddit", "greenhouse", "reddit"),
    ("Pinterest", "greenhouse", "pinterest"),
    ("Snap", "greenhouse", "snap"),
    ("Instacart", "greenhouse", "instacart"),
    ("DoorDash", "greenhouse", "doordash"),
    ("Uber", "greenhouse", "uber"),
    ("Lyft", "greenhouse", "lyft"),
    ("Airbnb", "greenhouse", "airbnb"),
    ("Spotify", "greenhouse", "spotify"),
    ("Roku", "greenhouse", "roku"),
    ("Roblox", "greenhouse", "roblox"),
    ("Unity", "greenhouse", "unity"),
    ("Niantic", "greenhouse", "niantic"),
    ("Cruise", "greenhouse", "cruise"),
    ("Waymo", "greenhouse", "waymo"),
    ("Aurora Innovation", "greenhouse", "aurora"),
    ("Zoox", "greenhouse", "zoox"),
    ("Nuro", "greenhouse", "nuro"),
    ("Verkada", "greenhouse", "verkada"),
    ("Samsara", "greenhouse", "samsara"),
    ("Astranis", "greenhouse", "astranis"),
    ("Joby Aviation", "greenhouse", "jobyaviation"),
    ("Archer Aviation", "greenhouse", "archeraviation"),
    ("Zipline", "greenhouse", "zipline"),
    ("Flexport", "greenhouse", "flexport"),
    ("Checkr", "greenhouse", "checkr"),
    ("Grammarly", "greenhouse", "grammarly"),
    ("Canva", "greenhouse", "canva"),
    ("Duolingo", "greenhouse", "duolingo"),
    ("Asana", "greenhouse", "asana"),
    ("Zapier", "greenhouse", "zapier"),
    ("Miro", "greenhouse", "miro"),
]

# Companies with explicit non-sponsorship policies in US postings
NON_SPONSOR_COMPANIES = {
    "caterpillar", "boston scientific", "philips", "motorola solutions",
    "paypal", "ge healthcare", "trimble", "rockwell automation",
    "ericsson us", "ericsson", "ninjaone", "omnissa", "cox", "medtronic"
}

# Export-control / ITAR restricted companies for US roles
ITAR_COMPANIES = {
    "applied materials", "analog devices", "cloudflare", "palantir",
    "coreweave", "kodiak", "sambanova", "qumulo", "illumio", "lightmatter",
    "anduril", "spacex", "shield ai", "lockheed", "lockheed martin",
    "raytheon", "rtx", "northrop", "northrop grumman", "booz allen",
    "amentum", "l3harris", "leidos", "saic"
}

# Staffing firms, aggregators, and spam listings
STAFFING_COMPANIES = {
    "ladders", "alignerr", "fetchjobs", "turing", "crossing hurdles",
    "toptal", "jobgether", "teksystems", "insight global", "robert half",
    "apex systems", "apex", "actalent", "collabera", "diverse lynx",
    "cybercoders", "kforce", "randstad", "adecco", "aerotek", "beacon hill",
    "motion recruitment", "dice", "jobot"
}

# Explicit sponsorship refusal phrases
SPONSORSHIP_REFUSAL_PATTERNS = [
    r"\bunable to sponsor\b",
    r"\bno sponsorship\b",
    r"\bwill not sponsor\b",
    r"\bcannot sponsor\b",
    r"\bnot able to sponsor\b",
    r"\bnot offer(?:ing)? sponsorship\b",
    r"\bdoes not offer sponsorship\b",
    r"\bvisa sponsorship is not available\b",
    r"\bvisa sponsorship not available\b",
    r"\bsponsorship is not available\b",
    r"\bsponsorship not available\b",
    r"\bsponsorship is not offered\b",
    r"\bwithout (?:company )?sponsorship\b",
    r"\bwithout sponsorship now or in the future\b",
    r"\bwithout the need for (?:visa )?sponsorship\b",
    r"\bnot eligible for visa sponsorship\b",
    r"\bcitizenship required\b",
    r"\bus citizen(?:ship)? (?:only|required)\b",
    r"\bu\.s\. citizen(?:ship)? (?:only|required)\b",
    r"\bsecurity clearance\b",
    r"\btop secret\b",
    r"\bactive clearance\b",
    r"\bdod clearance\b",
    r"\bitar\b",
    r"\bexport control(?:led)?\b",
    r"\bu\.s\. person\b",
    r"\bus person\b",
    r"\bgreen card or us citizen\b",
    r"\bgreen card holder\b",
]

# Explicit positive sponsorship phrases
SPONSORSHIP_POSITIVE_PATTERNS = [
    r"\bvisa sponsorship is available\b",
    r"\bvisa sponsorship available\b",
    r"\bsponsorship is available\b",
    r"\bsponsorship available\b",
    r"\bvisa sponsorship provided\b",
    r"\bwill sponsor\b",
    r"\bwe sponsor (?:visas|h-?1b)\b",
    r"\bsponsors h-?1b\b",
    r"\bvisa support provided\b",
    r"\bcan sponsor\b",
    r"\bopen to sponsoring\b",
    r"\bassistance with visa\b",
]

DEFAULT_PROFILE = {
    "primary_skill": "Python",
    "min_skill_count": 2,
    "must_also_mention": [],
    "max_years_experience": 5,
    "senior_title_exclusions": [
        "principal", "distinguished", "fellow", "architect",
        "director", "head of", "staff", "vp", "vice president",
        "manager", "intern", "internship", "new grad", "student", "co-op", "coop"
    ],
    "require_visa_sponsorship": True,
    "locations_allow": [
        "remote", "us", "united states", "usa",
        "san francisco", "sf", "bay area", "new york", "nyc", "seattle",
        "austin", "boston", "chicago", "los angeles", "sunnyvale",
        "mountain view", "palo alto", "san jose", "redmond", "cambridge"
    ],
    "locations_deny": [
        "canada", "uk", "london", "india", "bangalore", "bengaluru",
        "berlin", "singapore", "germany", "france", "australia", "sydney",
        "melbourne", "toronto", "vancouver", "dublin", "ireland", "tokyo",
        "japan", "netherlands", "amsterdam", "brazil", "mexico", "poland"
    ],
    "favorite_companies": [],
    "excluded_companies": [],
    "extra_companies": [],
    "max_jobs_per_company": 1,
    "auth": {
        "enabled": True,
        "username": "ramya",
        "password": "jobfinder2025"
    }
}


def strip_html(html_str: str) -> str:
    """Removes HTML tags and decodes HTML entities."""
    if not html_str:
        return ""
    text = re.sub(r"<style[\s\S]*?</style>", " ", html_str, flags=re.IGNORECASE)
    text = re.sub(r"<script[\s\S]*?</script>", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


SKILL_ALIASES = {
    "c++": [r"\bc\+\+\b", r"\bcpp\b"],
    "javascript": [r"\bjavascript\b", r"\bjs\b"],
    "typescript": [r"\btypescript\b", r"\bts\b"],
    "postgresql": [r"\bpostgresql\b", r"\bpostgres\b", r"\bpsql\b"],
    "spring boot": [r"\bspring\s+boot\b", r"\bspring\s+framework\b", r"\bspring\b"],
    "next.js": [r"\bnext\.js\b", r"\bnextjs\b", r"\bnext\s+js\b"],
    "node.js": [r"\bnode\.js\b", r"\bnodejs\b", r"\bnode\s+js\b"],
    "aws": [r"\baws\b", r"\bamazon\s+web\s+services\b"],
    "azure": [r"\bazure\b", r"\bmicrosoft\s+azure\b"],
    "oracle db": [r"\boracle(?:\s+db|\s+database)?\b"],
    "github actions": [r"\bgithub\s+actions\b", r"\bgh\s+actions\b"],
    "golang": [r"\bgolang\b", r"\bgo\b"],
}


def count_skill_occurrences(text: str, skill: str) -> int:
    """Counts non-overlapping occurrences of the skill using safe boundaries and aliases."""
    if not skill or not text:
        return 0
    
    skill_clean = skill.strip().lower()
    if skill_clean in SKILL_ALIASES:
        total = 0
        for pattern in SKILL_ALIASES[skill_clean]:
            total += len(re.findall(pattern, text, flags=re.IGNORECASE))
        return total

    # Special handling for skills with non-alphanumeric chars like C#, .NET
    escaped = re.escape(skill)
    prefix = r"\b" if re.match(r"^\w", skill) else r"(?:^|\s|[(\[{/<,])"
    suffix = r"\b" if re.match(r".*\w$", skill) else r"(?:$|\s|[)\]}/>,.:;!?])"
    pattern = f"{prefix}{escaped}{suffix}"
    matches = re.findall(pattern, text, flags=re.IGNORECASE)
    return len(matches)


def parse_min_experience(text: str) -> int | None:
    """Extracts minimum years of experience required from posting text."""
    if not text:
        return None

    # Matches patterns like '3+ years', '3-5 years', 'at least 3 years', '3 to 5 years'
    patterns = [
        r"(\d{1,2})\s*(?:-\s*(\d{1,2})|\s+to\s+(\d{1,2}))?\s*\+?\s*years?(?:\s+of)?(?:\s+(?:relevant|professional|software|engineering|industry|hands-on|work|related))?(?:\s+experience)?",
        r"(?:minimum|at least|req(?:uire[sd])?)\s+(\d{1,2})\s*\+?\s*years?",
    ]

    found_years = []
    for pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            # Take the first number in the match (the lower bound)
            for g in match.groups():
                if g and g.isdigit():
                    val = int(g)
                    # Filter out unreasonable numbers like 30 years or 1999 (years)
                    if 0 < val <= 25:
                        found_years.append(val)
                    break

    if found_years:
        return min(found_years)
    return None


def is_title_excluded(title: str, exclusions: list[str]) -> bool:
    """
    Checks if job title contains excluded senior/intern terms.
    Special rule: 'Member of Technical Staff' or 'MTS' is NOT treated as Staff level.
    """
    title_lower = title.lower()
    
    # Exemption for Member of Technical Staff
    if "member of technical staff" in title_lower or re.search(r"\bmts\b", title_lower):
        # Only exclude if other explicit exclusion matches (like manager or director)
        for term in exclusions:
            if term.lower() == "staff":
                continue
            if re.search(rf"\b{re.escape(term.lower())}\b", title_lower):
                return True
        return False

    for term in exclusions:
        term_clean = term.strip().lower()
        if not term_clean:
            continue
        if re.search(rf"\b{re.escape(term_clean)}\b", title_lower):
            return True
    return False


def check_sponsorship_status(company: str, text: str, title: str) -> tuple[bool, bool, str]:
    """
    Returns (rejected_due_to_visa, has_explicit_sponsorship, reason).
    """
    company_lower = company.strip().lower()
    
    # 1. Hardcoded non-sponsoring companies
    for non_sp in NON_SPONSOR_COMPANIES:
        if non_sp in company_lower:
            # Special case for Medtronic: sponsors principal+
            if "medtronic" in non_sp and "principal" in title.lower():
                pass
            else:
                return True, False, f"Company '{company}' does not offer visa sponsorship in US"

    # 2. Hardcoded ITAR / Export-control companies
    for itar in ITAR_COMPANIES:
        if itar in company_lower:
            return True, False, f"Company '{company}' is subject to US ITAR/Export-control restrictions"

    # 3. Check for explicit refusal phrases in job description
    for pattern in SPONSORSHIP_REFUSAL_PATTERNS:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return True, False, f"Posting states: '{match.group(0)}'"

    # 4. Check for positive explicit sponsorship
    explicit_positive = False
    for pattern in SPONSORSHIP_POSITIVE_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            explicit_positive = True
            break

    return False, explicit_positive, ""


def check_location(location_str: str, text: str, allowed_locations: list[str], denied_locations: list[str]) -> tuple[bool, str]:
    """Verifies location against allow-list and deny-list."""
    loc_combined = f"{location_str} {text[:300]}".lower()

    # Check deny-list first
    for denied in denied_locations:
        denied_clean = denied.strip().lower()
        if not denied_clean:
            continue
        if re.search(rf"\b{re.escape(denied_clean)}\b", loc_combined):
            # Check if it also explicitly says Remote - US
            if "united states" not in loc_combined and "us remote" not in loc_combined and "remote - us" not in loc_combined:
                return False, f"Matched denied location '{denied}'"

    # Check allow-list
    if not allowed_locations:
        return True, "All locations allowed"

    for allowed in allowed_locations:
        allowed_clean = allowed.strip().lower()
        if not allowed_clean:
            continue
        if re.search(rf"\b{re.escape(allowed_clean)}\b", loc_combined):
            return True, f"Matched location '{allowed}'"

    # If location is unspecified or says Remote
    if "remote" in loc_combined or "anywhere" in loc_combined:
        return True, "Remote position"

    return False, f"Location '{location_str}' not in allow-list"


def fetch_board_jobs(company_name: str, board_type: str, slug: str) -> list[dict]:
    """Fetches job postings from public APIs (Greenhouse, Ashby, Lever)."""
    jobs = []
    board_type = board_type.lower()
    headers = {
        "User-Agent": "Mozilla/5.0 (JobFinder/1.0; +https://github.com/jobfinder)"
    }

    try:
        if board_type == "greenhouse":
            url = f"https://boards-api.greenhouse.io/v1/boards/{urllib.parse.quote(slug)}/jobs?content=true"
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=12) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    raw_jobs = data.get("jobs", [])
                    for j in raw_jobs:
                        loc_name = ""
                        if isinstance(j.get("location"), dict):
                            loc_name = j["location"].get("name", "")
                        elif isinstance(j.get("location"), str):
                            loc_name = j.get("location", "")
                        
                        content = j.get("content", "")
                        plain_desc = strip_html(content)
                        jobs.append({
                            "id": f"gh_{slug}_{j.get('id')}",
                            "company": company_name,
                            "slug": slug,
                            "board": "greenhouse",
                            "title": j.get("title", "").strip(),
                            "url": j.get("absolute_url", ""),
                            "location": loc_name,
                            "description": plain_desc,
                            "raw_content": content,
                            "updated_at": j.get("updated_at", "")
                        })

        elif board_type == "ashby":
            url = f"https://api.ashbyhq.com/posting-api/job-board/{urllib.parse.quote(slug)}?includeCompensation=true"
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=12) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    raw_jobs = data.get("jobPostings") or data.get("jobs") or []
                    for j in raw_jobs:
                        loc_name = j.get("locationName", "")
                        sec_locs = j.get("secondaryLocations", [])
                        loc_parts = [loc_name] if loc_name else []
                        for l in sec_locs:
                            if isinstance(l, dict):
                                l_str = l.get("locationName") or l.get("location") or l.get("name") or ""
                                if l_str and l_str not in loc_parts:
                                    loc_parts.append(str(l_str))
                            elif isinstance(l, str) and l and l not in loc_parts:
                                loc_parts.append(l)
                        
                        clean_loc = ", ".join(loc_parts) if loc_parts else (j.get("departmentName") or "Remote / US")

                        desc_html = j.get("descriptionHtml", "")
                        desc_plain = strip_html(desc_html) or j.get("descriptionPlain", "")
                        jobs.append({
                            "id": f"ashby_{slug}_{j.get('id')}",
                            "company": company_name,
                            "slug": slug,
                            "board": "ashby",
                            "title": j.get("title", "").strip(),
                            "url": j.get("jobUrl", f"https://jobs.ashbyhq.com/{slug}/{j.get('id')}"),
                            "location": clean_loc,
                            "description": desc_plain,
                            "raw_content": desc_html,
                            "updated_at": j.get("publishedAt", "")
                        })

        elif board_type == "workday":
            # slug format: "tenant:site:wdN" e.g. "nvidia:NVIDIAExternalCareerSite:wd5"
            parts = slug.split(":")
            if len(parts) >= 2:
                tenant = parts[0]
                site = parts[1]
                wd_num = parts[2] if len(parts) > 2 else "wd1"
                url = f"https://{tenant}.{wd_num}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs"
                payload = json.dumps({"searchText": "", "limit": 20, "offset": 0, "appliedFacets": {}}).encode("utf-8")
                wd_req = urllib.request.Request(url, data=payload, headers={
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (JobFinder/1.0)"
                })
                with urllib.request.urlopen(wd_req, timeout=12) as response:
                    if response.status == 200:
                        wd_data = json.loads(response.read().decode("utf-8"))
                        for item in wd_data.get("jobPostings", []):
                            jobs.append({
                                "id": f"wd_{tenant}_{item.get('bulletFields', [''])[0] or item.get('title')}",
                                "company": company_name,
                                "slug": slug,
                                "board": "workday",
                                "title": item.get("title", "").strip(),
                                "url": f"https://{tenant}.{wd_num}.myworkdayjobs.com/en-US/{site}" + item.get("externalPath", ""),
                                "location": item.get("locationsText", "US"),
                                "description": item.get("title", ""),
                                "raw_content": "",
                                "updated_at": item.get("postedOn", "")
                            })

        elif board_type == "lever":
            url = f"https://api.lever.co/v0/postings/{urllib.parse.quote(slug)}?mode=json"
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=12) as response:
                if response.status == 200:
                    raw_jobs = json.loads(response.read().decode("utf-8"))
                    if isinstance(raw_jobs, list):
                        for j in raw_jobs:
                            categories = j.get("categories", {}) or {}
                            loc_name = categories.get("location", "")
                            workplace_type = categories.get("workplaceType", "")
                            if workplace_type and workplace_type.lower() not in loc_name.lower():
                                loc_name = f"{loc_name} ({workplace_type})" if loc_name else workplace_type

                            desc = j.get("descriptionPlain", "")
                            if not desc and j.get("description"):
                                desc = strip_html(j["description"])
                            
                            # Lever lists lists of additional requirements in lists
                            additional = j.get("additionalPlain", "") or strip_html(j.get("additional", ""))
                            full_desc = f"{desc}\n{additional}".strip()

                            jobs.append({
                                "id": f"lever_{slug}_{j.get('id')}",
                                "company": company_name,
                                "slug": slug,
                                "board": "lever",
                                "title": j.get("text", "").strip(),
                                "url": j.get("hostedUrl", ""),
                                "location": loc_name,
                                "description": full_desc,
                                "raw_content": j.get("description", ""),
                                "updated_at": str(j.get("createdAt", ""))
                            })

    except urllib.error.HTTPError as e:
        # A 404/400 just means board is inactive or slug differs; ignore silently
        pass
    except Exception as e:
        pass

    return jobs


def evaluate_job(job: dict, profile: dict) -> tuple[bool, dict]:
    """
    Evaluates a single job posting against user profile criteria.
    Returns (passed_filter, details_dict).
    """
    title = job.get("title", "")
    desc = job.get("description", "")
    full_text = f"{title}\n{desc}"
    company = job.get("company", "")
    loc = job.get("location", "")

    # 1. Staffing / Aggregator check
    for staff in STAFFING_COMPANIES:
        if staff in company.lower() or staff in title.lower():
            return False, {"reason": f"Staffing/Aggregator '{staff}'"}

    # 2. Excluded companies from profile
    for exc in profile.get("excluded_companies", []):
        if exc.strip().lower() in company.lower():
            return False, {"reason": f"User excluded company '{exc}'"}

    # 3. Title senior / intern exclusions (with MTS exemption)
    exclusions = profile.get("senior_title_exclusions", DEFAULT_PROFILE["senior_title_exclusions"])
    if is_title_excluded(title, exclusions):
        return False, {"reason": f"Title matched senior/intern exclusion in '{title}'"}

    # 4. Primary skill occurrence count (supports list of skills or comma-separated skills)
    primary_skills = profile.get("primary_skills", [])
    if not primary_skills:
        raw_skill = profile.get("primary_skill", "Python")
        if "," in raw_skill:
            primary_skills = [s.strip() for s in raw_skill.split(",") if s.strip()]
        else:
            primary_skills = [raw_skill.strip()] if raw_skill.strip() else ["Python"]

    min_count = profile.get("min_skill_count", 2)
    
    skill_counts = {}
    matched_skills = []
    total_skill_count = 0

    for sk in primary_skills:
        cnt = count_skill_occurrences(full_text, sk)
        if cnt > 0:
            skill_counts[sk] = cnt
            total_skill_count += cnt
            matched_skills.append(f"{sk} ({cnt}x)")

    max_count = max(skill_counts.values()) if skill_counts else 0

    # Pass if at least one skill reaches min_count OR total mentions across stack >= min_count
    if max_count < min_count and total_skill_count < min_count:
        skills_summary = ", ".join(primary_skills[:4])
        return False, {"reason": f"Skills [{skills_summary}] appeared {total_skill_count}x (min required: {min_count})"}

    # Secondary skills bonus (e.g. frameworks/devops/databases)
    secondary_skills = profile.get("secondary_skills", [])
    secondary_matches = []
    secondary_count = 0
    for sk in secondary_skills:
        if sk not in primary_skills:
            cnt = count_skill_occurrences(full_text, sk)
            if cnt > 0:
                secondary_matches.append(f"{sk} ({cnt}x)")
                secondary_count += cnt

    # 5. Must also mention terms
    must_mention = profile.get("must_also_mention", [])
    for term in must_mention:
        if term.strip() and count_skill_occurrences(full_text, term.strip()) < 1:
            return False, {"reason": f"Required term '{term}' not found"}

    # 6. Experience requirement cap
    max_exp = profile.get("max_years_experience", 10)
    parsed_exp = parse_min_experience(full_text)
    if parsed_exp is not None and parsed_exp > max_exp:
        return False, {"reason": f"Requires {parsed_exp} yrs experience (max cap is {max_exp})"}

    # 7. Location check
    allowed_locs = profile.get("locations_allow", DEFAULT_PROFILE["locations_allow"])
    denied_locs = profile.get("locations_deny", DEFAULT_PROFILE["locations_deny"])
    loc_ok, loc_reason = check_location(loc, desc, allowed_locs, denied_locs)
    if not loc_ok:
        return False, {"reason": loc_reason}

    # 8. Visa sponsorship check
    sponsorship_positive = False
    if profile.get("require_visa_sponsorship", True):
        rejected, sponsorship_positive, sp_reason = check_sponsorship_status(company, full_text, title)
        if rejected:
            return False, {"reason": sp_reason}
    else:
        _, sponsorship_positive, _ = check_sponsorship_status(company, full_text, title)

    # Score calculation for sorting best match
    is_favorite = any(fav.strip().lower() in company.lower() for fav in profile.get("favorite_companies", []))
    score = (max_count * 10) + (len(matched_skills) * 8) + (secondary_count * 4) + (25 if sponsorship_positive else 0) + (50 if is_favorite else 0)

    all_matched = matched_skills + secondary_matches
    skill_display = ", ".join(all_matched[:4]) if all_matched else f"{total_skill_count}x"

    details = {
        "score": score,
        "skill_count": total_skill_count,
        "max_skill_count": max_count,
        "matched_skills": all_matched,
        "skill_display": skill_display,
        "parsed_exp": parsed_exp,
        "sponsorship_explicit": sponsorship_positive,
        "is_favorite": is_favorite
    }
    return True, details


def get_data_dir() -> Path:
    """Returns directory path for storing seen jobs and reports (~/.jobfinder or .jobfinder)."""
    try:
        data_dir = Path.home() / ".jobfinder"
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir
    except Exception:
        data_dir = Path(".jobfinder")
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir


def load_seen_jobs(seen_file: Path) -> set:
    """Loads previously seen job IDs from JSON file."""
    if not seen_file.exists():
        return set()
    try:
        with open(seen_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return set(data)
            elif isinstance(data, dict):
                return set(data.get("seen_ids", []))
    except Exception:
        pass
    return set()


def save_seen_jobs(seen_file: Path, seen_ids: set):
    """Saves seen job IDs to JSON file."""
    try:
        with open(seen_file, "w", encoding="utf-8") as f:
            json.dump(sorted(list(seen_ids)), f, indent=2)
    except Exception as e:
        print(f"[!] Warning: Could not save seen jobs: {e}", file=sys.stderr)


def load_profile(profile_path: Path) -> dict:
    """Loads profile JSON configuration with defaults."""
    profile = dict(DEFAULT_PROFILE)
    if profile_path.exists():
        try:
            with open(profile_path, "r", encoding="utf-8") as f:
                user_p = json.load(f)
                profile.update(user_p)
        except Exception as e:
            print(f"[!] Warning reading {profile_path}: {e}. Using defaults.", file=sys.stderr)
    return profile


def generate_html_report(matches: list[dict], profile: dict, output_path: Path):
    """Generates a responsive, interactive standalone GitHub Pages website."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
    primary_skill = profile.get("primary_skill", "All")
    visa_flag = "Enforced" if profile.get("require_visa_sponsorship") else "All allowed"
    max_exp = profile.get("max_years_experience", "Any")
    fav_count = sum(1 for m in matches if m["details"].get("is_favorite"))
    sponsor_count = sum(1 for m in matches if m["details"].get("sponsorship_explicit"))

    # Authentication Configuration
    auth_info = profile.get("auth", {})
    auth_enabled = bool(auth_info.get("enabled", True))
    auth_user = str(auth_info.get("username") or os.environ.get("AUTH_USERNAME") or "ramya").strip()
    auth_pass = str(auth_info.get("password") or os.environ.get("AUTH_PASSWORD") or "jobfinder2025").strip()

    salt = "jobfinder_salt_v1"
    expected_hash = hashlib.sha256(f"{salt}:{auth_user.lower()}:{auth_pass}".encode("utf-8")).hexdigest() if auth_enabled else ""

    rows_html = []
    for idx, item in enumerate(matches, 1):
        job = item["job"]
        details = item["details"]
        
        sponsor_badge = ""
        is_sponsor = bool(details.get("sponsorship_explicit"))
        if is_sponsor:
            sponsor_badge = '<span class="badge badge-sponsor">★ Sponsorship Stated</span>'
        
        fav_badge = ""
        is_fav = bool(details.get("is_favorite"))
        if is_fav:
            fav_badge = '<span class="badge badge-fav">♥ Favorite Company</span>'

        exp_badge = ""
        parsed_exp = details.get("parsed_exp")
        if parsed_exp is not None:
            exp_badge = f'<span class="badge badge-exp">{parsed_exp}y min exp</span>'

        board_badge = f'<span class="badge badge-board">{job.get("board", "").upper()}</span>'

        skill_badges = ""
        matched = details.get("matched_skills", [])
        if matched:
            for sk in matched[:3]:
                skill_badges += f'<span class="badge badge-count">{html.escape(sk)}</span> '
        else:
            skill_badges = f'<span class="badge badge-count">{details.get("skill_count", 0)}x {html.escape(primary_skill)}</span>'

        search_text = f"{job.get('company','')} {job.get('title','')} {job.get('location','')} {' '.join(matched)} {job.get('board','')}".lower()
        is_remote = "remote" in (job.get("location", "") or "").lower()
        is_wa = any(x in (job.get("location", "") or "").lower() for x in ["seattle", "bellevue", "redmond", "wa", "washington"])

        row = f"""
        <tr class="job-row" 
            data-search="{html.escape(search_text)}" 
            data-remote="{'true' if is_remote else 'false'}"
            data-wa="{'true' if is_wa else 'false'}"
            data-sponsor="{'true' if is_sponsor else 'false'}"
            data-fav="{'true' if is_fav else 'false'}"
            data-exp="{parsed_exp if parsed_exp is not None else 0}">
            <td class="col-num">{idx}</td>
            <td class="col-company">
                <div class="company-name">{html.escape(job.get('company', ''))}</div>
                {fav_badge}
            </td>
            <td class="col-title">
                <a href="{html.escape(job.get('url', '#'))}" target="_blank" rel="noopener noreferrer" class="job-link">
                    {html.escape(job.get('title', ''))}
                </a>
                <div class="badges-wrap">
                    {board_badge}
                    {sponsor_badge}
                    {exp_badge}
                    {skill_badges}
                </div>
            </td>
            <td class="col-loc">{html.escape(job.get('location', '') or 'Remote / US')}</td>
            <td class="col-action">
                <a href="{html.escape(job.get('url', '#'))}" target="_blank" rel="noopener noreferrer" class="btn-apply">
                    Apply &rarr;
                </a>
            </td>
        </tr>
        """
        rows_html.append(row)

    if not rows_html:
        table_body = """
        <tr id="empty-state">
            <td colspan="5" style="text-align:center; padding:56px 24px; color:var(--text-muted);">
                <div style="font-size:36px; margin-bottom:12px;">🎉</div>
                <div style="font-size:18px; font-weight:700; color:var(--text-main);">You're all caught up!</div>
                <div style="font-size:14px; margin-top:6px;">No new matching jobs were posted since your last run. Check back tomorrow morning.</div>
            </td>
        </tr>
        """
    else:
        table_body = "\n".join(rows_html)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JobFinder &bull; Daily Tech Job Digest</title>
    <meta name="description" content="Automated daily tech job matches from 165+ ATS job boards.">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #f8fafc;
            --surface: #ffffff;
            --surface-hover: #f1f5f9;
            --border: #e2e8f0;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --primary: #2563eb;
            --primary-hover: #1d4ed8;
            --badge-bg: #eff6ff;
            --badge-text: #1e40af;
            --badge-sponsor-bg: #ecfdf5;
            --badge-sponsor-text: #047857;
            --badge-fav-bg: #fdf2f8;
            --badge-fav-text: #be185d;
            --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
            --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.07), 0 2px 4px -2px rgb(0 0 0 / 0.07);
        }}

        [data-theme="dark"] {{
            --bg: #0b0f17;
            --surface: #131b2e;
            --surface-hover: #1c2742;
            --border: #23304e;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --primary: #3b82f6;
            --primary-hover: #60a5fa;
            --badge-bg: #1e293b;
            --badge-text: #93c5fd;
            --badge-sponsor-bg: #064e3b;
            --badge-sponsor-text: #a7f3d0;
            --badge-fav-bg: #831843;
            --badge-fav-text: #fbcfe8;
            --shadow: 0 10px 15px -3px rgb(0 0 0 / 0.4);
        }}

        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: var(--bg);
            color: var(--text-main);
            padding: 24px 16px 48px;
            line-height: 1.5;
            transition: background-color 0.2s, color 0.2s;
        }}

        .container {{
            max-width: 1120px;
            margin: 0 auto;
        }}

        /* Header Navigation */
        .header {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 24px 28px;
            margin-bottom: 20px;
            box-shadow: var(--shadow);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
        }}

        .brand-area {{
            display: flex;
            align-items: center;
            gap: 14px;
        }}

        .brand-icon {{
            width: 44px;
            height: 44px;
            border-radius: 12px;
            background: linear-gradient(135deg, #2563eb, #4f46e5);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #ffffff;
            font-weight: 800;
            font-size: 20px;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        }}

        .title-area h1 {{
            font-size: 20px;
            font-weight: 800;
            letter-spacing: -0.02em;
        }}

        .title-area p {{
            font-size: 12px;
            color: var(--text-muted);
            margin-top: 2px;
        }}

        .header-actions {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .auth-user-badge {{
            display: none;
            align-items: center;
            gap: 8px;
            background: var(--surface-hover);
            border: 1px solid var(--border);
            padding: 6px 12px;
            border-radius: 10px;
            font-size: 12px;
            font-weight: 600;
            color: var(--text-main);
        }}

        .btn-logout {{
            background: transparent;
            border: 1px solid rgba(239, 68, 68, 0.35);
            color: #ef4444;
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.15s;
        }}

        .btn-logout:hover {{
            background: #ef4444;
            color: #ffffff;
        }}

        .btn-toggle-theme {{
            background: var(--surface-hover);
            border: 1px solid var(--border);
            color: var(--text-main);
            padding: 8px 14px;
            border-radius: 10px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: background 0.15s;
        }}
        .btn-toggle-theme:hover {{
            background: var(--border);
        }}

        /* Stats & Filter Bar */
        .controls-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 18px 22px;
            margin-bottom: 20px;
            box-shadow: var(--shadow-sm);
            display: flex;
            flex-direction: column;
            gap: 14px;
        }}

        .search-row {{
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }}

        .search-box {{
            flex: 1;
            min-width: 260px;
            position: relative;
        }}

        .search-box input {{
            width: 100%;
            padding: 10px 14px 10px 38px;
            border-radius: 10px;
            border: 1px solid var(--border);
            background: var(--surface-hover);
            color: var(--text-main);
            font-size: 14px;
            font-family: inherit;
            outline: none;
            transition: border 0.15s, box-shadow 0.15s;
        }}
        .search-box input:focus {{
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
            background: var(--surface);
        }}

        .search-icon {{
            position: absolute;
            left: 12px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-muted);
            font-size: 14px;
        }}

        .filter-pills {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            align-items: center;
        }}

        .filter-btn {{
            background: var(--surface-hover);
            border: 1px solid var(--border);
            color: var(--text-muted);
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s;
        }}
        .filter-btn:hover {{
            color: var(--text-main);
            border-color: var(--text-muted);
        }}
        .filter-btn.active {{
            background: var(--primary);
            color: #ffffff;
            border-color: var(--primary);
        }}

        .stats-summary {{
            font-size: 13px;
            color: var(--text-muted);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding-top: 10px;
            border-top: 1px solid var(--border);
        }}

        /* Table Card */
        .card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 16px;
            overflow: hidden;
            box-shadow: var(--shadow);
        }}

        .table-responsive {{
            width: 100%;
            overflow-x: auto;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 14px;
        }}

        th {{
            background: var(--surface-hover);
            padding: 14px 16px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: var(--text-muted);
            border-bottom: 1px solid var(--border);
        }}

        td {{
            padding: 16px;
            border-bottom: 1px solid var(--border);
            vertical-align: middle;
        }}

        tr:last-child td {{
            border-bottom: none;
        }}

        tr.job-row:hover td {{
            background: var(--surface-hover);
        }}

        .col-num {{ width: 44px; color: var(--text-muted); font-size: 12px; font-weight: 600; text-align: center; }}
        .col-company {{ width: 180px; }}
        .company-name {{ font-weight: 700; font-size: 14px; color: var(--text-main); }}
        .col-title {{ min-width: 320px; }}
        .col-loc {{ width: 190px; font-size: 13px; color: var(--text-muted); }}
        .col-action {{ width: 110px; text-align: right; }}

        .job-link {{
            color: var(--text-main);
            text-decoration: none;
            font-weight: 700;
            font-size: 15px;
            display: inline-block;
            margin-bottom: 5px;
            transition: color 0.15s;
        }}
        .job-link:hover {{
            color: var(--primary);
        }}

        .badges-wrap {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-top: 4px;
        }}

        .badge {{
            display: inline-flex;
            align-items: center;
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.01em;
        }}
        .badge-board {{ background: var(--surface-hover); color: var(--text-muted); border: 1px solid var(--border); }}
        .badge-sponsor {{ background: var(--badge-sponsor-bg); color: var(--badge-sponsor-text); }}
        .badge-fav {{ background: var(--badge-fav-bg); color: var(--badge-fav-text); font-size: 10px; }}
        .badge-exp {{ background: var(--surface-hover); color: var(--text-muted); border: 1px solid var(--border); }}
        .badge-count {{ background: var(--badge-bg); color: var(--badge-text); }}

        .btn-apply {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            background: var(--primary);
            color: #ffffff;
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 700;
            white-space: nowrap;
            transition: background 0.15s, transform 0.1s;
        }}
        .btn-apply:hover {{
            background: var(--primary-hover);
            transform: translateY(-1px);
        }}

        /* Authentication Gate Overlay */
        #auth-overlay {{
            display: {'flex' if auth_enabled else 'none'};
            position: fixed;
            inset: 0;
            background: rgba(11, 15, 23, 0.88);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            z-index: 99999;
            align-items: center;
            justify-content: center;
            padding: 20px;
            animation: authFadeIn 0.2s ease-out;
        }}

        @keyframes authFadeIn {{
            from {{ opacity: 0; transform: scale(0.98); }}
            to {{ opacity: 1; transform: scale(1); }}
        }}

        .auth-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 36px 32px;
            max-width: 400px;
            width: 100%;
            text-align: center;
            box-shadow: var(--shadow);
            position: relative;
        }}

        .auth-icon-wrap {{
            width: 54px;
            height: 54px;
            border-radius: 16px;
            background: linear-gradient(135deg, #2563eb, #4f46e5);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #ffffff;
            font-size: 24px;
            margin: 0 auto 16px;
            box-shadow: 0 8px 16px rgba(37, 99, 235, 0.25);
        }}

        .auth-card h2 {{
            font-size: 20px;
            font-weight: 800;
            letter-spacing: -0.02em;
            color: var(--text-main);
            margin-bottom: 6px;
        }}

        .auth-card p.auth-sub {{
            font-size: 13px;
            color: var(--text-muted);
            margin-bottom: 20px;
            line-height: 1.4;
        }}

        .auth-form {{
            text-align: left;
            display: flex;
            flex-direction: column;
            gap: 14px;
        }}

        .auth-field label {{
            display: block;
            font-size: 12px;
            font-weight: 700;
            color: var(--text-main);
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}

        .auth-input-wrap {{
            position: relative;
            display: flex;
            align-items: center;
        }}

        .auth-input {{
            width: 100%;
            padding: 11px 14px;
            border-radius: 10px;
            border: 1px solid var(--border);
            background: var(--surface-hover);
            color: var(--text-main);
            font-size: 14px;
            font-family: inherit;
            outline: none;
            transition: all 0.15s ease;
        }}

        .auth-input:focus {{
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.18);
            background: var(--surface);
        }}

        .auth-toggle-btn {{
            position: absolute;
            right: 10px;
            background: none;
            border: none;
            cursor: pointer;
            color: var(--text-muted);
            font-size: 16px;
            padding: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            user-select: none;
        }}

        .auth-remember-wrap {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
            color: var(--text-muted);
            cursor: pointer;
            user-select: none;
            margin-top: 2px;
        }}

        .auth-remember-wrap input[type="checkbox"] {{
            accent-color: var(--primary);
            width: 16px;
            height: 16px;
            cursor: pointer;
        }}

        .auth-submit-btn {{
            width: 100%;
            padding: 12px;
            border-radius: 10px;
            background: linear-gradient(135deg, #2563eb, #1d4ed8);
            color: #ffffff;
            font-weight: 700;
            font-size: 14px;
            border: none;
            cursor: pointer;
            margin-top: 6px;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
            transition: all 0.15s ease;
        }}

        .auth-submit-btn:hover {{
            background: linear-gradient(135deg, #1d4ed8, #1e40af);
            transform: translateY(-1px);
            box-shadow: 0 6px 16px rgba(37, 99, 235, 0.35);
        }}

        .auth-error-msg {{
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.3);
            color: #ef4444;
            border-radius: 10px;
            padding: 9px 12px;
            font-size: 12px;
            font-weight: 600;
            display: none;
            text-align: center;
        }}

        .footer-note {{
            margin-top: 28px;
            font-size: 12px;
            color: var(--text-muted);
            line-height: 1.6;
            text-align: center;
        }}
    </style>
</head>
<body>
    <!-- Authentication Overlay -->
    <div id="auth-overlay" style="display: {'flex' if auth_enabled else 'none'};">
        <div class="auth-card">
            <div class="auth-icon-wrap">🔒</div>
            <h2>JobFinder &bull; Private Access</h2>
            <p class="auth-sub">Enter your credentials to unlock your daily matches</p>

            <div id="auth-error" class="auth-error-msg">Invalid username or password. Please try again.</div>

            <div class="auth-form">
                <div class="auth-field">
                    <label for="auth-user">Username</label>
                    <div class="auth-input-wrap">
                        <input type="text" id="auth-user" class="auth-input" placeholder="Enter username..." autocomplete="username" />
                    </div>
                </div>

                <div class="auth-field">
                    <label for="auth-pass">Password</label>
                    <div class="auth-input-wrap">
                        <input type="password" id="auth-pass" class="auth-input" placeholder="Enter password..." autocomplete="current-password" />
                        <button type="button" class="auth-toggle-btn" id="toggle-pass-btn" onclick="togglePassVisibility()" title="Toggle password visibility">👁️</button>
                    </div>
                </div>

                <label class="auth-remember-wrap">
                    <input type="checkbox" id="auth-remember" checked />
                    <span>Remember me on this device</span>
                </label>

                <button type="button" class="auth-submit-btn" id="auth-submit-btn" onclick="attemptLogin()">
                    Sign In & Unlock Dashboard
                </button>
            </div>
        </div>
    </div>

    <div class="container" id="main-content" style="display: {'none' if auth_enabled else 'block'};">
        <!-- Header -->
        <header class="header">
            <div class="brand-area">
                <div class="brand-icon">&lt;/&gt;</div>
                <div class="title-area">
                    <h1>JobFinder &bull; Daily Digest</h1>
                    <p>Updated: {timestamp} &bull; 165+ ATS Boards Scanned</p>
                </div>
            </div>
            <div class="header-actions">
                <div id="auth-badge" class="auth-user-badge">
                    <span>👤 <span id="logged-in-user">{html.escape(auth_user)}</span></span>
                    <button class="btn-logout" onclick="handleLogout()">Logout</button>
                </div>
                <button class="btn-toggle-theme" onclick="toggleTheme()">
                    <span id="theme-icon">🌙</span> <span id="theme-text">Theme</span>
                </button>
            </div>
        </header>

        <!-- Filters & Search -->
        <div class="controls-card">
            <div class="search-row">
                <div class="search-box">
                    <span class="search-icon">🔍</span>
                    <input type="text" id="filter-input" placeholder="Search by role, company, language, framework, or location..." oninput="filterJobs()" />
                </div>
                <div class="filter-pills">
                    <button class="filter-btn active" onclick="setQuickFilter('all', this)">All ({len(matches)})</button>
                    <button class="filter-btn" onclick="setQuickFilter('remote', this)">Remote</button>
                    <button class="filter-btn" onclick="setQuickFilter('wa', this)">Seattle / WA</button>
                    <button class="filter-btn" onclick="setQuickFilter('sponsor', this)">★ Sponsor Stated ({sponsor_count})</button>
                    <button class="filter-btn" onclick="setQuickFilter('fav', this)">♥ Favorites ({fav_count})</button>
                </div>
            </div>
            <div class="stats-summary">
                <span id="match-counter">Showing {len(matches)} matching positions</span>
                <span>Stack: <strong>{html.escape(primary_skill[:45])}</strong></span>
            </div>
        </div>

        <!-- Table -->
        <div class="card">
            <div class="table-responsive">
                <table id="jobs-table">
                    <thead>
                        <tr>
                            <th class="col-num">#</th>
                            <th class="col-company">Company</th>
                            <th class="col-title">Role & Stack Match</th>
                            <th class="col-loc">Location</th>
                            <th class="col-action">Action</th>
                        </tr>
                    </thead>
                    <tbody id="jobs-body">
                        {table_body}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Footer -->
        <footer class="footer-note">
            <p><strong>GitHub Pages Automated Feed:</strong> Scans Greenhouse, Ashby, and Lever public APIs daily without scraping or API keys.</p>
            <p style="margin-top:4px;">Visa filter drops explicit non-sponsorship or clearance demands. Stated sponsorship indicates active H-1B/transfer readiness.</p>
        </footer>
    </div>

    <script>
        const AUTH_CONFIG = {{
            enabled: {"true" if auth_enabled else "false"},
            salt: "{salt}",
            expectedHash: "{expected_hash}",
            username: "{html.escape(auth_user)}"
        }};

        let currentFilter = 'all';

        function filterJobs() {{
            const query = (document.getElementById('filter-input').value || '').toLowerCase().trim();
            const rows = document.querySelectorAll('.job-row');
            let visibleCount = 0;

            rows.forEach(row => {{
                const searchData = row.getAttribute('data-search') || '';
                const isRemote = row.getAttribute('data-remote') === 'true';
                const isWa = row.getAttribute('data-wa') === 'true';
                const isSponsor = row.getAttribute('data-sponsor') === 'true';
                const isFav = row.getAttribute('data-fav') === 'true';

                let matchesFilter = true;
                if (currentFilter === 'remote' && !isRemote) matchesFilter = false;
                if (currentFilter === 'wa' && !isWa) matchesFilter = false;
                if (currentFilter === 'sponsor' && !isSponsor) matchesFilter = false;
                if (currentFilter === 'fav' && !isFav) matchesFilter = false;

                const matchesQuery = !query || searchData.includes(query);

                if (matchesFilter && matchesQuery) {{
                    row.style.display = '';
                    visibleCount++;
                }} else {{
                    row.style.display = 'none';
                }}
            }});

            const counter = document.getElementById('match-counter');
            if (counter) {{
                counter.innerText = `Showing ${{visibleCount}} matching positions`;
            }}
        }}

        function setQuickFilter(type, btn) {{
            currentFilter = type;
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            filterJobs();
        }}

        function toggleTheme() {{
            const current = document.documentElement.getAttribute('data-theme');
            const target = current === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', target);
            localStorage.setItem('jobfinder_theme', target);
            document.getElementById('theme-icon').innerText = target === 'dark' ? '☀️' : '🌙';
        }}

        // Theme init
        if (localStorage.getItem('jobfinder_theme') === 'dark' || (!localStorage.getItem('jobfinder_theme') && window.matchMedia('(prefers-color-scheme: dark)').matches)) {{
            document.documentElement.setAttribute('data-theme', 'dark');
            const icon = document.getElementById('theme-icon');
            if (icon) icon.innerText = '☀️';
        }}

        // --- Client-Side Cryptographic Authentication ---
        function sha256Sync(ascii) {{
            function rightRotate(value, amount) {{ return (value >>> amount) | (value << (32 - amount)); }}
            const mathPow = Math.pow, maxWord = mathPow(2, 32);
            let i, j, result = "";
            const words = [];
            const asciiBitLength = ascii.length * 8;
            let hash = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19];
            const k = [
                0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
                0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
                0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
                0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
                0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
                0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
                0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
                0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
            ];
            ascii += "\x80";
            while (ascii.length % 64 - 56) ascii += "\x00";
            for (i = 0; i < ascii.length; i++) {{
                j = ascii.charCodeAt(i);
                words[i >> 2] |= j << ((3 - i) % 4) * 8;
            }}
            words[words.length] = ((asciiBitLength / maxWord) | 0);
            words[words.length] = (asciiBitLength);
            for (j = 0; j < words.length;) {{
                const w = words.slice(j, j += 16);
                const oldHash = hash;
                hash = hash.slice(0, 8);
                for (i = 0; i < 64; i++) {{
                    const w15 = w[i - 15], w2 = w[i - 2];
                    const a = hash[0], e = hash[4];
                    const temp1 = hash[7]
                        + (rightRotate(e, 6) ^ rightRotate(e, 11) ^ rightRotate(e, 25))
                        + ((e & hash[5]) ^ ((~e) & hash[6]))
                        + k[i]
                        + (w[i] = (i < 16) ? w[i] : (
                            w[i - 16]
                            + (rightRotate(w15, 7) ^ rightRotate(w15, 18) ^ (w15 >>> 3))
                            + w[i - 7]
                            + (rightRotate(w2, 17) ^ rightRotate(w2, 19) ^ (w2 >>> 10))
                        ) | 0
                        );
                    const temp2 = (rightRotate(a, 2) ^ rightRotate(a, 13) ^ rightRotate(a, 22))
                        + ((a & hash[1]) ^ (a & hash[2]) ^ (hash[1] & hash[2]));
                    hash = [(temp1 + temp2) | 0].concat(hash);
                    hash[4] = (hash[4] + temp1) | 0;
                }}
                for (i = 0; i < 8; i++) {{ hash[i] = (hash[i] + oldHash[i]) | 0; }}
            }}
            for (i = 0; i < 8; i++) {{
                for (j = 3; j >= 0; j--) {{
                    const b = (hash[i] >> (8 * j)) & 255;
                    result += (b < 16 ? "0" : "") + b.toString(16);
                }}
            }}
            return result;
        }}

        function computeHash(salt, username, password) {{
            return sha256Sync(salt + ":" + username.toLowerCase() + ":" + password);
        }}

        function attemptLogin() {{
            const userEl = document.getElementById('auth-user');
            const passEl = document.getElementById('auth-pass');
            const errorEl = document.getElementById('auth-error');
            const rememberEl = document.getElementById('auth-remember');

            const user = (userEl ? userEl.value : '').trim();
            const pass = (passEl ? passEl.value : '').trim();

            if (!user || !pass) {{
                if (errorEl) {{
                    errorEl.innerText = "Please enter both username and password.";
                    errorEl.style.display = "block";
                }}
                return;
            }}

            try {{
                const calculatedHash = computeHash(AUTH_CONFIG.salt, user, pass);
                if (calculatedHash === AUTH_CONFIG.expectedHash) {{
                    if (errorEl) errorEl.style.display = 'none';
                    sessionStorage.setItem('jobfinder_auth_token', calculatedHash);
                    sessionStorage.setItem('jobfinder_auth_user', user);
                    if (rememberEl && rememberEl.checked) {{
                        localStorage.setItem('jobfinder_auth_token', calculatedHash);
                        localStorage.setItem('jobfinder_auth_user', user);
                    }} else {{
                        localStorage.removeItem('jobfinder_auth_token');
                        localStorage.removeItem('jobfinder_auth_user');
                    }}
                    showDashboard(user);
                }} else {{
                    if (errorEl) {{
                        errorEl.innerText = "Invalid username or password. Please try again.";
                        errorEl.style.display = "block";
                    }}
                    if (passEl) {{
                        passEl.value = "";
                        passEl.focus();
                    }}
                }}
            }} catch (err) {{
                console.error("Auth error:", err);
                if (errorEl) {{
                    errorEl.innerText = "Authentication error: " + err.message;
                    errorEl.style.display = "block";
                }}
            }}
        }}

        function showDashboard(username) {{
            const overlay = document.getElementById('auth-overlay');
            const mainContent = document.getElementById('main-content');
            const authBadge = document.getElementById('auth-badge');
            const userDisplay = document.getElementById('logged-in-user');

            if (overlay) overlay.style.display = 'none';
            if (mainContent) mainContent.style.display = 'block';
            if (authBadge && AUTH_CONFIG.enabled) authBadge.style.display = 'flex';
            if (userDisplay && username) userDisplay.innerText = username;
        }}

        function handleLogout() {{
            sessionStorage.removeItem('jobfinder_auth_token');
            sessionStorage.removeItem('jobfinder_auth_user');
            localStorage.removeItem('jobfinder_auth_token');
            localStorage.removeItem('jobfinder_auth_user');

            const overlay = document.getElementById('auth-overlay');
            const mainContent = document.getElementById('main-content');
            const authBadge = document.getElementById('auth-badge');
            const passInput = document.getElementById('auth-pass');
            const errorEl = document.getElementById('auth-error');

            if (errorEl) errorEl.style.display = 'none';
            if (passInput) passInput.value = '';
            if (mainContent) mainContent.style.display = 'none';
            if (authBadge) authBadge.style.display = 'none';
            if (overlay) overlay.style.display = 'flex';

            setTimeout(() => {{
                const userEl = document.getElementById('auth-user');
                if (userEl) userEl.focus();
            }}, 100);
        }}

        function togglePassVisibility() {{
            const passInput = document.getElementById('auth-pass');
            const toggleBtn = document.getElementById('toggle-pass-btn');
            if (!passInput) return;
            if (passInput.type === 'password') {{
                passInput.type = 'text';
                if (toggleBtn) toggleBtn.innerText = '🙈';
            }} else {{
                passInput.type = 'password';
                if (toggleBtn) toggleBtn.innerText = '👁️';
            }}
        }}

        function initAuth() {{
            if (!AUTH_CONFIG.enabled) {{
                showDashboard();
                return;
            }}

            const token = sessionStorage.getItem('jobfinder_auth_token') || localStorage.getItem('jobfinder_auth_token');
            const user = sessionStorage.getItem('jobfinder_auth_user') || localStorage.getItem('jobfinder_auth_user') || AUTH_CONFIG.username;

            if (token === AUTH_CONFIG.expectedHash) {{
                showDashboard(user);
            }} else {{
                const overlay = document.getElementById('auth-overlay');
                const mainContent = document.getElementById('main-content');
                if (overlay) overlay.style.display = 'flex';
                if (mainContent) mainContent.style.display = 'none';
                setTimeout(() => {{
                    const userEl = document.getElementById('auth-user');
                    if (userEl && !userEl.value) userEl.focus();
                    else {{
                        const passEl = document.getElementById('auth-pass');
                        if (passEl) passEl.focus();
                    }}
                }}, 100);
            }}

            ['auth-user', 'auth-pass'].forEach(id => {{
                const input = document.getElementById(id);
                if (input) {{
                    input.addEventListener('keydown', function(e) {{
                        if (e.key === 'Enter') {{
                            attemptLogin();
                        }}
                    }});
                }}
            }});
        }}

        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', initAuth);
        }} else {{
            initAuth();
        }}
    </script>
</body>
</html>
"""
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
    except Exception as e:
        print(f"[!] Warning: Could not write HTML report to {output_path}: {e}", file=sys.stderr)


def run_interactive_init(profile_path: Path):
    """Interactive wizard to configure profile.json."""
    print("\n" + "=" * 60)
    print("  JobFinder Profile Setup Wizard")
    print("=" * 60)

    profile = dict(DEFAULT_PROFILE)
    if profile_path.exists():
        try:
            with open(profile_path, "r", encoding="utf-8") as f:
                profile.update(json.load(f))
        except Exception:
            pass

    # 1. Primary skill
    curr_skill = profile.get("primary_skill", "Python")
    val = input(f"\n1. Primary skill / core stack [default: {curr_skill}]: ").strip()
    if val:
        profile["primary_skill"] = val

    # 2. Min skill count
    curr_count = profile.get("min_skill_count", 2)
    val = input(f"   Minimum mentions of skill in description [default: {curr_count}]: ").strip()
    if val.isdigit():
        profile["min_skill_count"] = int(val)

    # 3. Max years experience
    curr_exp = profile.get("max_years_experience", 5)
    val = input(f"\n2. Maximum years of experience required [default: {curr_exp}]: ").strip()
    if val.isdigit():
        profile["max_years_experience"] = int(val)

    # 4. Location preference
    print("\n3. Locations: where do you want to work?")
    val = input("   Enter comma-separated cities or 'remote' (e.g. 'remote, new york, san francisco')\n   [Press Enter for standard US + Remote]: ").strip()
    if val:
        locs = [x.strip() for x in val.split(",") if x.strip()]
        profile["locations_allow"] = locs

    # 5. Visa sponsorship
    curr_visa = "y" if profile.get("require_visa_sponsorship", True) else "n"
    val = input(f"\n4. Do you need visa sponsorship? (drops 'no sponsorship', citizenship, ITAR reqs) [y/n, default: {curr_visa}]: ").strip().lower()
    if val in ["y", "yes", "true"]:
        profile["require_visa_sponsorship"] = True
    elif val in ["n", "no", "false"]:
        profile["require_visa_sponsorship"] = False

    # 6. Favorite companies
    val = input("\n5. Favorite companies to highlight (comma-separated, optional): ").strip()
    if val:
        profile["favorite_companies"] = [x.strip() for x in val.split(",") if x.strip()]

    # 7. Excluded companies
    val = input("   Companies to NEVER show (comma-separated, optional): ").strip()
    if val:
        profile["excluded_companies"] = [x.strip() for x in val.split(",") if x.strip()]

    # Save
    with open(profile_path, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)

    print(f"\n[✓] Successfully saved configuration to {profile_path}")
    print("=" * 60 + "\n")


def install_daily_schedule(script_path: Path):
    """Installs a daily 9:00 AM launchd service (macOS) or crontab entry (Linux)."""
    system_os = platform.system().lower()
    abs_script = script_path.resolve()
    python_bin = sys.executable

    data_dir = get_data_dir()
    cron_log = data_dir / "cron.log"

    print("\n" + "=" * 60)
    print("  Installing Daily Automated 9:00 AM Job Search")
    print("=" * 60)

    if system_os == "darwin":
        # macOS launchd
        launch_dir = Path.home() / "Library" / "LaunchAgents"
        launch_dir.mkdir(parents=True, exist_ok=True)
        plist_path = launch_dir / "com.user.jobfinder.plist"

        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.jobfinder</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python_bin}</string>
        <string>{abs_script}</string>
        <string>--quiet</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>{cron_log}</string>
    <key>StandardErrorPath</key>
    <string>{cron_log}</string>
</dict>
</plist>
"""
        try:
            with open(plist_path, "w", encoding="utf-8") as f:
                f.write(plist_content)
            # Unload if already loaded, then load
            subprocess.run(["launchctl", "unload", str(plist_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            res = subprocess.run(["launchctl", "load", str(plist_path)], capture_output=True, text=True)
            if res.returncode == 0:
                print(f"[✓] macOS LaunchAgent installed and activated: {plist_path}")
                print(f"[✓] Scheduled to run every morning at 9:00 AM.")
                print(f"[✓] Output log: {cron_log}")
            else:
                print(f"[!] Warning loading plist: {res.stderr.strip()}")
        except Exception as e:
            print(f"[!] Error installing macOS plist: {e}")

    else:
        # Linux Crontab
        cron_job_line = f"0 9 * * * {python_bin} {abs_script} --quiet >> {cron_log} 2>&1"
        try:
            # Read existing crontab
            current_cron = ""
            res = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
            if res.returncode == 0:
                current_cron = res.stdout

            if str(abs_script) in current_cron:
                # Replace existing
                lines = [l for l in current_cron.splitlines() if str(abs_script) not in l]
                lines.append(cron_job_line)
                new_cron = "\n".join(lines) + "\n"
            else:
                new_cron = current_cron.strip() + "\n" + cron_job_line + "\n"

            p = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            out, err = p.communicate(input=new_cron)
            if p.returncode == 0:
                print(f"[✓] Linux crontab updated successfully.")
                print(f"[✓] Added cron entry: {cron_job_line}")
                print(f"[✓] Scheduled to run daily at 9:00 AM.")
                print(f"[✓] Output log: {cron_log}")
            else:
                print(f"[!] Error updating crontab: {err.strip()}")
        except Exception as e:
            print(f"[!] Error installing crontab: {e}")

    print("=" * 60 + "\n")


def execute_job_search(profile_path: Path, show_all: bool = False, limit: int | None = None, quiet: bool = False, as_json: bool = False):
    """Executes the full concurrent job fetching and filtering workflow."""
    data_dir = get_data_dir()
    seen_file = data_dir / "seen.json"
    report_file = data_dir / "report.html"
    local_report = Path("report.html")
    docs_report = Path("docs/index.html")

    profile = load_profile(profile_path)
    seen_ids = set() if show_all else load_seen_jobs(seen_file)

    # Combine built-in companies with profile's extra_companies
    all_companies = list(COMPANIES)
    extra = profile.get("extra_companies", [])
    for item in extra:
        if isinstance(item, (list, tuple)) and len(item) == 3:
            all_companies.append((str(item[0]), str(item[1]), str(item[2])))

    if not quiet and not as_json:
        print(f"[*] Scanning {len(all_companies)} company job boards across Greenhouse, Ashby, and Lever...")
        print(f"[*] Matching criteria: Skill='{profile.get('primary_skill')}' (>={profile.get('min_skill_count')}x), MaxExp={profile.get('max_years_experience')}y, VisaFilter={profile.get('require_visa_sponsorship')}")

    fetched_jobs = []
    start_time = time.time()

    # Concurrent fetching with 20 worker threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_company = {
            executor.submit(fetch_board_jobs, name, board, slug): (name, board, slug)
            for name, board, slug in all_companies
        }
        for future in concurrent.futures.as_completed(future_to_company):
            name, board, slug = future_to_company[future]
            try:
                jobs = future.result()
                if jobs:
                    fetched_jobs.extend(jobs)
            except Exception:
                pass

    elapsed = time.time() - start_time
    if not quiet and not as_json:
        print(f"[*] Downloaded {len(fetched_jobs)} total raw postings in {elapsed:.1f}s. Filtering matches...")

    # Filter and score jobs
    company_matches = {}  # company -> list of {job, details}
    newly_seen_count = 0

    for job in fetched_jobs:
        job_id = job.get("id")
        if not show_all and job_id in seen_ids:
            continue

        passed, details = evaluate_job(job, profile)
        if passed:
            comp = job.get("company", "")
            if comp not in company_matches:
                company_matches[comp] = []
            company_matches[comp].append({"job": job, "details": details})

    # Pick top N jobs per company (default 1) to keep digest readable
    max_per_company = profile.get("max_jobs_per_company", 1)
    final_matches = []

    for comp, matches in company_matches.items():
        # Sort by score desc, then by skill_count desc
        matches.sort(key=lambda x: (x["details"]["score"], x["details"]["skill_count"]), reverse=True)
        selected = matches[:max_per_company]
        final_matches.extend(selected)

    # Sort all final matches by score desc
    final_matches.sort(key=lambda x: (x["details"]["score"], x["details"]["skill_count"]), reverse=True)

    if limit and limit > 0:
        final_matches = final_matches[:limit]

    # Mark all found matches as seen
    for item in final_matches:
        seen_ids.add(item["job"]["id"])
    
    if not show_all:
        save_seen_jobs(seen_file, seen_ids)

    # Generate HTML reports
    generate_html_report(final_matches, profile, report_file)
    generate_html_report(final_matches, profile, local_report)
    generate_html_report(final_matches, profile, docs_report)

    if as_json:
        output_data = {
            "timestamp": datetime.now().isoformat(),
            "count": len(final_matches),
            "report_path": str(report_file),
            "local_report_path": str(local_report.resolve()),
            "github_pages_path": str(docs_report.resolve()),
            "profile": profile,
            "jobs": [
                {
                    "id": item["job"]["id"],
                    "company": item["job"]["company"],
                    "title": item["job"]["title"],
                    "url": item["job"]["url"],
                    "location": item["job"]["location"],
                    "board": item["job"]["board"],
                    "score": item["details"]["score"],
                    "skill_count": item["details"]["skill_count"],
                    "matched_skills": item["details"].get("matched_skills", []),
                    "skill_display": item["details"].get("skill_display", ""),
                    "parsed_exp": item["details"]["parsed_exp"],
                    "sponsorship_explicit": item["details"]["sponsorship_explicit"],
                    "is_favorite": item["details"]["is_favorite"]
                }
                for item in final_matches
            ]
        }
        print(json.dumps(output_data, indent=2))
        return

    if quiet:
        return

    # Print clean formatted console summary
    print("\n" + "=" * 80)
    print(f"  JOB DIGEST: {len(final_matches)} NEW MATCHES FOUND")
    print("=" * 80)

    if not final_matches:
        print("  [✓] All caught up! No new postings matching your criteria today.")
    else:
        # Table Header
        print(f"  {'#':<3} {'Company':<20} {'Role':<28} {'Matched Skills':<20} {'Sponsor':<9} {'Location'}")
        print("  " + "-" * 88)
        for i, item in enumerate(final_matches, 1):
            j = item["job"]
            d = item["details"]
            comp = (j["company"][:18] + "..") if len(j["company"]) > 20 else j["company"]
            title = (j["title"][:26] + "..") if len(j["title"]) > 28 else j["title"]
            skills_str = (d.get("skill_display", "")[:18] + "..") if len(d.get("skill_display", "")) > 20 else d.get("skill_display", f"{d['skill_count']}x")
            sponsor_info = "★ Yes" if d["sponsorship_explicit"] else "-"
            loc = (j["location"][:16] + "..") if len(j["location"]) > 18 else (j["location"] or "Remote / US")
            print(f"  {i:<3} {comp:<20} {title:<28} {skills_str:<20} {sponsor_info:<9} {loc}")

    print("=" * 80)
    print(f"[✓] Full interactive HTML report generated at:")
    print(f"    - {report_file}")
    print(f"    - {local_report.resolve()}")
    print(f"    - {docs_report.resolve()} (GitHub Pages ready)")
    print(f"[✓] Seen list updated: {len(seen_ids)} total records in {seen_file}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Daily automated job search engine for 150+ public job boards (Greenhouse, Ashby, Lever)"
    )
    parser.add_argument("--init", action="store_true", help="Interactive setup wizard to configure profile.json")
    parser.add_argument("--all", action="store_true", help="Show all matching jobs, ignoring seen.json cache")
    parser.add_argument("--limit", type=int, default=None, help="Limit maximum number of returned jobs")
    parser.add_argument("--profile", type=str, default="profile.json", help="Path to profile.json (default: profile.json)")
    parser.add_argument("--reset", action="store_true", help="Reset seen jobs database")
    parser.add_argument("--quiet", action="store_true", help="Run silently without console output")
    parser.add_argument("--json", action="store_true", help="Output results as JSON for API integration")
    parser.add_argument("--install-daily", action="store_true", help="Install automated daily 9am schedule (launchd/cron)")
    parser.add_argument("--test-slug", nargs=3, metavar=("NAME", "BOARD", "SLUG"), help="Test a single board (e.g. --test-slug Anthropic greenhouse anthropic)")

    args = parser.parse_args()
    profile_path = Path(args.profile)
    data_dir = get_data_dir()

    if args.reset:
        seen_file = data_dir / "seen.json"
        if seen_file.exists():
            seen_file.unlink()
            print(f"[✓] Seen jobs database reset: {seen_file}")
        else:
            print("[✓] Seen jobs database is already empty.")
        return

    if args.init:
        run_interactive_init(profile_path)
        return

    if args.install_daily:
        install_daily_schedule(Path(__file__))
        return

    if args.test_slug:
        name, board, slug = args.test_slug
        print(f"[*] Testing {board} board for '{name}' with slug '{slug}'...")
        jobs = fetch_board_jobs(name, board, slug)
        print(f"[✓] Successfully retrieved {len(jobs)} active job postings!")
        for j in jobs[:5]:
            print(f"    - {j['title']} ({j['location']}) -> {j['url']}")
        if len(jobs) > 5:
            print(f"    ... and {len(jobs) - 5} more")
        return

    # Standard run
    execute_job_search(
        profile_path=profile_path,
        show_all=args.all,
        limit=args.limit,
        quiet=args.quiet,
        as_json=args.json
    )


if __name__ == "__main__":
    main()
