from flask import Flask, render_template, request

import os
import sys

# make parent directory available to import k8sapi
sys.path.insert(1, os.path.join(sys.path[0], '../..'))

import k8sapi.registry as docker_registry
import k8sapi.api as k8sapi

app = Flask(__name__)
k8sapi.load_api()

running_pods = {} # dict with pod-name as key and running-instances as value

registry_address = 'localhost'
registry_port = 5001

@app.route('/', methods=('GET', 'POST'))
def list():
    global running_pods

    if request.method == 'POST':
        k8s_pod_image_name = request.form['image-name']
        k8s_pod_tag = request.form['tag']
        k8s_pod_node = request.form['node']

        if k8s_pod_image_name in running_pods:
            running_pods[k8s_pod_image_name] += 1
        else:
            running_pods[k8s_pod_image_name] = 1
        
        k8sapi.create_pod(
            f'{k8s_pod_image_name}-{running_pods[k8s_pod_image_name]}',
            k8s_pod_image_name,
            k8s_pod_tag,
            node_name=k8s_pod_node,
            args=['tail', '-f', '/dev/null'], # command for looping with images that just stop
            registry_address=registry_address,
            registry_port=registry_port)

    imagelist = docker_registry.getImageList(registry_address, registry_port)
    return render_template('list.html', imagelist=imagelist, nodelist=k8sapi.get_node_list())

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
