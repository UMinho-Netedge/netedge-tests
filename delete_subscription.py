import requests
import random
import string
import json


with open("Subscription_Example.json", "r") as read_content:
    json_body = json.load(read_content)



def test_check_status_equals_204_confirm():
    response = requests.post("http://127.0.0.1:8080/mec_app_support/v1/applications/12321/confirm_ready",
                             json = {"indication":"READY"})
    assert  response.status_code == 204

def test_check_status_equals_201():
    response = requests.post("http://127.0.0.1:8080/mec_service_mgmt/v1/applications/12321/subscriptions",
                             json = json_body)
    assert response.status_code == 201

def test_check_content_type_equals_json():
    response = requests.post("http://127.0.0.1:8080/mec_service_mgmt/v1/applications/12321/subscriptions",
                             json=json_body)
    assert response.headers["Content-Type"] == "application/json"

def test_check_status_204():
    response_ = requests.post("http://127.0.0.1:8080/mec_service_mgmt/v1/applications/12321/subscriptions",
                              json=json_body)

    SubsId = json.loads(response_.text)['_links']['self']['href'].split(sep="subscriptions/")[1]
    
    response = requests.delete("http://127.0.0.1:8080/mec_service_mgmt/v1/applications/12321/subscriptions/"+SubsId)
    assert response.status_code == 204


# 404 Not Found. It is used when a client provided a URI that cannot be mapped to a valid resource URI.
def test_check_status_code_equals_404():
    response = requests.delete("http://127.0.0.1:8080/mec_service_mgmt/v1/applications/12321/subscriptionsxxx")
    assert response.status_code == 404


# 403 - Forbidden. It is used to indicate the AppStatus don't allow this requisition
def test_check_status_code_equals_403():
    response_ = requests.post("http://127.0.0.1:8080/mec_service_mgmt/v1/applications/12321/subscriptions",
                              json=json_body)

    SubsId = json.loads(response_.text)['_links']['self']['href'].split(sep="subscriptions/")[1]

    response_ = requests.post("http://127.0.0.1:8080/mec_app_support/v1/applications/12321/confirm_termination",
                            json={"operationAction": "STOPPING"})

    response = requests.get("http://127.0.0.1:8080/mec_service_mgmt/v1/applications/12321/subscriptions/" + SubsId)
    assert response.status_code == 403