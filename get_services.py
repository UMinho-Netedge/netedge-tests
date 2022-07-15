import requests
import random
import string

# 200 It is used to indicate nonspecific success. The response body contains a representation of the resource.
def test_check_status_code_equals_200():
    response = requests.get("http://127.0.0.1:8080/mec_service_mgmt/v1/services")
    assert response.status_code == 200

# Check the content type field of a 200 OK
def test_check_content_type_equals_json():
    response = requests.get("http://127.0.0.1:8080/mec_service_mgmt/v1/services")
    assert response.headers["Content-Type"] == "application/json"

# TODO - TEST THE CONTENT OF THE BODY - SHOULD MAKE A SEQUENCE TEST AND CHECK IT
#  (appConfirmReady -> appPostService -> getService)

# 400 - Bad Request. It is used to indicate that incorrect parameters were passed to the request.
def test_check_status_code_equals_400():
    response = requests.get("http://127.0.0.1:8080/mec_service_mgmt/v1/services?teste=teste")
    assert response[".status_code == 400"]

# Check the content type field of a 400
def test_check_content_type_equals_json():
    response = requests.get("http://127.0.0.1:8080/mec_service_mgmt/v1/services?teste=teste")
    assert response.headers["Content-Type"] == "application/problem+json"

# 404 Not Found. It is used when a client provided a URI that cannot be mapped to a valid resource URI.
def test_check_status_code_equals_404():
    response = requests.get("http://127.0.0.1:8080/mec_service_mgmt/v1/servicesxxx")
    assert response[".status_code == 404"]

# 414 - It is used to indicate that the server is refusing to process the request because
# the request URI is longer than the server is willing or able to process.
def test_check_data_status_code_equals_414():
    longstring = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(1000))
    response = requests.get("http://127.0.0.1:8080/mec_service_mgmt/v1/applications/ExampleApp01/services?"
                            f"ser_name={longstring}")
    assert response[".status_code == 404"]

# TODO - CREATE 403 FORBIDDEN TEST - SOMEHOW IT MUST MAKE GET_SERVICES UNAVAILABLE.