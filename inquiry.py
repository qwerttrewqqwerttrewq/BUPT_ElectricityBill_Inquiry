import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import timedelta
from datetime import datetime
import time

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def get_execution(session, login_url):
    response = session.get(login_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.find("input", {"name": "execution"})['value']

def login(session, url_login, config):
    if "username" in config and "password" in config:
        username = config["username"]
        password = config["password"]
    else:
        username = input("输入学号: ")
        password = input("输入密码: ")
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

def get_eai_sess(session, ticket_url):
    response_ticket = session.get(ticket_url, allow_redirects=False)
    if "eai-sess" in session.cookies:
        return session.cookies["eai-sess"]
    print("Failed to retrieve eai-sess cookie.")
    exit()

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
    print(f"Accessing target URL: {target_url}")
    response = session.get(target_url)
    

    if response.status_code == 200:
        return response.text  
    else:
        print("Step 4: Failed to access the target URL.")
        print("Status Code:", response.status_code)
        print("Response Content:", response.text)
        exit()

def select_areaid(config, nchoice="1"):
    if "areaid" in config:
        print(f"Using stored areaid: {config['areaid']}")
        return config["areaid"]
    choice = nchoice
    return 1 if choice != "2" else 2

def get_options(session, url, payload):
    response = session.post(url, data=payload, allow_redirects=False)
    data = response.json()
    return data["d"]["data"]

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
def send_notification(message,name,isRoom=False):
    newSession = requests.Session()
    payload={
        "to":name,
        "isRoom":True,
        "data":{
        "content":message
    }
    }
    newSession.post("http://localhost:3001/send_msg",data=payload)
def get_notification():
    newSession = requests.Session()
    return 


    
def getEle(config):
    url_login = "https://auth.bupt.edu.cn/authserver/login?noAutoRedirect=1&service=https%3A%2F%2Fapp.bupt.edu.cn%2Fa_bupt%2Fapi%2Fsso%2Fcas%3Fredirect%3Dhttps%253A%252F%252Fapp.bupt.edu.cn%252Fbuptdf%252Fwap%252Fdefault%252Fchong%26from%3Dwap"
    ticket_url = "https://app.bupt.edu.cn/a_bupt/api/sso/cas?redirect=https%3A%2F%2Fapp.bupt.edu.cn%2Fbuptdf%2Fwap%2Fdefault%2Fchong&from=wap&ticket={}"
    target_url = "https://app.bupt.edu.cn/buptdf/wap/default/chong"
    part_url = "https://app.bupt.edu.cn/buptdf/wap/default/part"
    floor_url = "https://app.bupt.edu.cn/buptdf/wap/default/floor"
    drom_url = "https://app.bupt.edu.cn/buptdf/wap/default/drom"
    bed_url = "https://app.bupt.edu.cn/buptdf/wap/default/search"

    session = requests.Session()
    castgc = login(session, url_login, config)
    eai_sess = get_eai_sess(session, ticket_url.format(castgc))
    chong=access_target_url(session, target_url)
    areaid = select_areaid(config)
    uukey = get_uukey(session, part_url, areaid, config)
    tos = "机器人测试"
    #上面这段能跑，但是有时间我再检查一下吧，似乎UUkey那一步是多余的
    
    partment_id = post_and_select(session, part_url, {"areaid": areaid}, "partmentId", config, "partment")
    # floor_ids = get_options(session, floor_url, {"partmentId": partment_id, "areaid": areaid})
    floor_id = post_and_select(session, floor_url, {"partmentId": partment_id, "areaid": areaid}, "floorId", config, "floor")
    # drom_ids = get_options(session, drom_url, {"partmentId": partment_id, "areaid": areaid, "floorId": floor_id})
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
        return {"Surplus": float(surplus), "FreeEnd": float(free_end)}
    else:
        print("Failed to retrieve bed information.")
def main():
    config=load_config()
    toName=''
    timetosleep=60*60*24
    emergemount=10
    emergesleep=60*60
    isRoom=False
    if 'dockerUrl' in config :
        dockerUrl=config['dockerUrl']
    else:
        dockerUrl=input("请输入url,(默认为http://localhost:3001/webhook/msg/v2?token=qweerttrewq):") or 'http://localhost:3001/webhook/msg/v2?token=qweerttrewq'
        config['dockerUrl']=dockerUrl
        save_config(config)
    if 'toName' in config and 'isRoom' in config:
        toName=config['toName']
        isRoom=config['isRoom']
    else:
        toName=input("请输入发送对象:")
        isroom=input("是否是群聊,y/n:")
        isRoom=isroom=='y' or isroom=='Y'
        config['toName']=toName
        config['isRoom']=isRoom
        save_config(config)
    if 'timeToSleep' in config and 'emergeSleep' in config and 'emergeMount' in config:
        timetosleep=config['timeToSleep']
        emergesleep=config['emergeSleep']
        emergemount=config['emergeMount']
    else:
        timetosleep=int(input("请输入间隔查询时间(秒),默认为86400(24小时):") or 86400)
        emergesleep=int(input("请输入紧急查询时间(秒),默认为3600(1小时):") or 3600)
        emergemount=int(input("请输入紧急电量阈值,默认为10度:") or 10)
        config['timeToSleep']=timetosleep
        config['emergeSleep']=emergesleep
        config['emergeMount']=emergemount
        save_config(config)
    messagesession=requests.Session()
    
    previous=0
    change=0
    seconds=0
    power=0
    while True:
        retObj=getEle(config)
        now = datetime.now()
        if 'previous' in config and 'lastTime' in config:
            change=retObj["Surplus"]+retObj["FreeEnd"]-config['previous']
            change = round(change, 2)
            seconds=now-datetime.fromisoformat(config['lastTime'])
            seconds=seconds.total_seconds()
            power=-change*3600000/seconds
            power=round(power,2)
        previous=retObj["Surplus"]+retObj["FreeEnd"]
        config['lastTime']=now.isoformat()
        config['previous']=previous
        save_config(config)
        payload={
            "to":toName,#要发送的对象，可以是群聊或个人。需要设置备注的话请查看官方文档
            "isRoom":isRoom,#设置是否是群聊
            "data":{
            "content": "查询时间："+str(now)+"\n剩余电量：" + str(retObj["Surplus"]) + "度\n剩余赠送电量：" + str(retObj["FreeEnd"])+"度\n与上次查询相比变化："+str(change)+"\n距离上次查询："+str(timedelta(seconds=seconds))+"\n平均功率:"+str(power)+"W"
            }
        }
        
        res=messagesession.post(dockerUrl,json=payload)#设置docker链接
        print("发送结果",res.text)
        if retObj["Surplus"]+retObj["FreeEnd"] <= emergemount:
            timetosleep=emergesleep
        time.sleep(timetosleep)
if __name__ == "__main__":
    main()
