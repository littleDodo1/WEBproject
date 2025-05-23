import requests, urllib3, uuid, os

from dotenv import load_dotenv


load_dotenv()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
def get_access_token():
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    payload = {'scope': 'GIGACHAT_API_PERS'}
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': str(uuid.uuid4()),
        'Authorization': f"Basic {os.getenv('API_AUTH_TOKEN')}"
    }

    response = requests.post(url, headers=headers, data=payload)
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        return None

def ask_gigachat(prompt, access_token):
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    json_data = {
        "model": "GigaChat:latest",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(url, headers=headers, json=json_data)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    return "Oops, нейросеть не смогла найти ответ..."