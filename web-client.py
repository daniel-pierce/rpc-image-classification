import requests
import json
import sys

headers = {'Content-Type': 'application/json'}
url = "http://localhost:5000/"
params = len(sys.argv)
for i in range(len(sys.argv)):
    if i == 0:
        r = requests.get(url)
        dataDict = r.json()
        print(dataDict['title'])
        print(dataDict['name'])
        print(dataDict['date'])
    else:
        image = {'image': sys.argv[i]}
        response = requests.post(url, headers=headers, data=json.dumps(image))
        print("\nThe image you've submitted is classified as: " + response.json()['prediction'])
