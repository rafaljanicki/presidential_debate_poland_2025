# Presidential Debate AI

This project simulates a presidential debate between two AI candidates using Amazon Bedrock and Claude 4.

## Setup

1.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure AWS Credentials:**
    Ensure your AWS credentials are configured correctly (e.g., via AWS CLI `aws configure`, or environment variables) with permissions to access Amazon Bedrock.
4.  **Configure Debate Settings:**
    Modify `config.py` to set the AWS region, debate topic, and other parameters.
5. **Configure Model ID**
    Create `.env` file based on the `.env.local` and set your MODEL_ID from AWS

## Running the Debate

```bash
python main.py
```