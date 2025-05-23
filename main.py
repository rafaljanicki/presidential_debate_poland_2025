import os
import time
from dotenv import load_dotenv
import datetime  # For timestamping filenames

import bedrock_service
import config
import utils

load_dotenv()  # Load environment variables from .env file


def format_conversation_for_bedrock(conversation_history: list, next_speaker_name: str) -> list:
    """
    Formats the conversation history for the Bedrock Converse API.
    The history should alternate between 'user' and 'assistant' roles.
    The last message from the opponent is treated as 'user' for the current speaker.
    """
    messages = []
    for entry in conversation_history:
        # For the current speaker, their previous turns were 'assistant'.
        # Their opponent's turns are 'user'.
        if entry["speaker"] == next_speaker_name:
            role = "assistant"
        else:
            role = "user"
        messages.append({"role": role, "content": [{"text": entry["statement"]}]})
    return messages


def run_debate():
    print("Presidential Debate Simulation Starting...")
    print("-----------------------------------------")
    print(f"Topic: {config.DEBATE_TOPIC}")
    print(f"Max turns per candidate: {config.MAX_TURNS_PER_CANDIDATE}")
    print("-----------------------------------------")

    # Load Personas
    candidate_alpha_persona = utils.load_persona(config.CANDIDATE_ALPHA_PERSONA_FILE)
    candidate_beta_persona = utils.load_persona(config.CANDIDATE_BETA_PERSONA_FILE)

    if not candidate_alpha_persona or not candidate_beta_persona:
        print("Error: Could not load one or both candidate personas. Exiting.")
        return

    # Initialize debate state
    turn_count_alpha = 0
    turn_count_beta = 0
    conversation_history = []  # List of dicts: {"speaker": name, "statement": text}

    # Construct behavioral guidance string
    behavioral_prompt_template = config.BEHAVIORAL_GUIDANCE
    if isinstance(behavioral_prompt_template, tuple):
        behavioral_prompt_template = " ".join(behavioral_prompt_template)
    behavioral_prompt = behavioral_prompt_template.format(max_turns=config.MAX_TURNS_PER_CANDIDATE)

    # System prompts for each candidate
    system_prompt_alpha = f"{candidate_alpha_persona}\n\nDebate Topic: {config.DEBATE_TOPIC}\n\n{behavioral_prompt}"
    system_prompt_beta = f"{candidate_beta_persona}\n\nDebate Topic: {config.DEBATE_TOPIC}\n\n{behavioral_prompt}"

    current_speaker_name = config.CANDIDATE_ALPHA_NAME
    current_system_prompt = system_prompt_alpha
    # opponent_name is not strictly needed for the current logic after refactoring for streaming/linter.
    # If future logic requires knowing the opponent directly in the loop, it can be reinstated.
    # opponent_name = config.CANDIDATE_BETA_NAME

    # Kick off the debate with an initial prompt for the first speaker
    # The first "user" message for Candidate Alpha will be this initial prompt.
    # We add it to history as if a moderator said it, then Alpha responds.

    # Option 1: A neutral initial prompt to get Candidate Alpha to start
    # This will be the first "user" message for Candidate Alpha
    initial_prompt_for_alpha = config.INITIAL_DEBATE_PROMPT + f" {config.CANDIDATE_ALPHA_NAME}, please provide your opening statement."
    # This initial prompt isn't part of the turn count for candidates.
    # It acts as the very first "user" message in the conversation sent to Alpha.

    # For the very first turn, messages for Bedrock will contain only this initial user prompt.
    # After this, the conversation_history will be used.
    bedrock_messages_for_alpha = [{"role": "user", "content": [{"text": initial_prompt_for_alpha}]}]

    print(f"\nMODERATOR: {initial_prompt_for_alpha}")

    while turn_count_alpha < config.MAX_TURNS_PER_CANDIDATE or turn_count_beta < config.MAX_TURNS_PER_CANDIDATE:
        if current_speaker_name == config.CANDIDATE_ALPHA_NAME and turn_count_alpha >= config.MAX_TURNS_PER_CANDIDATE:
            # Alpha is done, switch to Beta if Beta still has turns
            if turn_count_beta < config.MAX_TURNS_PER_CANDIDATE:
                print(f"\n--- {config.CANDIDATE_ALPHA_NAME} has reached max turns. Switching to {config.CANDIDATE_BETA_NAME} --- ")
                current_speaker_name = config.CANDIDATE_BETA_NAME
                current_system_prompt = system_prompt_beta
                # opponent_name = config.CANDIDATE_ALPHA_NAME
            else:
                break  # Both are done
        elif current_speaker_name == config.CANDIDATE_BETA_NAME and turn_count_beta >= config.MAX_TURNS_PER_CANDIDATE:
            # Beta is done, switch to Alpha if Alpha still has turns
            if turn_count_alpha < config.MAX_TURNS_PER_CANDIDATE:
                print(f"\n--- {config.CANDIDATE_BETA_NAME} has reached max turns. Switching to {config.CANDIDATE_ALPHA_NAME} --- ")
                current_speaker_name = config.CANDIDATE_ALPHA_NAME
                current_system_prompt = system_prompt_alpha
                # _ = config.CANDIDATE_BETA_NAME # Assign to underscore to indicate 'opponent_name' is intentionally unused for now
            else:
                break  # Both are done

        print(f"\nTurn for {current_speaker_name} (Turn {turn_count_alpha + 1 if current_speaker_name == config.CANDIDATE_ALPHA_NAME else turn_count_beta + 1}):")

        # For the very first turn of Alpha, we use the specially prepared bedrock_messages_for_alpha
        if not conversation_history and current_speaker_name == config.CANDIDATE_ALPHA_NAME:
            bedrock_api_messages = bedrock_messages_for_alpha
        else:
            # After the first turn, or for Beta's first turn (if Alpha spoke first), format from history
            # If it's Beta's very first turn, conversation_history will contain Alpha's first statement.
            # This statement becomes the "user" message for Beta.
            bedrock_api_messages = format_conversation_for_bedrock(conversation_history, current_speaker_name)
            if not bedrock_api_messages:  # Should not happen if initial prompt was handled
                print(f"Error: No messages to send for {current_speaker_name}. This indicates a logic flaw.")
                # As a fallback, use the initial debate prompt if history is unexpectedly empty
                # This helps avoid an empty messages list to Bedrock if something went wrong with history.
                initial_context = config.INITIAL_DEBATE_PROMPT + f" {current_speaker_name}, it's your turn."
                if conversation_history and conversation_history[-1]["statement"]:
                    initial_context = conversation_history[-1]["statement"]  # Use opponent's last words
                bedrock_api_messages = [{"role": "user", "content": [{"text": initial_context}]}]

        response_text = bedrock_service.generate_candidate_response(
            model_id=os.environ['MODEL_ID'],
            system_prompt=current_system_prompt,
            messages=bedrock_api_messages,
            candidate_name=current_speaker_name
        )

        # The response is now printed by bedrock_service.py as it streams.
        # So, we don't need the line below anymore.
        # print(f"\n{current_speaker_name}: {response_text}")
        conversation_history.append({"speaker": current_speaker_name, "statement": response_text})

        # Check for early conclusion
        if response_text.strip().startswith("I CONCUR AND THE DEBATE CAN CONCLUDE."):
            print(f"\n--- {current_speaker_name} concurs. The debate concludes early. ---")
            break

        if current_speaker_name == config.CANDIDATE_ALPHA_NAME:
            turn_count_alpha += 1
            current_speaker_name = config.CANDIDATE_BETA_NAME
            current_system_prompt = system_prompt_beta
            # _ = config.CANDIDATE_ALPHA_NAME # Assign to underscore
        else:
            turn_count_beta += 1
            current_speaker_name = config.CANDIDATE_ALPHA_NAME
            current_system_prompt = system_prompt_alpha
            # _ = config.CANDIDATE_BETA_NAME # Assign to underscore

        time.sleep(15)  # Small delay to avoid hitting API rate limits too quickly if any

    print("\n-----------------------------------------")
    print("Debate Concluded.")
    print("-----------------------------------------")
    print("\nFull Debate Transcript:")
    transcript_content = []
    for entry in conversation_history:
        line = f"\n{entry['speaker']}: {entry['statement']}"
        print(line)
        transcript_content.append(line.strip())  # Add to list for file saving
    print("-----------------------------------------")

    # Save transcript to file
    if not os.path.exists("debates"):
        os.makedirs("debates")

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    transcript_filename = f"debates/debate_transcript_{timestamp}.txt"

    try:
        with open(transcript_filename, 'w', encoding='utf-8') as f:
            f.write(f"Debate Topic: {config.DEBATE_TOPIC}\n")
            f.write(f"Candidate Alpha: {config.CANDIDATE_ALPHA_NAME}\n")
            f.write(f"Candidate Beta: {config.CANDIDATE_BETA_NAME}\n")
            f.write("-----------------------------------------\n")
            f.write("\n".join(transcript_content))
            f.write("\n-----------------------------------------\n")
        print(f"Transcript saved to: {transcript_filename}")
    except IOError as e:
        print(f"Error saving transcript: {e}")


if __name__ == "__main__":
    run_debate()
