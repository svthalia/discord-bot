import requests

def lambda_handler(event, context):
    print("Hello from save data!")

    r = requests.post('https://thalia.nu/api/v1/token-auth/', data=event)
    print(r.json())

    return event
