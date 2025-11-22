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

