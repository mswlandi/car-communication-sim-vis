from kubernetes import config
from kubernetes.client import Configuration, V1ObjectMeta, V1Container, V1PodSpec, V1Pod
from kubernetes.client.api import core_v1_api

k8sapi = None

def create_pod(name, image, tag, args=None, node_name='kind-control-plane', registry_address='localhost', registry_port=5001):
    global k8sapi

    metadata = V1ObjectMeta(name=name)
    container = V1Container(name='container', image=f'localhost:5001/{image}:{tag}', args=args)
    # container = V1Container(name='container', image=f'{registry_address}:{registry_port}/{image}:{tag}', args=args)
    pod_spec = V1PodSpec(containers=[container], node_name=node_name)
    pod_body = V1Pod(metadata=metadata, spec=pod_spec, kind='Pod', api_version='v1')
    pod = k8sapi.create_namespaced_pod(namespace='default', body=pod_body)

    print(f'Created pod {name} with image {image}:{tag} on node {node_name}')

    return pod


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