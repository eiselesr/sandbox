import requests
import json
from requests_toolbelt import MultipartEncoder

# def create_tenant(pulsar_admin_url=None, tenant=None):
#     # create tenant
#     r = requests.put("{}/tenants/{}".format(pulsar_admin_url, tenant),
#                      data=json.dumps({"allowedClusters": ["standalone", "pulsar-modicum"]}),
#                      headers={'Content-Type': "application/json", 'Accept': "application/json"})
#
#     print(r.request.url)
#     print(r.request.body)
#     if (r.status_code == 400) or (r.status_code == 204):
#         print("new tenant created: {}".format(tenant))
#     elif r.status_code == 403:
#         print("{}: The requester doesn't have admin permissions".format(r.status_code))
#     elif r.status_code == 409:
#         print("409: Tenant already exists")
#     elif (r.status_code == 412):
#         print("412: Clusters do not exist: {}")
#     else:
#         print("unknown error: {}, {}".format(r.status_code, r.content))
#         quit()


def create_tenant(pulsar_admin_url=None, clusters=None, tenant=None):
    # create tenant
    r = requests.put("{}/tenants/{}".format(pulsar_admin_url, tenant),
                     data=json.dumps({"allowedClusters": clusters}),
                     headers={'Content-Type': "application/json", 'Accept': "application/json"})

    print(r.request.url)
    print(r.request.body)
    if (r.status_code == 400) or (r.status_code == 204):
        print(f"{r.status_code} {r.content}: new tenant created: {tenant}")
    elif r.status_code == 403:
        print(f"{r.status_code} {r.content}")
    elif r.status_code == 409:
        print(f"{r.status_code} {r.content}")
    elif r.status_code == 412:
        print(f"{r.status_code} {r.content}")
    else:
        print("unknown error: {}, {}".format(r.status_code, r.content))
        quit()


def get_tenants(pulsar_admin_url=None):

    r = requests.get("{}/tenants".format(pulsar_admin_url),
                     headers={'Content-Type': "application/json",
                              'Accept': "application/json"})

    # print(r.request.url)
    if r.status_code == 200:
        print("Known tenants: {}".format(r.json()))
        return r.json()
    elif r.status_code == 403:
        print(f"{r.status_code}, {r.content} The requester doesn't have admin permissions")
    elif r.status_code == 404:
        print(f"{r.status_code}, {r.content}: Tenant doesn't exist")
    else:
        print(f"unknown error: {r.status_code}, {r.content}")
        quit()



def get_clusters(pulsar_admin_url=None, tenant=None):

    r = requests.get("{}/clusters".format(pulsar_admin_url),
                     headers={'Content-Type': "application/json",
                              'Accept': "application/json"})

    # print(r.request.url)
    if r.status_code == 200:
        print("clusters: {}".format(r.json()))
        return r.json()
    elif r.status_code == 500:
        print(f"{r.status_code}: Internal server error")
    else:
        print(f"unknown error: {r.status_code}, {r.content}")
        quit()


def create_namespace(pulsar_admin_url=None, tenant=None, namespace=None):
    # create tenant
    r = requests.put("{}/namespaces/{}/{}".format(pulsar_admin_url, tenant, namespace))


    if (r.status_code == 400) or (r.status_code == 204):
        print("new namespace created: {}/{}".format(tenant, namespace))
    elif r.status_code == 403:
        print("{}: Don't have admin permission".format(r.status_code))
    elif r.status_code == 404:
        print("{}: Tenant or cluster doesn't exist".format(r.status_code))
    elif r.status_code == 409:
        print("{}: namespace already exists".format(r.status_code))
    elif r.status_code == 412:
        print("{}: Namespace name is not valid".format(r.status_code))
    else:
        print("unknown error: {}, {}".format(r.status_code, r.content))
        quit()

def get_namespaces(pulsar_admin_url=None, tenant=None):

    r = requests.get("{}/namespaces/{}".format(pulsar_admin_url, tenant),
                     headers={'Content-Type': "application/json",
                              'Accept': "application/json"})

    # print(r.request.url)
    if (r.status_code == 200):
        print("known namespaces: {}".format(r.json()))
        return r.json()
    elif r.status_code == 403:
        print("{}: The requester doesn't have admin permissions".format(r.status_code))
    elif r.status_code == 404:
        print("404: Tenant or cluster or namespace doesn't exist")
    else:
        print("unknown error: {}, {}".format(r.status_code, r.content))
        quit()


def get_functions():

    api = "http://localhost:8080/admin/v3/functions/public/default"
    headers = {'Content-Type': "application/json",
               'Accept': "application/json"}
    r = requests.get(api, headers=headers)

    print(r.json())
    print(r.request.url)


def create_reverse():

    api_url = f"http://localhost:8080/admin/v3/functions/public/default/reverse"

    config = {"tenant": "public",
              "namespace": "default",
              "name": "reverse",
              "className": "reverse",
              "inputs": ["persistent://public/default/backwards"],
              "output": "persistent://public/default/forwards",
              "outputSchemaType": "",
              "forwardSourceMessageProperty": True,
              "userConfig": {},
              "py": "/shared/reverse.py"}

    file = open('/home/ubuntu/IdeaProjects/pulsar-python-helloWorld/shared/reverse.py', 'rb')
    mp_encoder = MultipartEncoder(
        fields={
            'functionConfig': (None, json.dumps(config), 'application/json'),
            'data': ("reverse.py", file, 'application/octet-stream')
        }
    )

    headers = {'Content-Type': mp_encoder.content_type, 'user-agent': 'Pulsar-Java-v2.6.1'}

    print(mp_encoder)
    print(mp_encoder.content_type)
    print(api_url)
    print(headers)

    response = requests.post(api_url, data=mp_encoder, headers=headers)

    print(response.reason)
    print(response.content)


def create_function(api_url: str, config: dict, function_path: str):
    """
    :param api_url: f"http://localhost:8080/admin/v3/functions/public/default/reverse"
    :param config: config = {"tenant": "public",
                             "namespace": "default",
                             "name": "reverse",
                             "className": "reverse",
                             "inputs": ["persistent://public/default/backwards"],
                             "output": "persistent://public/default/forwards",
                             "outputSchemaType": "",
                             "forwardSourceMessageProperty": True,
                             "userConfig": {},
                             "py": "/shared/reverse.py"}
                   config = {"tenant": str,
                             "namespace": str,
                             "name": str,
                             "className": str,
                             "inputs": list,
                             "output": str,
                             "outputSchemaType": "",
                             "forwardSourceMessageProperty": bool,
                             "userConfig": dict,
                             "py": str}
    :param function_path: "/home/ubuntu/projects/MODiCuM-Streaming/deployment/shared/reverse.py
    :return:
    """

    file = open(function_path, 'rb')
    mp_encoder = MultipartEncoder(
        fields={
            'functionConfig': (None, json.dumps(config), 'application/json'),
            'data': (f"{config['name']}.py", file, 'application/octet-stream')
        }
    )

    headers = {'Content-Type': mp_encoder.content_type, 'user-agent': 'Pulsar-Java-v2.6.1'}

    print(mp_encoder)
    print(mp_encoder.content_type)
    print(api_url)
    print(headers)

    response = requests.post(api_url, data=mp_encoder, headers=headers)

    print(response.reason)
    print(response.content)

def update_function(api_url: str, config: dict, function_path: str):
    """
    :param api_url: f"http://localhost:8080/admin/v3/functions/public/default/reverse"
    :param config: config = {"tenant": "public",
                             "namespace": "default",
                             "name": "reverse",
                             "className": "reverse",
                             "inputs": ["persistent://public/default/backwards"],
                             "output": "persistent://public/default/forwards",
                             "outputSchemaType": "",
                             "forwardSourceMessageProperty": True,
                             "userConfig": {},
                             "py": "/shared/reverse.py"}
                   config = {"tenant": str,
                             "namespace": str,
                             "name": str,
                             "className": str,
                             "inputs": list,
                             "output": str,
                             "outputSchemaType": "",
                             "forwardSourceMessageProperty": bool,
                             "userConfig": dict,
                             "py": str}
    :param function_path: "/home/ubuntu/projects/MODiCuM-Streaming/deployment/shared/reverse.py
    :return:
    """

    file = open(function_path, 'rb')
    mp_encoder = MultipartEncoder(
        fields={
            'functionConfig': (None, json.dumps(config), 'application/json'),
            'data': (f"{config['name']}.py", file, 'application/octet-stream')
        }
    )

    headers = {'Content-Type': mp_encoder.content_type, 'user-agent': 'Pulsar-Java-v2.6.1'}

    print(mp_encoder)
    print(mp_encoder.content_type)
    print(api_url)
    print(headers)

    response = requests.put(api_url, data=mp_encoder, headers=headers)

    print(response.reason)
    print(response.content)





if __name__ == "__main__":

    create_reverse()