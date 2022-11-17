from kubernetes import config
from kubernetes.client import Configuration, V1ObjectMeta, V1Container, V1PodSpec, V1Pod, V1EnvVar, V1Namespace
from kubernetes.client.api import core_v1_api

k8sapi: core_v1_api.CoreV1Api = None


def create_pod(
    name: str,
    image: str,
    tag: str,
    args: list[str] = None,
    node_name: str = 'kind-control-plane',
    registry_address: str = 'localhost',
    registry_port: int = 5001,
    envs: dict = None,
    namespace: str = "default"):
    """k8s api wrapper to launch a pod with a given image and tag

    envs is a dict with the key being the name and the value being the value
    """

    global k8sapi

    envs_formatted = []

    for key, value in envs.items():
        envs_formatted.append(V1EnvVar(name = key, value=value))

    create_namespace_if_inexistent(namespace)

    metadata = V1ObjectMeta(name=name)
    container = V1Container(name='container', image=f'{registry_address}:{registry_port}/{image}:{tag}', args=args, env=envs_formatted)
    pod_spec = V1PodSpec(containers=[container], node_name=node_name, restart_policy="Never")
    pod_body = V1Pod(metadata=metadata, spec=pod_spec, kind='Pod', api_version='v1')
    pod = k8sapi.create_namespaced_pod(namespace=namespace, body=pod_body)

    print(f'Created pod {name} with image {image}:{tag} on node {node_name}')

    return pod


def create_namespace_if_inexistent(name: str):
    '''Creates namespace if inexistent, returns true if created, false if already existed'''
    global k8sapi

    namespace_names = [namespace.metadata.name for namespace in k8sapi.list_namespace().items]
    # print(namespace_names)
    if name not in namespace_names:
        body = V1Namespace(metadata=V1ObjectMeta(name=name))
        k8sapi.create_namespace(body, pretty=True)
        return True
    
    return False


def delete_namespace_pods(namespace, destroy_namespace=False, prefix=""):
    """deletes pods from a namespace
    
    destroy_namespace: deletes namespace and all its pods (overrides prefix)
    prefix: delete only pods with given prefix
    """
    global k8sapi

    if destroy_namespace:
        k8sapi.delete_namespace(namespace)
    
    elif prefix == "":
        k8sapi.delete_collection_namespaced_pod(namespace)
    
    else:
        pod_names_list = [pod.metadata.name for pod in k8sapi.list_namespaced_pod(namespace, watch=False).items]
        for pod_name in pod_names_list:
            if pod_name.startswith(prefix):
                k8sapi.delete_namespaced_pod(name=pod_name, namespace=namespace)


def delete_pod(name, namespace):
    '''deletes a specific pod, given its name and namespace'''
    global k8sapi

    k8sapi.delete_namespaced_pod(name, namespace)


def load_api():
    global k8sapi

    # Loading Kubernetes Configs
    config.load_kube_config()
    try:
        c = Configuration().get_default_copy()
    except AttributeError:
        c = Configuration()
        c.assert_hostname = False
    Configuration.set_default(c)
    k8sapi = core_v1_api.CoreV1Api()
    
    return k8sapi


# returns a list of (node_name, ip_address)
def get_node_list():
    global k8sapi

    resp = k8sapi.list_node()
    node_addresses_list = []
    for node in resp.items:
        node_addresses_list.append((resp.items[0].metadata.name, [address.address for address in node.status.addresses if address.type == 'InternalIP'][0]))
    
    return node_addresses_list


def main():
    k8sapi = load_api()

    resp = k8sapi.list_node()

    print(f"{resp.items[0].metadata.name} - {[ address.address for address in resp.items[0].status.addresses if address.type == 'InternalIP'][0]}")

    create_pod("alpinetest", "localhost:5001/my-alpine", "latest", args=['tail', '-f', '/dev/null'])


if __name__ == '__main__':
    main()