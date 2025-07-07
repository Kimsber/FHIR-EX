import requests
import json

server_url = "https://hapi.fhir.org/baseR4/"

SearchCode = ""  # 可填入想要搜尋的參數，若為空則搜尋整個Condition
access_token = requests.get(server_url + "Condition" + SearchCode, verify=False)
RequestResult = json.loads(str(access_token.text))
print(RequestResult)
