
import requests
import random
import string
import json

with open("ExampleService_backup.json", "r") as read_content:
    json_body = json.load(read_content)

# 200 It is used to indicate nonspecific success. The response body contains a representation of the resource.
def test_check_status_code_equals_200():
    response = requests.get("http://127.0.0.1:8080/mec_service_mgmt/v1/applications/12321/services")
    assert response.status_code == 200

# Check the content type field of a 200 OK
def test_check_content_type_equals_json():
    response = requests.get("http://127.0.0.1:8080/mec_service_mgmt/v1/applications/12321/services")
    assert response.headers["Content-Type"] == "application/problem+json"

# TODO - TEST THE CONTENT OF THE BODY - SHOULD MAKE A SEQUENCE TEST AND CHECK IT
#  (appConfirmReady -> appPostService -> getService)

def test_check_status_equals_204_confirm():
    response = requests.post("http://127.0.0.1:8080/mec_app_support/v1/applications/12321/confirm_ready",
                             json = {"indication":"READY"})
    assert  response.status_code == 204

def test_check_status_equals_201():
    response = requests.post("http://127.0.0.1:8080/mec_service_mgmt/v1/applications/12321/services",
                             json = json_body)
    assert response.status_code == 201

def test_check_content_type_equals_json():
    response = requests.get("http://127.0.0.1:8080/mec_service_mgmt/v1/applications/12321/services")
    assert response.headers["Content-Type"] == "application/json"

def test_check_status_code_equals_200():
    response = requests.get("http://127.0.0.1:8080/mec_service_mgmt/v1/applications/12321/services")
    assert response.status_code == 200

# Check the content type field of a 200 OK
def test_check_content_type_equals_json():
    response = requests.get("http://127.0.0.1:8080/mec_service_mgmt/v1/applications/12321/services")
    assert response.headers["Content-Type"] == "application/json"


# 400 - Bad Request. It is used to indicate that incorrect parameters were passed to the request.
def test_check_status_code_equals_400():
    response = requests.get("http://127.0.0.1:8080/mec_service_mgmt/v1/applications/12321/services?teste=teste")
    assert response.status_code == 400

# Check the content type field of a 400
def test_check_content_type_equals_json():
    response = requests.get("http://127.0.0.1:8080/mec_service_mgmt/v1/applications/12321/services?teste=teste")
    assert response.headers["Content-Type"] == "application/problem+json"

# 404 Not Found. It is used when a client provided a URI that cannot be mapped to a valid resource URI.
def test_check_status_code_equals_404():
    response = requests.get("http://127.0.0.1:8080/mec_service_mgmt/v1/applications/12321/servicesxxx")
    assert response.status_code == 404

# 414 - It is used to indicate that the server is refusing to process the request because
# the request URI is longer than the server is willing or able to process.
def test_check_data_status_code_equals_414():
    longstring = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(1000000))
    response = requests.get("http://127.0.0.1:8080/mec_service_mgmt/v1/applications/12321/services?"
                            f"ser_name={longstring}")
    assert response.status_code == 414

# TODO - CREATE 403 FORBIDDEN TEST - SOMEHOW IT MUST MAKE GET_SERVICES UNAVAILABLE.
def test_check_status_equals_204_termination():
    response = requests.post("http://127.0.0.1:8080/mec_app_support/v1/applications/12321/confirm_termination",
                             json = {"operationAction":"STOPPING"})
    assert  response.status_code == 204

def test_check_status_code_equals_403():
    response = requests.get("http://127.0.0.1:8080/mec_service_mgmt/v1/applications/12321/services")
    assert response.status_code == 403
