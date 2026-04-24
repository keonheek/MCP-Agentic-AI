# ClickUp System Extract — @nateherk
_Generated: 2026-04-22_
_Source videos: 26_

# ClickUp Extraction from @nateherk Transcripts

---

## 1. System / Workspace Structure

**Workspace mentioned:** "Up at AAI" (referenced when connecting ClickUp via OAuth in managed agents demo)

**Specific areas/lists mentioned:**
- **"Research queue area"** — a dedicated list/space in ClickUp where Nate drops research tasks
- **"To-do" status** — tasks are created and moved to "to-do" status to trigger agent workflows
- **"Complete" status** — agent moves tasks here after processing

**Naming conventions:**
- A list/area called **"research queue"** for the ClickUp research agent workflow
- Tasks created as **"to-dos"** for specific research items (e.g., "a different type of voice AI provider")

**Channels:**
- References a **"ClickUp channel"** where the Field Monitor agent sends weekly signals/summaries

---

## 2. Automations & Workflows

### Workflow 1: ClickUp Research Agent (mentioned twice with detail)
**Trigger → Action pattern:**
1. User creates a new to-do task in the **"research queue"** area in ClickUp
2. User moves task to **"to-do"** status
3. Managed agent picks up the task
4. Agent does research on the topic
5. Agent **leaves a comment** on the task with: summary, key findings, additional information, and sources at the bottom
6. Agent moves task to **"Complete"**

> *"I would basically be able to come into this research queue area in my ClickUp. I would be able to create a new to-do down here for a different type of voice AI provider. And then when I move it to to-do, the manage agent would pick up the task and then it would do research and it would leave me a comment over here."*

**Problem Nate identified:** This workflow requires manual triggering — the agent can't automatically wake up when a task is created. He wanted a ClickUp webhook or scheduled cron to trigger the agent automatically but couldn't do it natively in Anthropic's managed agents.

> *"What I had to do here is I had to come into the agent and say, 'Hey, go check the ClickUp and then see if you've got any to-dos.' and then fulfill them."*

**Workaround he considered:** Schedule the agent to wake up every 30 minutes, check for to-dos, process if found, sleep if not — but managed agents don't support cron scheduling natively.

**Alternative glue solution mentioned:**
> *"I could literally glue it together by having a scheduled trigger in Naden or having a ClickUp trigger in Nen and then just making this shoot off an HTTP request to my managed agent over in Interropus Cloud."*

---

### Workflow 2: Field Monitor → ClickUp Channel
**Trigger → Action pattern:**
1. Agent monitors AI/tech space news weekly
2. Sends a signal/summary to a **ClickUp channel**
3. Output includes: clusters of information with sources

> *"I made one called Field Monitor, which basically it looks at things that are going on in the text space and then sends me a signal in my ClickUp channel... I get all this information from the week. It gives me different clusters of information with all of these having sources and it actually was able to send that to me in my ClickUp."*

**Setup time:** ~2 minutes

---

### Workflow 3: Trading Agent → Daily ClickUp Summary
**Trigger → Action pattern:**
- Trading agent (running on Cloud Code routines/crons) sends **end-of-day summary to ClickUp** every day of the week

> *"It's going to send me every day, every day of the week, an end of day summary to my ClickUp."*

**Previous setup:** Used Telegram for notifications
**Reason for switching:** *"I'm going to get my notifications in ClickUp this time rather than Telegram just cuz I live in ClickUp a lot more."*

---

### Workflow 4: YouTube Transcript → ClickUp Action Items (via Managed Agent CLI)
**Trigger → Action pattern:**
1. Drop a YouTube video transcript into Claude Code
2. Claude sends API call to a managed agent hosted on Anthropic's cloud
3. Managed agent sends a **summary** + **action items** to ClickUp

> *"I'm telling it to use Enthropic CLI to build myself a managed agent. The goal of this would be I can drop in a YouTube video transcript and then I can just have it do things for me in my ClickUp like sending me a summary as well as potentially some action items from that video."*

---

### Workflow 5: Notion-style Task Delegation (referenced as example of managed agents)
**Not Nate's own workflow** — referenced as what Notion built:
> *"Notion has a manage agent setup where teams can delegate work to Claude directly inside of Notion itself. They basically drag over some tasks to a different status and then Claude agent picks it up and processes them."*

---

## 3. Templates

No explicit ClickUp templates with field names are described. However, the **research queue workflow** implies a task structure:
- **Task name:** Topic to research (e.g., "voice AI provider name")
- **Status field:** to-do → Complete
- **Comments field:** Agent drops research output here (summary, key findings, sources)

---

## 4. Integrations

**ClickUp ↔ Anthropic Managed Agents:**
- Connected via **OAuth (SSO login)** inside Anthropic's managed agents console
- Stored in a **credential vault** that can be shared across team members
- Connection type: **MCP server** with OAuth credentials

> *"I created one called test vault. For the sake of the demo, let's say I want to create a new vault in order to store this different ClickUp credential... basically prompted me to do the actual like single sign on and then we should be all set. I'll go ahead and click connect as you can see and then all I have to do is choose which workspace I actually want to connect. So I choose up at AAI."*

**ClickUp ↔ Claude Code (via API):**
- ClickUp API token used directly
- *"I would go up here and go to my settings. And then I scroll down and find ClickUp API. And then I would just copy this token right here."*

**ClickUp ↔ n8n (mentioned as potential glue):**
- Nate mentions using a **ClickUp trigger in n8n** to fire HTTP requests to managed agents as a workaround

**ClickUp ↔ Alpaca/Perplexity (via trading agent):**
- Trading agent reads market data via Perplexity API + Alpaca, then writes EOD summaries to ClickUp

**Tools Nate uses alongside ClickUp:**
| Tool | Purpose |
|------|---------|
| Anthropic Managed Agents | Host agents that interact with ClickUp |
| Claude Code | Build and trigger ClickUp workflows |
| n8n | Potential webhook/trigger bridge to ClickUp |
| Alpaca API | Trading brokerage (output sent to ClickUp) |
| Perplexity API | Research (output sent to ClickUp) |
| Telegram | Previous notification channel (replaced by ClickUp) |

---

## 5. Tips & Best Practices

**Tip 1: Use ClickUp as your notification hub instead of Telegram**
> *"I live in ClickUp a lot more"* — Nate switched his trading agent's daily summaries from Telegram to ClickUp because it's where he already spends time. Reduces context switching.

**Tip 2: ClickUp triggers need external glue for automation**
Nate explicitly flags this as a limitation of managed agents: ClickUp webhooks can't natively trigger Anthropic managed agents. You need n8n, Zapier, or similar middleware to:
- Listen for a ClickUp status change
- Fire an HTTP request to the managed agent's API endpoint

**Tip 3: The "Research Queue" pattern**
Simple but powerful pattern: create a dedicated ClickUp list as an **input queue**, move tasks to a trigger status, let the agent process, have it comment results and move to complete. Essentially turning ClickUp into a human-in-the-loop task management interface for AI agents.

**Tip 4: Don't rely solely on managed agents for ClickUp automation**
Nate's honest take:
> *"Why can't we just have a ClickUp trigger natively there or a scheduled trigger natively there?"*
His recommendation: use trigger.dev or n8n instead if you want reliable ClickUp-triggered automation.

**Tip 5: Credential vaults for team sharing**
When connecting ClickUp in managed agents, store the OAuth credential in a **shared vault** so team members can all access the same ClickUp connection without each person needing to re-authenticate.

**Mistake to avoid:** Building a ClickUp → managed agent workflow and assuming it will be fully automatic. The agent needs to be manually triggered or you need external scheduling (n8n cron, trigger.dev) to make it truly autonomous.

---

## 6. Content Ideas for First Mover AI

### YouTube Shorts

1. **"How to Turn ClickUp Into an AI Research Assistant in 2 Minutes"**
   *(The research queue workflow — create task → agent researches → leaves comment → marks complete)*

2. **"Why Your AI Agent Can't React to ClickUp Automatically (And the Fix)"**
   *(Nate's frustration about missing native ClickUp triggers in managed agents — real pain point)*

3. **"I Replaced Telegram Notifications With ClickUp for My AI Trading Bot"**
   *(Quick POV on using ClickUp as a notification hub vs. Telegram)*

4. **"Connect ClickUp to Claude in 60 Seconds With OAuth"**
   *(Screen recording of the OAuth connection flow in Anthropic managed agents)*

---

### Long-Form Videos

5. **"Build a ClickUp AI Research Agent That Works While You Sleep"**
   *(Full tutorial: research queue list setup → managed agent or trigger.dev → OAuth connection → task comment output → status automation. Directly replicates Nate's workflow with the gaps filled in)*

6. **"The ClickUp + n8n + Claude Stack That Actually Works (No Code)"**
   *(Solving Nate's exact problem: ClickUp status change → n8n webhook → HTTP call to managed agent → results posted back as comment)*

7. **"I Built a 24/7 AI Agent That Sends Me Daily Briefings in ClickUp"**
   *(Combining the Field Monitor + trading agent concepts: scheduled Claude Code routine → research → ClickUp summary via API)*

8. **"ClickUp as an AI Command Center: The System Top Creators Are Building"**
   *(Higher-level video positioning ClickUp as the human-in-the-loop interface for AI workflows — research queue, field monitor, daily summaries, action items from YouTube transcripts — all in one place)*

9. **"Why I Stopped Using Telegram for AI Notifications (ClickUp Setup Tour)"**
   *(Nate's exact reasoning + walkthrough of where to find ClickUp API key + how to wire it to Claude Code routines)*

10. **"YouTube Transcript → ClickUp Action Items: Full Claude Automation Tutorial"**
    *(The specific workflow Nate mentions building: drop transcript into Claude Code → managed agent → summary + action items posted to ClickUp)*

---

**Frequency note:** ClickUp is mentioned across **3 of the 5 transcripts**, making it clearly a central tool in Nate's personal workflow — not just a passing reference. The research queue pattern and the "I live in ClickUp" quote are the most reusable/quotable moments for content framing.