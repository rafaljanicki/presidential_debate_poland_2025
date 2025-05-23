import boto3
import config
# import os # No longer used
# import utils # No longer used

bedrock_runtime_client = None

def get_bedrock_runtime_client():
    """Initializes and returns the Bedrock Runtime client."""
    global bedrock_runtime_client
    if bedrock_runtime_client is None:
        try:
            bedrock_runtime_client = boto3.client(
                service_name="bedrock-runtime",
                region_name=config.AWS_REGION
            )
        except Exception as e:
            print(f"Error initializing Bedrock Runtime client: {e}")
            raise
    return bedrock_runtime_client

def generate_candidate_response(model_id: str, system_prompt: str, messages: list, candidate_name: str) -> str:
    """
    Generates a response from a Claude model on Bedrock using the Converse API.

    Args:
        model_id: The ID of the Claude model to use.
        system_prompt: The system prompt defining the AI's role and instructions.
        messages: A list of message objects representing the conversation history.
                  Each message should be a dict like: {"role": "user"/"assistant", "content": [{"text": "..."}]}
        candidate_name: Name of the candidate for logging.

    Returns:
        The text content of the model's response.
    """
    client = get_bedrock_runtime_client()

    if not messages:
        print(f"Warning: Empty messages list for {candidate_name}. This might lead to unexpected behavior.")
        # Provide a default initial message if none exists to avoid errors with the API
        # This scenario ideally should be handled by the calling logic in main.py
        # by ensuring the first turn has a prompt.

    inference_config = {
        "maxTokens": config.MAX_TOKENS_TO_SAMPLE,
        "temperature": config.TEMPERATURE,
        # "topK": config.TOP_K, # Converse API uses a different structure for these
        "topP": config.TOP_P
    }

    # Additional model specific inference parameters for Anthropic Claude models
    # For Claude, top_k and top_p are under `additional_model_request_fields`
    # if needed directly, but Converse API aims to abstract this.
    # For now, we are using the simplified inference_config for Converse.
    # If more granular control is needed, this is where it would go.

    try:
        response_stream = client.converse_stream(
            modelId=model_id,
            messages=messages,
            system=[{"text": system_prompt}],
            inferenceConfig=inference_config
        )

        response_text = ""
        print(f"\n{candidate_name}: ", end="", flush=True)
        for event in response_stream['stream']:
            if 'contentBlockDelta' in event:
                delta = event['contentBlockDelta']['delta']['text']
                print(delta, end="", flush=True)
                response_text += delta
            elif 'metadata' in event:
                # You can capture usage stats here if needed
                # print(f"\nStream metadata: {event['metadata']}")
                pass

        if not response_text.strip():
            print(f"\nWarning: Received empty response stream from Bedrock for {candidate_name}.")
            return "\n(No response generated)"  # Ensure newline after streaming

        print()  # Newline after streaming is complete
        return response_text

    except Exception as e:
        print(f"Error during Bedrock API call for {candidate_name}: {e}")
        # Depending on the error, you might want to raise it or return a specific error message.
        # For a debate, it might be better to indicate an error rather than crash.
        return f"(An error occurred while generating a response: {str(e)})"
