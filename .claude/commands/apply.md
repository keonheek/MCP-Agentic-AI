Read `projects/next-ai-role/README.md` and `context/me.md` and `context/work.md`. The company to apply to is: $ARGUMENTS

Using the writing-agent persona (professional, specific claims, no vague language), draft a cover letter for this company in Korean. Follow these rules:

**Project selection by company type:**
- McKinsey QuantumBlack / BCG Gamma → Lead with FinAgent (data analysis automation + business impact). Frame technical decisions as strategic choices.
- Deloitte Korea AI / Accenture → Lead with FinAgent + SDC grader (demonstrates end-to-end AI implementation for real clients). Emphasize Korean market knowledge.
- Korean enterprise (Samsung SDS, LG CNS, Upstage) → Lead with FinAgent agentic system + DART MCP (demonstrates MCP + Korean enterprise market knowledge). Highlight SKKU connection for Samsung SDS.
- General consulting → Lead with the business outcome, not the tech.

**Format rules:**
- Under 250 words (in Korean)
- Include live URL: keonhee-finagent.streamlit.app
- End with a clear ask (인터뷰 기회 요청)
- Use formal Korean (존댓말) appropriate for a job application
- No vague language — specific project names, specific tech, specific outcomes

**After drafting:**
- Save to `projects/next-ai-role/cover-letter-[company-slug].md`
- Update the Status column in `projects/next-ai-role/README.md` to "Cover letter ready"
