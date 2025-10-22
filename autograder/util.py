# dependencies
import json, sys, os

# helper function to send print statements to stderr
def print_stderr(error_msg):
    print(str(error_msg), file=sys.stderr)

# compile json object for sending score and feedback to Coursera
def send_feedback(score, msg):
    # Ensure score is within valid range
    score = max(0.0, min(1.0, float(score)))
    
    post = {'fractionalScore': score, 'feedback': str(msg)}
    # Optional: this goes to container log and is best practice for debugging purpose
    print(json.dumps(post))
    # This is required for actual feedback to be surfaced
    try:
        with open("/shared/feedback.json", "w") as outfile:
            json.dump(post, outfile)
    except FileNotFoundError:
        # Fallback for local testing - create the directory if it doesn't exist
        try:
            os.makedirs("/shared", exist_ok=True)
            with open("/shared/feedback.json", "w") as outfile:
                json.dump(post, outfile)
        except Exception as e:
            print(f"Warning: Could not write feedback file: {e}")
    except Exception as e:
        print(f"Warning: Could not write feedback file: {e}")

# helper function to match part Ids
def match_partId(partId, testCases):
    # Handle None and string "None" cases
    if partId is None or partId == "None":
        partId = "MernNotesApp"  # Default fallback
    
    print_stderr(f"Attempting to match partId: '{partId}'")
    print_stderr(f"Available test case keys: {list(testCases.keys())}")
    
    # First try direct key match (new approach)
    if partId in testCases:
        print_stderr(f"Found direct match for partId: '{partId}'")
        return testCases[partId]
    
    # Fallback to old approach for backward compatibility
    partIds = {}
    for key in testCases:
        if "partId" in testCases[key]:
            partIds[testCases[key]["partId"]] = key
    
    print_stderr(f"Available partIds in test cases: {list(partIds.keys())}")
    
    if partId in partIds:
        print_stderr(f"Found indirect match for partId: '{partId}' -> '{partIds[partId]}'")
        return testCases[partIds[partId]]
    else:
        print_stderr(f"No match found for partId: '{partId}'")
        return None
