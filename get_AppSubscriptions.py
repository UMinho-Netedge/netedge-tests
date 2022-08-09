
import requests
import random
import string
import json

with open("Subscription_Example.json", "r") as read_content:
    json_body = json.load(read_content)

# Enable MEC App - Instantiate an App (if not instatiated before) and Change AppStatus to READY:
def test_check_status_equals_204_confirm():
    response = requests.post("http://127.0.0.1:8080/mec_app_support/v1/applications/12321/confirm_ready",
                             json = {"indication":"READY"})
    assert  response.status_code == 204

# POST a subscription - To Guarantee a subscription in db:
def test_check_status_equals_201():
    response = requests.post("http://127.0.0.1:8080/mec_service_mgmt/v1/applications/12321/subscriptions",
                             json = json_body)
    assert response.status_code == 201

# Verify the response body of the POST:
def test_check_content_type_equals_json():
    response = requests.get("http://127.0.0.1:8080/mec_service_mgmt/v1/applications/12321/subscriptions")
    assert response.headers["Content-Type"] == "application/json"

# Test if the GET method is OK. Asserting the HTTP 200 code.
def test_check_status_code_equals_200():
    response = requests.get("http://127.0.0.1:8080/mec_service_mgmt/v1/applications/12321/subscriptions")
    assert response.status_code == 200

# Check the content type field of a 200 OK
def test_check_content_type_equals_json():
    response = requests.get("http://127.0.0.1:8080/mec_service_mgmt/v1/applications/12321/subscriptions")
    assert response.headers["Content-Type"] == "application/json"


# 400 - Bad Request. It is used to indicate that incorrect parameters were passed to the request.
def test_check_status_code_equals_400():
    response = requests.get("http://127.0.0.1:8080/mec_service_mgmt/v1/applications/12321/subscriptions?teste=teste")
    assert response.status_code == 400

# Check the content type field of a 400
def test_check_content_type_equals_json():
    response = requests.get("http://127.0.0.1:8080/mec_service_mgmt/v1/applications/12321/subscriptions?teste=teste")
    assert response.headers["Content-Type"] == "application/problem+json"

# 404 Not Found. It is used when a client provided a URI that cannot be mapped to a valid resource URI.
def test_check_status_code_equals_404():
    response = requests.get("http://127.0.0.1:8080/mec_service_mgmt/v1/applications/12321/subscriptionsxxx")
    assert response.status_code == 404

# STOPPING the MEC App - Change the AppStatus that don't allow the get method
def test_check_status_equals_204_termination():
    response = requests.post("http://127.0.0.1:8080/mec_app_support/v1/applications/12321/confirm_termination",
                             json = {"operationAction":"STOPPING"})
    assert  response.status_code == 204

# 403 - Forbidden. It is used to indicate the AppStatus don't allow this requisition
def test_check_status_code_equals_403():
    response = requests.get("http://127.0.0.1:8080/mec_service_mgmt/v1/applications/12321/subscriptions")
    assert response.status_code == 403
