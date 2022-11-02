from urllib import response
from wsgiref import headers
import requests
import json
import pytest
import pprint as pp
import jsonpath as jsp
import time


baseUrl = "http://127.0.0.1:8080/"
serv_mgmt = baseUrl + "mec_service_mgmt/v1/"
app_supp = baseUrl + "mec_app_support/v1/"
tests = baseUrl + "mec_tests/v1/"

with open("data_model_types/AppReadyConfirmation.json", "r") as f:
    json_ready_conf = json.load(f)

with open("data_model_types/DnsRule.json", "r") as f:
    json_dns_rule = json.load(f)

@pytest.fixture
def context():
    # Apps 111 and 222 registration with AppReadyConfirmation
    for appInstanceId in [111, 222]:
        #print(f"json_ready_conf type: {type(json_ready_conf)}")
        url = app_supp + "applications/" + str(appInstanceId) + "/confirm_ready"
        requests.post(url, json=json_ready_conf)
        time.sleep(6)

        url = tests + "applications/" + str(appInstanceId) + "/dns_rules/"
        for dnsRule in ["dns_rule_1_" + str(appInstanceId), 
                        "dns_rule_2_" + str(appInstanceId)]:
            dns_json = json_dns_rule.copy()
            dns_json['dnsRuleId'] = dnsRule
            requests.post(url + dnsRule, json=dns_json)

    print("\n[CONTEXT] Created:                                                 \
           \n* App 111 with DNS rules dns_rule_1_111 and dns_rule_2_111         \
           \n* App 222 with DNS rules dns_rule_1_222 and dns_rule_2_222\n")

    yield

    url = tests + "/applications/remove_all"
    deleted_docs = requests.post(url)
    resp_json = json.loads(deleted_docs.text)
    
    print(f"\n\nRemoved all documents from all collections: {resp_json}")


#########################
# Individual mecDnsRule #
#########################

################################################################################
# PUT

def test_put_dns_rule_200_OK(context):
    appInstanceId = "111"
    dnsRuleId = "dns_rule_1_" + str(appInstanceId)

    url = app_supp + "applications/" + appInstanceId + "/dns_rules/" + dnsRuleId
    response = requests.put(url, json ={"ipAddress": "8.8.8.8",
                                        "ipAddressType": "IP_V6",
                                        "state": "INACTIVE"})
    
    resp_json = json.loads(response.text)
    print('200 OK. Response text:')
    pp.pprint(resp_json)
    
    ipAddress = jsp.jsonpath(resp_json, 'ipAddress')
    ipAddressType = jsp.jsonpath(resp_json, 'ipAddressType')
    state = jsp.jsonpath(resp_json, 'state')
    
    assert response.status_code == 200
    assert ipAddress[0] == "8.8.8.8"
    assert ipAddressType[0] == "IP_V6"
    assert state[0] == "INACTIVE"


def test_put_400_Bad_Request(context):
    appInstanceId = "111"
    dnsRuleId = "dns_rule_1_" + str(appInstanceId)

    url = app_supp + "applications/" + appInstanceId + "/dns_rules/" + dnsRuleId
    
    # Empty request body (JSON)
    response = requests.put(url, json ={})
    assert response.status_code == 400
    detail = jsp.jsonpath(json.loads(response.text), 'detail')
    print("# Empty request body (JSON) [error message]:\n    " + detail[0])

    # Request body (JSON) with unexisting attribute (Json Schema fail)
    response = requests.put(url, json ={"wrong_attribute": "8.8.8.8"})
    assert response.status_code == 400
    detail = jsp.jsonpath(json.loads(response.text), 'detail')
    print("# Request body (JSON) with unexisting attribute (Json Schema fail) [error message]:\n    " 
        + detail[0])

    # Attempt to change dnsRuleId
    response = requests.put(url, json ={"dnsRuleId": "new_dns_rule_id"})
    assert response.status_code == 400
    detail = jsp.jsonpath(json.loads(response.text), 'detail')
    print("# Attempt to change dnsRuleId [error message]:\n    " + detail[0])


def test_put_404_Not_Found(context):
    # Attempt to update DNS rule of a nonexistent app
    appInstanceId = "5555"
    dnsRuleId = "dns_rule_1_111"

    url = app_supp + "applications/" + appInstanceId + "/dns_rules/" + dnsRuleId
    response = requests.put(url, json ={"state": "INACTIVE"})

    assert response.status_code == 404
    detail = jsp.jsonpath(json.loads(response.text), 'detail')
    print("Attempt to update DNS rule of a nonexistent app: " + detail[0])

    # Attempt to update nonexistent DNS rule in a existent app
    appInstanceId = "111"
    dnsRuleId = "dns_rule_1_222"

    url = app_supp + "applications/" + appInstanceId + "/dns_rules/" + dnsRuleId
    response = requests.put(url, json ={"state": "INACTIVE"})

    assert response.status_code == 404
    detail = jsp.jsonpath(json.loads(response.text), 'detail')
    print("Attempt to update DNS rule of a nonexistent rule id (in a existent app): " 
            + detail[0])


def test_put_403_Forbidden(context):
    # change app 222 status to "TERMINATING"
    url = tests + "applications/222/update_status"
    requests.patch(url, json={"operationAction": "TERMINATING"})

    # Attempt to update existent DNS rule from a NOT READY app
    appInstanceId = "222"
    dnsRuleId = "dns_rule_1_222"
    url = app_supp + "applications/" + appInstanceId + "/dns_rules/" + dnsRuleId

    response = requests.put(url, json ={"ipAddressType": "IP_V6"})

    print("\n## Before 403 Forbidden assertion ##\n")

    assert response.status_code == 403
    detail = jsp.jsonpath(json.loads(response.text), 'detail')
    print("Attempt to update a DNS rule of a app without ready status [error msg]: " 
            + detail[0])


def test_put_419_PreConditionFailed(context):
    appInstanceId = "111"
    dnsRuleId = "dns_rule_1_" + str(appInstanceId)
    url = app_supp + "applications/" + appInstanceId + "/dns_rules/" + dnsRuleId
    
    get_response = requests.get(url)
    etag = get_response.headers['ETag']
    last_modified = get_response.headers['Last-Modified']
    print(f"GET RESPONSE # ETag: {etag} Last-Modified: {last_modified}")

    time.sleep(6)

    response = requests.put(
        url, 
        json ={"ipAddressType": "IP_V6"},
        headers={"If-Unmodified-Since": last_modified, "If-Match": etag}
        )

    '''
    Update ipAddressType with sucess and returns ETag and Last-Modified within header
    '''
    assert response.status_code == 200
    assert 'ETag' in response.headers
    assert 'Last-Modified' in response.headers

    new_etag = response.headers['ETag']
    new_date = response.headers['Last-Modified']
    print(f"PUT 1 RESPONSE HEADER# new ETag: {new_etag} new_date {new_date}")

    time.sleep(6)

    response = requests.put(
        url, 
        json ={"ipAddressType": "IP_V4"}, 
        headers={"If-Unmodified-Since": new_date, "If-Match": new_etag}
        )
    print(f"PUT 2 RESP HEADER: {response.headers}")

    ipAddressType = jsp.jsonpath(json.loads(response.text), 'ipAddressType')
    

    '''
    Update ipAddressType to the previous value giving the same etag as in GET (first time) 
    '''
    assert response.status_code == 200
    assert ipAddressType[0] == "IP_V4"
    assert response.headers['ETag'] == etag
    
    new_date = response.headers['Last-Modified']
    print(f"PUT2 new ETag: {response.headers['ETag']} new_date {new_date}")

    time.sleep(6)

    # first date as last_modified (wrong date)
    # right etag
    put_headers={
        "If-Unmodified-Since": last_modified,
        "If-Match": etag,
    }
    response = requests.put(
        url, 
        json ={"ipAddressType": "IP_V6"}, 
        headers=put_headers)
    
    ipAddressType = jsp.jsonpath(json.loads(response.text), 'ipAddressType')

    print(f"PUT2 new ETag: {response.headers['ETag']} new_date {response.headers['Last-Modified']}")


    assert response.status_code == 412
    # confirmar que não mudou ipAddresseType

    detail = jsp.jsonpath(json.loads(response.text), 'detail')
    print("Attempt to update a DNS rule with different 'Last-Modified' date [error msg]: " 
            + detail[0])

    # right last_modified date
    # wrong etag
    put_headers={
        "If-Unmodified-Since": new_date,
        "If-Match": new_etag,
    }
    response = requests.put(
        url, 
        json ={"ipAddressType": "IP_V6"}, 
        headers=put_headers)
    
    ipAddressType = jsp.jsonpath(json.loads(response.text), 'ipAddressType')

    assert response.status_code == 412
    detail = jsp.jsonpath(json.loads(response.text), 'detail')
    print("Attempt to update a DNS rule with different ETag [error msg]: " 
            + detail[0])
            

################################################################################
# GET

def test_get_individual_dns_rule_200_OK(context):
    appInstanceId = "111"
    dnsRuleId = "dns_rule_1_111"

    url = app_supp + "applications/" + appInstanceId + "/dns_rules/" + dnsRuleId
    response = requests.get(url)

    assert response.status_code == 200

    json_resp = json.loads(response.text)
    print("\nResponse body:")
    pp.pprint(json_resp)


def test_get_individual_dns_rule_400_Bad_Request():
    appInstanceId = "111"
    dnsRuleId = "dns_rule_1_111"

    url = app_supp + "applications/" + appInstanceId + "/dns_rules/" + dnsRuleId
    response = requests.get(url, params={"wrong_param": "rand_str"})

    assert response.status_code == 400
    json_resp = json.loads(response.text)
    print("\nResponse body:")
    pp.pprint(json_resp)


def test_get_individual_dns_rule_404_Not_Found(context):
    # get DNS rule of a nonexistent app
    non_exist_app_id = "5555"
    non_exist_rule_id = "rule_555"
    exist_app_id = "111"
    exist_rule_id = "dns_rule_1_111"

    url = app_supp + "applications/" + non_exist_app_id + "/dns_rules/" + exist_rule_id
    response = requests.get(url)

    assert response.status_code == 404
    detail = jsp.jsonpath(json.loads(response.text), 'detail')
    print("Attempt to get DNS rule of a nonexistent app: " + detail[0])

    # Attempt to update nonexistent DNS rule in a existent app
    url = app_supp + "applications/" + exist_app_id + "/dns_rules/" + non_exist_rule_id
    response = requests.get(url)

    assert response.status_code == 404
    detail = jsp.jsonpath(json.loads(response.text), 'detail')
    print("Attempt to get DNS rule of a nonexistent rule id (in a existent app): " 
            + detail[0])


def test_get_individual_dns_rule_403_Forbidden(context):
    # change app 222 status to "TERMINATING"
    url = tests + "applications/222/update_status"
    requests.patch(url, json={"operationAction": "TERMINATING"})

    # Attempt to get DNS rule from a NOT READY app
    appInstanceId = "222"
    dnsRuleId = "dns_rule_1_222"
    url = app_supp + "applications/" + appInstanceId + "/dns_rules/" + dnsRuleId

    response = requests.get(url)

    assert response.status_code == 403
    detail = jsp.jsonpath(json.loads(response.text), 'detail')
    print("Attempt to get an active DNS rule of a not ready app [error msg]: " 
            + detail[0])

    # Attempt to get a NOT ACTIVE DNS rule
    appInstanceId_2 = "111"
    dnsRuleId_2 = "dns_rule_1_111"

    url = app_supp + "applications/" + appInstanceId_2 + "/dns_rules/" + dnsRuleId_2
    requests.put(url, json ={"state": "INACTIVE"})
    response = requests.get(url)

    assert response.status_code == 403
    detail = jsp.jsonpath(json.loads(response.text), 'detail')
    print("Attempt to get an not active DNS rule [error msg]: " 
            + detail[0])




##################
# All mecDnsRule #
##################

################################################################################
# GET

def test_get_all_dns_rules_200_OK(context):
    appInstanceId = "111"

    url = app_supp + "applications/" + appInstanceId + "/dns_rules"
    response = requests.get(url)

    assert response.status_code == 200

    json_resp = json.loads(response.text)
    print("\nResponse body:")
    pp.pprint(json_resp)
    print(f"no. of found dns rules: {len(json_resp)}")

    assert len(json_resp) == 2
    
    for idx, dnsRule in enumerate(["dns_rule_1_" + str(appInstanceId), 
                                   "dns_rule_2_" + str(appInstanceId)]):
        rule = json_resp[idx]
        rule_id = jsp.jsonpath(rule, 'dnsRuleId')

        assert rule_id[0] == dnsRule

    # Change status of DNS rule "dns_rule_2_111" (app "111") to INACTIVE state
    dnsRuleId = "dns_rule_2_111"
    url_put = app_supp + "applications/" + appInstanceId + "/dns_rules/" + dnsRuleId
    response = requests.put(url_put, json ={"state": "INACTIVE"})

    url_get_all = app_supp + "applications/" + appInstanceId + "/dns_rules"
    response = requests.get(url_get_all)

    json_resp = json.loads(response.text)
    pp.pprint(json_resp)
    print(f"no. of found dns rules: {len(json_resp)}")

    assert len(json_resp) == 1

    rule_id = jsp.jsonpath(json_resp[0], 'dnsRuleId')

    assert rule_id[0] == "dns_rule_1_111"


def test_get_all_dns_rules_400_Bad_Request():
    appInstanceId = "111"
    url = app_supp + "applications/" + appInstanceId + "/dns_rules"
    response = requests.get(url, params={"wrong_param": "rand_str"})

    assert response.status_code == 400
    json_resp = json.loads(response.text)
    print("\nResponse body:")
    pp.pprint(json_resp)


def test_get_all_dns_rules_404_Not_Found(context):
    # get DNS rules of a nonexistent app
    non_exist_app_id = "5555"
    url = app_supp + "applications/" + non_exist_app_id + "/dns_rules"
    response = requests.get(url)

    assert response.status_code == 404
    detail = jsp.jsonpath(json.loads(response.text), 'detail')
    print("Attempt to get DNS rules of a nonexistent app: " + detail[0])


def test_get_all_dns_rules_403_Forbidden(context):
    # change app 222 status to "TERMINATING"
    url = tests + "applications/222/update_status"
    requests.patch(url, json={"operationAction": "TERMINATING"})

    # Attempt to get DNS rule from a NOT READY app
    appInstanceId = "222"
    url = app_supp + "applications/" + appInstanceId + "/dns_rules"
    response = requests.get(url)

    print("\n\nHEADER: ")
    pp.pprint(response.request.headers)

    assert response.status_code == 403
    detail = jsp.jsonpath(json.loads(response.text), 'detail')
    print("Attempt to get DNS rules of a not ready app [error msg]: " 
            + detail[0])







