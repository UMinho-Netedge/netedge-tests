import requests
import json
import jsonpath
import pytest
import pprint as pp
import time


TIME_RESET = 5  # same as in app_confirmation_controller.py

baseUrl = "http://127.0.0.1:8080/"
serv_mgmt = baseUrl + "mec_service_mgmt/v1/"
app_supp = baseUrl + "mec_app_support/v1/"
tests = baseUrl + "mec_tests/v1/"

with open("data_model_types/AppTerminationConfirmation.json", "r") as f:
    json_term_conf = json.load(f)

with open("data_model_types/AppReadyConfirmation.json", "r") as f:
    json_ready_conf = json.load(f)

with open("data_model_types/ExampleService_v1.json", "r") as f:
    json_service_v1 = json.load(f)

with open("data_model_types/ExampleService_v2.json", "r") as f:
    json_service_v2 = json.load(f)   


# Already tested:
# * ApplicationConfirmationController.application_confirm_ready
# * ApplicationServicesController.applications_services_post

# Creates apps with the appInstanceId 111 and 222 and two services for each one
@pytest.fixture
def context():
    # Apps 111 and 222 registration with AppReadyConfirmation
    for appInstanceId in [111, 222]:
        #print(f"json_ready_conf type: {type(json_ready_conf)}")
        url = app_supp + "applications/" + str(appInstanceId) + "/confirm_ready"
        requests.post(url, json=json_ready_conf)

        for serName in ['service_1_app_'+str(appInstanceId), 'service_2_app_'+str(appInstanceId)]:
            url = serv_mgmt + "applications/" + str(appInstanceId) + "/services"
            serv_json = json_service_v1.copy()
            serv_json['serName'] = serName
    print('END CONTEXT!')
    
# App doesn't exist in db (appInstanceId = 12321)
def test_409Conflict_v1():
    # App Removal
    path = app_supp + "applications/12321/confirm_termination"
    response = requests.post(path, json=json_term_conf)

    assert response.status_code == 409

    detail = jsonpath.jsonpath(json.loads(response.text), 'detail')
    assert detail[0] == "The application instance resource is not instantiated."

# App exists but not with the given status ("operationAction")
def test_409Conflict_v2(context):
    wrong_status = {"operationAction": "STOPPING"}
    path = app_supp + "applications/111/confirm_termination"
    response = requests.post(path, json=wrong_status)

    print("Response body:")
    pp.pprint(response.text)

    assert response.status_code == 409

    detail = jsonpath.jsonpath(json.loads(response.text), 'detail')
    assert detail[0] == "There is no stopping operation ongoing."



# appStatus['indication'] == operationAction and appStatus['indication'] != operationAction
def test_429TooManyRequests_v1(context):
    # Resetting Time.. 6 seconds
    time.sleep(TIME_RESET+1)

    # change app 111 status to "TERMINATING"
    url = tests + "applications/111/update_status"
    requests.patch(url, json={"operationAction": "TERMINATING"})

    # try confirm_termination with different app status
    wrong_status = {"operationAction": "STOPPING"}
    url = app_supp + "applications/111/confirm_termination"
    response = requests.post(url, json=wrong_status)

    assert response.status_code == 409

    # repeated try with different app status
    wrong_status = {"operationAction": "STOPPING"}
    url = app_supp + "applications/111/confirm_termination"
    response = requests.post(url, json=wrong_status)

    assert response.status_code == 429

    # new try but with the right app status
    wrong_status = {"operationAction": "TERMINATING"}
    url = app_supp + "applications/111/confirm_termination"
    response = requests.post(url, json=wrong_status)

    assert response.status_code == 429

    # Resetting Time.. 6 seconds
    time.sleep(TIME_RESET+1)


# App removal with app and services removal from database confirmation
def test_removal_sucess_with_data_confirmation(context):
    # change app 111 status to "TERMINATING"
    url = tests + "applications/111/update_status"
    requests.patch(url, json={"operationAction": "TERMINATING"})

    # App Removal
    path = app_supp + "applications/111/confirm_termination"
    response = requests.post(path, json=json_term_conf)

    print(f"status_code: {response.status_code}")
    if response.status_code != 204:
        print("Response body:")
        pp.pprint(response.json())

    # [ASSERT] termination conclued with success
    assert response.status_code == 204

    resp = requests.get(serv_mgmt + "applications/111/services")
    json_response = json.loads(resp.text)
    detail = jsonpath.jsonpath(json_response, 'detail')

    # [ASSERT] app removed from database
    assert resp.status_code == 400
    assert detail[0] == "Invalid 'appInstanceId'. Value not found."


def test_400BadRequest_with_wrong_request_body(context):
    # App Removal
    path = app_supp + "applications/111/confirm_termination"
    wrong_json = {"wrong_att": "TERMINATING"}
    response = requests.post(path, json=wrong_json)

    print("Response body:")
    pp.pprint(response.text)

    assert response.status_code == 400

    
# TODO 401 Unauthorized
# TODO 403 Forbidden
