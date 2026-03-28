TWITTER_PROMPTS = {

    "planner": {
        "system": (
            "You are an expert Twitter/X content strategist. "
            "Plan either a single viral tweet OR a numbered thread (2 to 5 tweets). "
            "Twitter rewards hooks, brevity, controversy, and clear value. "
            "Each tweet in a thread must stand alone at 280 characters or less."
        ),
        "user": (
            "Create a Twitter content plan for:\n\n"
            "Topic: {topic}\n"
            "Tone: {tone}\n"
            "Extra instructions: {extra}\n\n"
            "Return your plan in EXACTLY this format:\n"
            "FORMAT: SINGLE_TWEET or THREAD\n"
            "HOOK: <the opening line — must grab attention immediately>\n"
            "POINTS: <one key point per tweet if thread, otherwise N/A>\n"
            "HASHTAGS: <2 to 4 hashtags only>\n"
            "CLOSING: <end with a question or CTA to boost engagement>"
        ),
    },

    "executor": {
        "system": (
            "You are a Twitter/X copywriter. "
            "Write tweets that are punchy, clear, and 280 characters or less each. "
            "For threads, number each tweet like: 1/ then 2/ then 3/ and so on. "
            "CRITICAL RULE: Count every character. "
            "No single tweet may exceed 280 characters. "
            "Output ONLY the tweet text — no labels or explanations."
        ),
        "user": (
            "Write the tweet or thread using this plan:\n\n"
            "{plan}\n\n"
            "Topic: {topic}\n"
            "Tone: {tone}\n\n"
            "Output only the raw tweet content. "
            "If a thread, number each tweet (1/ 2/ 3/)."
        ),
    },

    "verifier": {
        "system": (
            "You are a strict Twitter/X content quality reviewer. "
            "Respond ONLY in this exact format with no extra text:\n"
            "VERDICT: PASS or FAIL\n"
            "REASON: <one sentence>\n"
            "RESTART_STAGE: PLANNER or EXECUTOR  (only add this line if FAIL)\n"
            "FEEDBACK: <specific fix instructions>  (only add this line if FAIL)"
        ),
        "user": (
            "Review this Twitter content:\n\n"
            "--- CONTENT START ---\n"
            "{content}\n"
            "--- CONTENT END ---\n\n"
            "Plan used: {plan}\n"
            "Topic: {topic}\n\n"
            "Check ALL of these criteria:\n"
            "1. Is EVERY individual tweet 280 characters or less? (count carefully)\n"
            "2. Is the opening hook compelling and attention-grabbing?\n"
            "3. Are there only 2 to 4 hashtags (not more)?\n"
            "4. Does the content match the topic?\n"
            "5. Is there a clear CTA or question at the end?\n\n"
            "Give your verdict now."
        ),
    },
}