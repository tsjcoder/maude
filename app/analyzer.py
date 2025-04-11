from anthropic import Anthropic, APIError, APITimeoutError
import os
import json
import traceback
import time

# Get API key from environment variable with fallback to a default value
# Set your ANTHROPIC_API_KEY environment variable instead of hardcoding it
API_KEY = os.environ.get("ANTHROPIC_API_KEY_MAUDE", "")

# Check if API key is set
if not API_KEY:
    raise ValueError("Please set the ANTHROPIC_API_KEY_MAUDE environment variable")

print(f">>> Using API key starting with: {API_KEY[:8] if len(API_KEY) > 8 else 'NOT_SET'}")

class MedicalAnalyzer:
    """
    A class that uses the Anthropic Claude API to analyze patient medical data,
    suggest potential diagnoses, and recommend appropriate medications.
    """
    
    def __init__(self):
        """
        Initialize the MedicalAnalyzer with the predefined Anthropic API key.
        """
        print(">>> Initializing Anthropic client")
        self.client = None
        
        # Create client only if we have a valid API key
        if API_KEY != "your_api_key_here" and API_KEY:
            try:
                self.client = Anthropic(api_key=API_KEY)
                print(">>> Anthropic client initialized successfully")
            except Exception as e:
                print(f">>> ERROR initializing Anthropic client: {str(e)}")
                traceback.print_exc()
                # We'll continue without a client and use mock responses
        else:
            print(">>> No valid API key found, will use mock responses")
    
    def analyze_patient_data(self, patient_data):
        """
        Analyze patient data to identify potential diagnoses and recommend medications.
        
        Args:
            patient_data (str): String containing patient medical information
            
        Returns:
            str: JSON string containing diagnoses and medication recommendations
        """
        print(">>> Starting patient data analysis")
        if not patient_data or len(patient_data.strip()) == 0:
            print(">>> ERROR: Empty patient data")
            return json.dumps({
                "error": "Empty patient data provided",
                "diagnoses": [],
                "warnings": ["No patient data was provided for analysis"],
                "disclaimer": "This analysis could not be completed due to missing data."
            })
        
        print(f">>> Patient data length: {len(patient_data)}")
        
        # Check if we have a valid API key and client
        if not self.client or API_KEY == "your_api_key_here" or not API_KEY:
            print(">>> WARNING: No valid API key or client found! Using mock response.")
            # Return a mock response for testing purposes
            return self._generate_mock_response(patient_data)
        
        # Prepare prompt for Claude
        system_prompt = "You are a medical diagnostic assistant that produces structured analysis in JSON format."
        
        user_prompt = f"""
        Based on the following patient data, please identify potential diagnoses and recommend appropriate medications. 
        Include reasoning for each diagnosis and medication.
        
        PATIENT DATA:
        {patient_data}
        
        INSTRUCTIONS:
        1. Analyze the patient's symptoms, history, and any test results
        2. List potential diagnoses in order of likelihood
        3. For each diagnosis, provide recommended medications
        4. Include any warnings, contraindications, or further tests needed
        
        YOUR RESPONSE MUST BE VALID JSON WITH THIS EXACT STRUCTURE:
        {{
            "diagnoses": [
                {{
                    "condition": "Name of condition",
                    "likelihood": "High/Medium/Low",
                    "reasoning": "Reasoning based on patient data",
                    "medications": [
                        {{
                            "name": "Medication name",
                            "dosage": "Recommended dosage",
                            "frequency": "How often to take",
                            "duration": "How long to take",
                            "notes": "Any special instructions"
                        }}
                    ],
                    "additional_tests": ["Test 1", "Test 2"]
                }}
            ],
            "warnings": ["Warning 1", "Warning 2"],
            "disclaimer": "This analysis is not a substitute for professional medical advice."
        }}
        """
        
        # Call the Anthropic API
        try:
            print(f">>> Making API call to Anthropic with key: {API_KEY[:8]}...")
            
            # Add retries for API call robustness
            max_retries = 3
            retry_delay = 2  # seconds
            
            for attempt in range(max_retries):
                try:
                    print(f">>> API call attempt {attempt + 1} of {max_retries}")
                    start_time = time.time()
                    
                    response = self.client.messages.create(
                        model="claude-3-sonnet-20240229",
                        max_tokens=4000,
                        system=system_prompt,
                        messages=[
                            {"role": "user", "content": user_prompt}
                        ]
                    )
                    
                    print(f">>> API call completed in {time.time() - start_time:.2f} seconds")
                    break  # Success - exit retry loop
                    
                except (APIError, APITimeoutError) as api_err:
                    print(f">>> API error on attempt {attempt + 1}: {str(api_err)}")
                    if attempt < max_retries - 1:
                        print(f">>> Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        raise  # Re-raise on last attempt
            
            # Extract the content from the response
            try:
                print(">>> Extracting content from response")
                analysis = response.content[0].text
                print(f">>> Content extracted, length: {len(analysis)}")
                
                # Try to clean up any potential issues with the JSON
                analysis = analysis.strip()
                if analysis.startswith('```json'):
                    print(">>> Detected code block format, cleaning up")
                    analysis = analysis.replace('```json', '', 1)
                    if analysis.endswith('```'):
                        analysis = analysis[:-3]
                    analysis = analysis.strip()
                
                # Validate that the response is valid JSON
                print(">>> Validating JSON format")
                json_data = json.loads(analysis)
                print(">>> JSON validation successful")
                return analysis
                
            except (KeyError, AttributeError) as err:
                print(f">>> Error accessing response content: {str(err)}")
                traceback.print_exc()
                raise Exception(f"Error processing API response: {str(err)}")
            
        except Exception as e:
            print(f">>> ERROR during API call: {str(e)}")
            traceback.print_exc()
            
            # Create a clean error response
            error_response = {
                "error": str(e),
                "diagnoses": [],
                "warnings": ["An error occurred during analysis"],
                "disclaimer": "This system encountered an error and could not complete the analysis."
            }
            
            try:
                return json.dumps(error_response)
            except Exception as json_err:
                print(f">>> ERROR creating error JSON: {str(json_err)}")
                # Last resort fallback
                return json.dumps({
                    "error": "Multiple errors occurred",
                    "diagnoses": [],
                    "warnings": ["Critical system error"],
                    "disclaimer": "System failure"
                })
    
    def _generate_mock_response(self, patient_data):
        """
        Generate a mock response for testing when no valid API key is available.
        
        Args:
            patient_data (str): The patient data that was submitted
            
        Returns:
            str: A JSON string with mock analysis results
        """
        print(">>> Generating mock response for testing")
        
        # Extract some basic data from the patient info to make the mock response somewhat relevant
        patient_data_lower = patient_data.lower()
        has_fever = "fever" in patient_data_lower or "temperature" in patient_data_lower
        has_headache = "headache" in patient_data_lower
        has_cough = "cough" in patient_data_lower
        has_sore_throat = "sore throat" in patient_data_lower or "throat pain" in patient_data_lower
        has_fatigue = "fatigue" in patient_data_lower or "tired" in patient_data_lower
        
        # Build the mock response based on symptoms found
        mock_response = {
            "diagnoses": [],
            "warnings": ["This is a mock response for testing only. No actual medical analysis was performed."],
            "disclaimer": "This analysis is not a substitute for professional medical advice. API key was not provided or invalid."
        }
        
        # Add potential diagnoses based on symptoms
        if has_fever and (has_cough or has_sore_throat):
            mock_response["diagnoses"].append({
                "condition": "Common Cold or Upper Respiratory Infection",
                "likelihood": "High",
                "reasoning": "Patient reports symptoms consistent with viral upper respiratory infection including fever and respiratory symptoms.",
                "medications": [
                    {
                        "name": "Acetaminophen (Tylenol)",
                        "dosage": "500-1000 mg",
                        "frequency": "Every 6 hours as needed",
                        "duration": "Until symptoms resolve",
                        "notes": "For fever and pain relief. Do not exceed 4000 mg per day."
                    },
                    {
                        "name": "Guaifenesin (Mucinex)",
                        "dosage": "400 mg",
                        "frequency": "Every 12 hours as needed",
                        "duration": "Until symptoms resolve",
                        "notes": "To help thin mucus secretions. Drink plenty of fluids."
                    }
                ],
                "additional_tests": ["If symptoms worsen or persist beyond 7 days, consider COVID-19 testing"]
            })
        
        if has_headache and has_fatigue:
            mock_response["diagnoses"].append({
                "condition": "Tension Headache",
                "likelihood": "Medium",
                "reasoning": "Patient reports headache with fatigue, consistent with tension headache possibly due to stress or dehydration.",
                "medications": [
                    {
                        "name": "Ibuprofen (Advil, Motrin)",
                        "dosage": "400-600 mg",
                        "frequency": "Every 6-8 hours as needed",
                        "duration": "Until symptoms resolve",
                        "notes": "Take with food to minimize gastrointestinal side effects."
                    }
                ],
                "additional_tests": ["If headaches are recurrent or worsening, consider neurological evaluation"]
            })
        
        # If no specific symptoms were found, add a generic response
        if len(mock_response["diagnoses"]) == 0:
            mock_response["diagnoses"].append({
                "condition": "Nonspecific Symptoms",
                "likelihood": "Medium",
                "reasoning": "Based on the limited information provided, a specific diagnosis cannot be determined with certainty.",
                "medications": [
                    {
                        "name": "Supportive care",
                        "dosage": "N/A",
                        "frequency": "As needed",
                        "duration": "Until symptoms resolve",
                        "notes": "Rest, hydration, and monitoring of symptoms"
                    }
                ],
                "additional_tests": [
                    "Complete blood count (CBC)",
                    "Basic metabolic panel (BMP)",
                    "Follow up with primary care physician for further evaluation"
                ]
            })
        
        # Add a development mode warning
        mock_response["warnings"].append("Development mode active: Please set a valid Anthropic API key using the ANTHROPIC_API_KEY environment variable.")
        
        return json.dumps(mock_response)