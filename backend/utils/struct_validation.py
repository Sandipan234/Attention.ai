import json


def complete_json(raw_output: str) -> str:
    """
    Check and complete a JSON string by ensuring matching braces.

    Args:
        raw_output (str): Raw JSON string from the LLM.

    Returns:
        str: Complete JSON string.
    """
    open_braces = raw_output.count("{")
    close_braces = raw_output.count("}")

    # Append missing closing braces
    if open_braces > close_braces:
        raw_output += "}" * (open_braces - close_braces)

    return raw_output

def validate_json(raw_output: str) -> dict:
    """
    Validate and parse JSON from raw LLM output.

    Args:
        raw_output (str): Raw JSON string from the LLM.

    Returns:
        dict: Parsed JSON or an empty default structure.
    """
    try:
        # Ensure JSON is complete
        completed_json = complete_json(raw_output)
        return json.loads(completed_json)
    except json.JSONDecodeError:
        print("Invalid JSON detected. Falling back to defaults.")
        return {
            "preferences": [],
            "budget": "average",
            "location": "null"
        }