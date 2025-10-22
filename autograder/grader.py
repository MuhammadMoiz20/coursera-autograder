#!/usr/bin/env python3

# ENTRYPOINT for Dockerfile
# MERN Notes App Autograder for Coursera - Cypress Test Based

# Dependencies
import sys, os, stat, shutil, json, subprocess, time, re, glob
from pathlib import Path

# Import helper functions from util.py
from util import print_stderr, send_feedback

def main(partId):
    print_stderr(f"Starting Cypress-based grader with partId: '{partId}'")
    print_stderr(f"Environment variables: partId={os.environ.get('partId', 'NOT_SET')}")

    # Find the learner's submission  ----------------------------------------------
    # Allow override for local testing
    submission_location = os.environ.get('SHARED_SUBMISSION_PATH', "/shared/submission/")
    
    # Check if submission is in a 'learn' subfolder (common Coursera pattern)
    actual_submission_path = submission_location
    if os.path.exists(os.path.join(submission_location, "learn")):
        actual_submission_path = os.path.join(submission_location, "learn")
        print_stderr("Found submission in 'learn' subfolder")
    
    # Look for React project files
    submission_files = []
    if os.path.exists(actual_submission_path):
        try:
            submission_files = os.listdir(actual_submission_path)
        except PermissionError:
            print_stderr(f"Permission denied accessing {actual_submission_path}")
            send_feedback(0.0, "Permission error accessing submission. Please contact course staff.")
            return
        except Exception as e:
            print_stderr(f"Error listing submission files: {str(e)}")
            send_feedback(0.0, "Error accessing submission files. Please contact course staff.")
            return
    else:
        print_stderr(f"Submission directory does not exist: {actual_submission_path}")
        send_feedback(0.0, "No submission found. Please ensure you have submitted your project.")
        return
    
    print_stderr(f"Found submission files: {submission_files}")
    print_stderr(f"Looking in: {actual_submission_path}")
    
    # Check if we have the required files
    required_files = ['package.json', 'src']
    missing_files = []
    for req_file in required_files:
        if req_file not in submission_files:
            missing_files.append(req_file)
    
    if missing_files:
        send_feedback(0.0, f"Missing required files: {', '.join(missing_files)}. Please ensure you have submitted a complete React project.")
        return

    # Copy submission to grader directory with executable permissions
    grader_dir = os.environ.get('GRADER_DIR', '/grader/submission')
    try:
        if os.path.exists(grader_dir):
            shutil.rmtree(grader_dir)
        shutil.copytree(actual_submission_path, grader_dir)
        print_stderr(f"Successfully copied submission to {grader_dir}")
    except Exception as e:
        print_stderr(f"Error copying submission: {str(e)}")
        send_feedback(0.0, "Error processing submission. Please contact course staff.")
        return
    
    # Run Cypress tests and calculate grade based on test results
    try:
        # Change to submission directory
        os.chdir(grader_dir)
        
        # Install dependencies
        print_stderr("Installing dependencies...")
        try:
            install_result = subprocess.run(['npm', 'install'], 
                                          capture_output=True, text=True, timeout=300)
            if install_result.returncode != 0:
                print_stderr(f"npm install failed: {install_result.stderr}")
                print_stderr(f"npm install stdout: {install_result.stdout}")
                send_feedback(0.0, "Failed to install dependencies. Please check your package.json file and ensure all dependencies are correctly specified.")
                return
            print_stderr("Dependencies installed successfully")
        except subprocess.TimeoutExpired:
            print_stderr("npm install timed out after 5 minutes")
            send_feedback(0.0, "Dependency installation timed out. Please check your package.json for any problematic dependencies.")
            return
        except FileNotFoundError:
            print_stderr("npm command not found")
            send_feedback(0.0, "npm is not available. Please ensure Node.js and npm are properly installed.")
            return
        except Exception as e:
            print_stderr(f"Error during npm install: {str(e)}")
            send_feedback(0.0, f"Error installing dependencies: {str(e)}")
            return
        
        # Run Cypress tests
        print_stderr("Running Cypress tests...")
        test_results = run_cypress_tests()
        
        if test_results is None:
            send_feedback(0.0, "Failed to run Cypress tests. Please contact course staff.")
            return
        
        # Calculate score based on Cypress test results
        total_tests = test_results['total_tests']
        passed_tests = test_results['passed_tests']
        failed_tests = test_results['failed_tests']
        
        if total_tests == 0:
            send_feedback(0.0, "No tests were found or executed. Please ensure your project has Cypress tests configured.")
            return
        
        final_score = passed_tests / total_tests
        
        # Generate detailed feedback
        feedback_parts = []
        if failed_tests == 0:
            feedback_parts.append("🎉 Excellent! You passed all Cypress tests!")
        else:
            feedback_parts.append(f"❌ You passed {passed_tests} out of {total_tests} Cypress tests.")
        
        feedback_parts.append(f"\n📊 Test Summary:")
        feedback_parts.append(f"✅ Passed: {passed_tests}")
        feedback_parts.append(f"❌ Failed: {failed_tests}")
        feedback_parts.append(f"📈 Score: {final_score:.2%}")
        
        if test_results['test_details']:
            feedback_parts.append("\n📋 Detailed Test Results:")
            for test_detail in test_results['test_details']:
                status = "✅" if test_detail['passed'] else "❌"
                feedback_parts.append(f"{status} {test_detail['title']}")
                if not test_detail['passed'] and test_detail.get('error'):
                    feedback_parts.append(f"   Error: {test_detail['error']}")
        
        feedback = "\n".join(feedback_parts)
        send_feedback(final_score, feedback)

    except Exception as e:
        print_stderr(f"Error running tests: {str(e)}")
        send_feedback(0.0, f"Error running tests: {str(e)}")
        return


def run_cypress_tests():
    """Run Cypress tests and return detailed results"""
    try:
        # First, check if Cypress is installed
        cypress_check = subprocess.run(['npx', 'cypress', '--version'], 
                                      capture_output=True, text=True, timeout=30)
        if cypress_check.returncode != 0:
            print_stderr("Cypress not found, installing...")
            install_cypress = subprocess.run(['npm', 'install', '--save-dev', 'cypress'], 
                                            capture_output=True, text=True, timeout=300)
            if install_cypress.returncode != 0:
                print_stderr(f"Failed to install Cypress: {install_cypress.stderr}")
                return None
        
        # Check if cypress.config.js or cypress.config.cjs exists
        cypress_config_files = ['cypress.config.js', 'cypress.config.cjs', 'cypress.json']
        config_file = None
        for config in cypress_config_files:
            if os.path.exists(config):
                config_file = config
                break
        
        if not config_file:
            print_stderr("No Cypress configuration file found")
            return None
        
        print_stderr(f"Found Cypress config: {config_file}")
        
        # Check if cypress directory exists
        if not os.path.exists('cypress'):
            print_stderr("No cypress directory found")
            return None
        
        # Run Cypress tests in headless mode
        print_stderr("Running Cypress tests in headless mode...")
        
        # Try to run the dev server first (non-blocking)
        dev_server_process = None
        server_started = False
        
        try:
            print_stderr("Starting development server...")
            dev_server_process = subprocess.Popen(['npm', 'run', 'dev'], 
                                                 stdout=subprocess.PIPE, 
                                                 stderr=subprocess.PIPE,
                                                 text=True)
            
            # Wait a bit for the server to start
            time.sleep(10)
            
            # Check if server is running
            try:
                server_check = subprocess.run(['curl', '-f', 'http://localhost:5173'], 
                                            capture_output=True, text=True, timeout=5)
                if server_check.returncode == 0:
                    print_stderr("Development server started successfully")
                    server_started = True
                else:
                    print_stderr("Development server failed to start, trying tests anyway")
            except Exception as e:
                print_stderr(f"Could not check server status: {str(e)}, trying tests anyway")
            
        except Exception as e:
            print_stderr(f"Error starting dev server: {str(e)}, trying tests anyway")
            if dev_server_process:
                dev_server_process.terminate()
                dev_server_process = None
        
        # Run Cypress tests
        try:
            cypress_result = subprocess.run(['npx', 'cypress', 'run', '--headless'], 
                                           capture_output=True, text=True, timeout=600)
            
            # Parse Cypress output to extract test results
            test_results = parse_cypress_output(cypress_result.stdout, cypress_result.stderr)
            
            print_stderr(f"Cypress test run completed with return code: {cypress_result.returncode}")
            print_stderr(f"Test results: {test_results}")
            
            return test_results
            
        except subprocess.TimeoutExpired:
            print_stderr("Cypress tests timed out")
            return {'total_tests': 0, 'passed_tests': 0, 'failed_tests': 0, 'test_details': []}
        except Exception as e:
            print_stderr(f"Error running Cypress tests: {str(e)}")
            return None
        finally:
            # Clean up dev server
            if dev_server_process:
                try:
                    dev_server_process.terminate()
                    dev_server_process.wait(timeout=5)
                except:
                    dev_server_process.kill()
    
    except Exception as e:
        print_stderr(f"Error in run_cypress_tests: {str(e)}")
        return None


def parse_cypress_output(stdout, stderr):
    """Parse Cypress test output to extract test results"""
    try:
        # Initialize result structure
        result = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_details': []
        }
        
        # Look for test results in the output
        lines = stdout.split('\n')
        current_suite = None
        
        for line in lines:
            line = line.strip()
            
            # Look for test suite starts
            if 'Running:' in line and '.cy.' in line:
                current_suite = line.split('Running:')[1].strip()
                print_stderr(f"Found test suite: {current_suite}")
            
            # Look for individual test results
            elif line.startswith('✓') or line.startswith('✗'):
                test_name = line[1:].strip()
                passed = line.startswith('✓')
                
                result['total_tests'] += 1
                if passed:
                    result['passed_tests'] += 1
                else:
                    result['failed_tests'] += 1
                
                result['test_details'].append({
                    'title': test_name,
                    'passed': passed,
                    'suite': current_suite or 'Unknown'
                })
                
                print_stderr(f"Test: {test_name} - {'PASSED' if passed else 'FAILED'}")
        
        # If no tests were found in stdout, try to extract from stderr
        if result['total_tests'] == 0:
            stderr_lines = stderr.split('\n')
            for line in stderr_lines:
                line = line.strip()
                if '✓' in line or '✗' in line:
                    # Extract test results from stderr
                    if '✓' in line:
                        result['total_tests'] += 1
                        result['passed_tests'] += 1
                        result['test_details'].append({
                            'title': line.split('✓')[1].strip(),
                            'passed': True,
                            'suite': 'Unknown'
                        })
                    elif '✗' in line:
                        result['total_tests'] += 1
                        result['failed_tests'] += 1
                        result['test_details'].append({
                            'title': line.split('✗')[1].strip(),
                            'passed': False,
                            'suite': 'Unknown'
                        })
        
        # If still no tests found, try alternative parsing
        if result['total_tests'] == 0:
            # Look for summary patterns
            for line in lines:
                if 'passing' in line.lower() and 'failing' in line.lower():
                    # Try to extract numbers
                    import re
                    numbers = re.findall(r'\d+', line)
                    if len(numbers) >= 2:
                        result['passed_tests'] = int(numbers[0])
                        result['failed_tests'] = int(numbers[1])
                        result['total_tests'] = result['passed_tests'] + result['failed_tests']
                        break
        
        print_stderr(f"Parsed test results: {result}")
        return result
        
    except Exception as e:
        print_stderr(f"Error parsing Cypress output: {str(e)}")
        return {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_details': []
        }


if __name__ == '__main__':
    try:
        partid = os.environ.get('partId')
        if not partid:
            print_stderr("partId environment variable not set")
            send_feedback(0.0, "partId not provided. Please contact course staff.")
            sys.exit(1)
        
        print_stderr(f"Starting autograder with partId: '{partid}'")
        main(partid)
        
    except KeyboardInterrupt:
        print_stderr("Grader interrupted by user")
        send_feedback(0.0, "Grader was interrupted. Please try again.")
        sys.exit(1)
    except Exception as e:
        print_stderr(f"Unexpected error in main: {str(e)}")
        import traceback
        traceback.print_exc()
        send_feedback(0.0, "An unexpected error occurred. Please contact course staff.")
        sys.exit(1)
