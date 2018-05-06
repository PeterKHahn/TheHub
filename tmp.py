import requests

url = 'https://script.google.com/macros/s/AKfycbxSiPEVAQNp-xSKcB470pdu8eofHShJlcR5oq5y7RsNy6dgpJgb/exec'

params = {
    'eventName' : "hello",
    'when' : "there"
}

res = requests.post(url, params=params).text

print(res)
