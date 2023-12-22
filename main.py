import openai
import json
import requests
import os  
import shutil  
from fastapi import FastAPI  
from pydantic import BaseModel  
from requests.auth import HTTPBasicAuth


app = FastAPI()

class functionPromt(BaseModel):  
    prompt: str  


def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    if "tokyo" in location.lower():
        return json.dumps({"location": "Tokyo", "temperature": "10", "unit": "celsius"})
    elif "san francisco" in location.lower():
        return json.dumps({"location": "San Francisco", "temperature": "72", "unit": "fahrenheit"})
    elif "paris" in location.lower():
        return json.dumps({"location": "Paris", "temperature": "22", "unit": "celsius"})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})

def send_email(to_email, subject):
            # API URL
            url = "https://gray-repulsive-duck.cyclic.app/sendEmail"

            # Headers
            headers = {
                "Content-Type": "application/json",
            }

            # the request body with the provided values
            payload = {
                "to": to_email,
                "subject": subject,
            }

            # Convert the payload to JSON
            json_payload = json.dumps(payload)

            # Send the POST request
            response = requests.post(url, headers=headers, data=json_payload)

            # Check the response status code
            if response.status_code == 200:
                return "Email sent successfully!"
            else:
                # return f"Failed to send email. Status code: {response.status_code}"
 
                return f"Failed to send email. Status code: please provide the write details"

def disk_cleanup(dummy_property):
    # Define the path of the folder to clean up  
    folder_path = '/tmp'  # Change this to your temp directory
    size_threshold = 5000  # Size threshold in bytes

    # Loop through all the files in the folder  
    for filename in os.listdir(folder_path):  
      
        # Create the file path  
        file_path = os.path.join(folder_path, filename)  
      
        # Check if it's a file
        if os.path.isfile(file_path):
            # Get the size of the file in bytes  
            file_size = os.path.getsize(file_path)  
        
            # If the file is larger than size_threshold, delete it  
            if file_size > size_threshold:  
                try:  
                    os.remove(file_path)  
                    print(f"{filename} was deleted.")  
                except Exception as e:  
                    print(f"{filename} could not be deleted. {e}")
        else:
            print(f"{filename} is not a file.")  
    print("Disk cleanup complete.")
    send_email('hemac140@gmail.com',"Disk cleanup completed")
    return "Disk cleanup completed and you have received email shortly"


def service_now_ticket_creation(short_description, description):
        """Create a new ServiceNow ticket"""

        auth = HTTPBasicAuth("adarsh.talinki@wipro.com", "Demo@1234")

        uri = "https://wiprodemo4.service-now.com/api/now/table/incident?sysparm_display_value=true"

        headers = {
            "Accept": "application/json;charset=utf-8",
            "Content-Type": "application/json",
        }

        # define payload for request, note we are passing the sysparm_action variable in the body of the request

        payload = {"short_description": short_description, "description": description}

        try:
            r = requests.post(
                url=uri, data=json.dumps(payload), auth=auth, verify=False, headers=headers
            )
            r.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            return json.dumps({"error": {"message": str(errh)}})
        except requests.exceptions.ConnectionError as errc:
            return json.dumps({"error": {"message": str(errc)}})
        except requests.exceptions.Timeout as errt:
            return json.dumps({"error": {"message": str(errt)}})
        except requests.exceptions.RequestException as err:
            return json.dumps({"error": {"message": str(err)}})

        content = r.json()

        return json.dumps(content)

@app.post("/function_calling")
async def run_conversation(fprompt: functionPromt):
    # Step 1: send the conversation and available functions to the model
    
    client = openai.OpenAI(
        api_key = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", # can be anything
        base_url = "http://localhost:8001/v1" # NOTE: Replace with IP address and port of your llama-cpp-python server
    )

    messages = [{"role": "user", "content": fprompt.prompt}]
    tools = [
        {
            "type": "function",
            "function":{

                    "name": "send_email",
                    "description": "Send mail to the given email",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "to_email": {
                                "type": "string",
                                "description": "The email or gmail,  e.g. balaji@gmail.com, abhijeet@wipro.com",
                            },
                            "subject": {
                                "type": "string",
                                "description": "Subject of the email or gmail, e.g. Can you fix meet today, What is the status of the task",
                            }
                        },
                        "required": ["to_email","subject"],
                    },

            }
        },
         {
            "type":"function",
            "function":{
                    "name": "service_now_ticket_creation",
                    "description": "Create a ServiceNow ticket with the given short description and description",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "short_description": {
                                "type": "string",
                                "description": "A brief summary of the ticket",
                            },
                            "description": {
                                "type": "string",
                                "description": "Detailed information about the ticket",
                            },
                        },
                        "required": ["short_description", "description"],
                    },
                },
        },
       {
         "type":"function",
            "function": {
                    "name": "get_current_weather",
                    "description": "Get the current weather in a given location ask for location if not mentioned",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city and state, e.g. San Francisco, CA, Bangalore",
                            },
                            "unit": {"type": "string", "enum": ["celsius"]},
                        },
                        "required": ["location"],
                    },
                },
       },
       {
        "type":"function",
        "function":{
    "name": "disk_cleanup",
    "description": "Initiates a cleanup process on the system disk to free up space.",
   "parameters": {
            "type": "object",
            "properties": {
                "dummy_property": {
                    "type": "null",
                }
            }
        }
    }

    },
    ]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages,
        tools=tools,
        tool_choice="auto",  # auto is default, but we'll be explicit
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    # Step 2: check if the model wanted to call a function
    if tool_calls:
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "get_current_weather": get_current_weather,
             "send_email": send_email,
             "disk_cleanup":disk_cleanup,
             "service_now_ticket_creation":service_now_ticket_creation
        }  # only one function in this example, but you can have multiple
        messages.append(response_message)  # extend conversation with assistant's reply
        # Step 4: send the info for each function call and function response to the model
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_response = function_to_call(**function_args)
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )  # extend conversation with function response
        second_response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=messages,
        )  # get a new response from the model where it can see the function response
        return second_response


if __name__ == "__main__":  
    uvicorn.run(app, host="0.0.0.0", port=8001)  


# Function Calling
# llama-cpp-python supports structured function calling based on a JSON schema. Function calling is completely compatible with the OpenAI function calling API and can be used by connecting with the official OpenAI Python client.

# You'll first need to download one of the available function calling models in GGUF format:

# functionary-7b-v1
# Then when you run the server you'll need to also specify the functionary chat_format


# python3 -m llama_cpp.server --model <model_path> --chat_format functionary


# Check out this example notebook for a walkthrough of some interesting use cases for function calling.


# Reference
# https://llama-cpp-python.readthedocs.io/en/latest/server/#function-calling


#Model Repo
#curl -L https://huggingface.co/abetlen/functionary-7b-v1-GGUF/resolve/main/functionary-7b-v1.f16.gguf?download=true --output functionary-7b-v1.f16.gguf



# Example dummy function hard coded to return the same weather
# In production, this could be your backend API or an external API