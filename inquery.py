import os
import json
import requests
from bs4 import BeautifulSoup

# File to store persistent data
CONFIG_FILE = "config.json"

# Load configuration from file
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

# Save configuration to file
def save_config(data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Step 1: Get the initial cookies and 'execution' field
def get_execution(session, login_url):
    response = session.get(login_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.find("input", {"name": "execution"})['value']

# Login and retrieve CASTGC cookie
def login(session, url_login, config):
    if "username" in config and "password" in config:
        username = config["username"]
        password = config["password"]
    else:
        username = input("Enter your username: ").strip()
        password = input("Enter your password: ").strip()
        config["username"] = username
        config["password"] = password
        save_config(config)

    execution = get_execution(session, url_login)
    login_data = {
        "username": username,
        "password": password,
        "submit": "登录",
        "type": "username_password",
        "execution": execution,
        "_eventId": "submit"
    }
    response_post = session.post(url_login, data=login_data, allow_redirects=False)
    if "CASTGC" in response_post.cookies:
        return response_post.cookies["CASTGC"]
    print("Login failed.")
    exit()

# Retrieve eai-sess cookie
def get_eai_sess(session, ticket_url):
    response_ticket = session.get(ticket_url, allow_redirects=False)
    if "eai-sess" in session.cookies:
        return session.cookies["eai-sess"]
    print("Failed to retrieve eai-sess cookie.")
    exit()

# POST request to part URL and retrieve UUkey
def get_uukey(session, part_url, areaid, config):
    payload = {"areaid": areaid}
    response_part = session.post(part_url, data=payload, allow_redirects=False)
    if "UUkey" in session.cookies:
        uukey = session.cookies["UUkey"]
        config["areaid"] = areaid
        save_config(config)
        return uukey
    print("Status Code:", response_part.status_code)
    print("Response Content:", response_part.text)
    print(f"Failed to retrieve UUkey cookie for areaid {areaid}.")
    exit()
def access_target_url(session, target_url):
    # Send a GET request to the target URL using the session
    print(f"Accessing target URL: {target_url}")
    response = session.get(target_url)
    
    # Check if the response is successful
    if response.status_code == 200:
        # print("Step 4: Successfully accessed the target URL.")
        # print("Response Content:", response.text[:500])  # Display a snippet of the content
        return response.text  # Return the response content for further processing
    else:
        print("Step 4: Failed to access the target URL.")
        print("Status Code:", response.status_code)
        print("Response Content:", response.text)
        exit()
# Let the user select or load areaid
def select_areaid(config):
    if "areaid" in config:
        print(f"Using stored areaid: {config['areaid']}")
        return config["areaid"]
    print("Select Campus:")
    print("1: Area 1")
    print("2: Area 2")
    choice = input("Enter your choice (1 or 2): ").strip()
    return 1 if choice != "2" else 2

# Generic POST function for department, floor, and dormitory selection
def post_and_select(session, url, payload, key, config, step_name):
    if key in config:
        print(f"Using stored {key}: {config[key]}")
        return config[key]
    response = session.post(url, data=payload, allow_redirects=False)
    data = response.json()
    options = data["d"]["data"]
    print(f"Select {step_name}:")
    for idx, option in enumerate(options, start=1):
        print(f"{idx}: {option[f'{step_name}Name']} (ID: {option[f'{step_name}Id']})")
    choice = int(input("Enter your choice: ").strip()) - 1
    selected_id = options[choice][f"{step_name}Id"]
    config[key] = selected_id
    save_config(config)
    return selected_id
def post_and_select_drom(session, url, payload, key, config, step_name):
    if key in config:
        print(f"Using stored {key}: {config[key]}")
        return config[key]
    response = session.post(url, data=payload, allow_redirects=False)
    data = response.json()
    options = data["d"]["data"]
    print(f"Select {step_name}:")
    for idx, option in enumerate(options, start=1):
        print(f"{idx}: {option[f'{step_name}Name']} (ID: {option[f'dromNum']})")
    choice = int(input("Enter your choice: ").strip()) - 1
    selected_id = options[choice][f"dromNum"]
    config["dromNum"] = selected_id
    save_config(config)
    return selected_id
# Main script execution
def main():
    url_login = "https://auth.bupt.edu.cn/authserver/login?noAutoRedirect=1&service=https%3A%2F%2Fapp.bupt.edu.cn%2Fa_bupt%2Fapi%2Fsso%2Fcas%3Fredirect%3Dhttps%253A%252F%252Fapp.bupt.edu.cn%252Fbuptdf%252Fwap%252Fdefault%252Fchong%26from%3Dwap"
    ticket_url = "https://app.bupt.edu.cn/a_bupt/api/sso/cas?redirect=https%3A%2F%2Fapp.bupt.edu.cn%2Fbuptdf%2Fwap%2Fdefault%2Fchong&from=wap&ticket={}"
    target_url = "https://app.bupt.edu.cn/buptdf/wap/default/chong"
    part_url = "https://app.bupt.edu.cn/buptdf/wap/default/part"
    floor_url = "https://app.bupt.edu.cn/buptdf/wap/default/floor"
    drom_url = "https://app.bupt.edu.cn/buptdf/wap/default/drom"
    bed_url = "https://app.bupt.edu.cn/buptdf/wap/default/search"

    session = requests.Session()
    config = load_config()

    castgc = login(session, url_login, config)
    eai_sess = get_eai_sess(session, ticket_url.format(castgc))
    chong=access_target_url(session, target_url)
    areaid = select_areaid(config)
    uukey = get_uukey(session, part_url, areaid, config)
    
    partment_id = post_and_select(session, part_url, {"areaid": areaid}, "partmentId", config, "partment")
    floor_id = post_and_select(session, floor_url, {"partmentId": partment_id, "areaid": areaid}, "floorId", config, "floor")
    drom_id = post_and_select_drom(session, drom_url, {"partmentId": partment_id, "areaid": areaid, "floorId": floor_id}, "dromNum", config, "drom")
    print(f"Selected drom: {drom_id}")
    # Final POST for bed selection
    payload = {
        "partmentId": partment_id,
        "areaid": areaid,
        "floorId": floor_id,
        "dromNumber": drom_id
    }
    print("Payload:", payload)
    response_bed = session.post(bed_url, data=payload, allow_redirects=False)
    if response_bed.status_code == 200:
        print("Successfully retrieved bed information.")
        print("Response Content:", response_bed.text)
        data = response_bed.json()
        surplus = data["d"]["data"]["surplus"]
        free_end = data["d"]["data"]["freeEnd"]
        print(f"Surplus: {surplus}, Free End: {free_end}")
    else:
        print("Failed to retrieve bed information.")

if __name__ == "__main__":
    main()
