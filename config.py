AWS_REGION = "us-east-1"  # Example region, change if needed

MAX_TURNS_PER_CANDIDATE = 7
DEBATE_TOPIC = "Czy były minister Zbigniew Ziobro powinien stawić się przed sejmową komisją śledczą ds. Pegasusa?"

CANDIDATE_ALPHA_NAME = "Candidate PiS"
CANDIDATE_ALPHA_PERSONA_FILE = "candidates/candidate_pis_persona.txt"

CANDIDATE_BETA_NAME = "Candidate KO"
CANDIDATE_BETA_PERSONA_FILE = "candidates/candidate_po_persona.txt"

# Configuration for Bedrock Converse API
# Max tokens for the model to generate in its response.
MAX_TOKENS_TO_SAMPLE = 1024
# Temperature controls randomness. Lower for more factual, higher for more creative.
TEMPERATURE = 0.2
# Top-K sampling
TOP_K = 250
# Top-P sampling (nucleus sampling)
TOP_P = 0.999

# Optional: Define a neutral prompt to kick off the debate if desired
# INITIAL_DEBATE_PROMPT = f"The debate on the topic of '{DEBATE_TOPIC}' begins now. Candidate Alpha, please provide your opening statement."
INITIAL_DEBATE_PROMPT = f"The debate on the topic of '{DEBATE_TOPIC}' begins now."

# Rate Limiting for AWS Bedrock
BEDROCK_TPM_LIMIT = 6000  # Tokens Per Minute limit (set conservatively)
# Estimate of tokens used per full turn (one candidate query + response)
ESTIMATED_TOKENS_PER_TURN = 1500

# System prompt additions to guide candidate behavior
BEHAVIORAL_GUIDANCE = (
    "You are participating in a presidential debate. You have a maximum of {max_turns} turns to make your points. "
    "While you should primarily rely on factual information consistent with your persona, you may subtly introduce one or two plausible but misleading or "
    "incorrect statements during the debate. Your opponent may or may not fact-check these statements. You can also choose to challenge "
    "or fact-check your opponent's statements if you suspect inaccuracies, but this is optional. Focus on convincing the other side and "
    "making your case within the turn limit. "
    "IMPORTANT: If you find that you agree with your opponent's main argument on the core debate topic "
    "(as stated in the system prompt), or have been convinced by their points, and believe there is no further "
    "substantial disagreement, you MUST clearly state this. "
    "Begin your response with the exact phrase 'I CONCUR AND THE DEBATE CAN CONCLUDE.' before any other text. "
    "Only use this specific phrase if genuine agreement on the core topic is reached and further debate is unnecessary."
)