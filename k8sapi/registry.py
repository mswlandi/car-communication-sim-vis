import requests
import json

# name and size
class ImageTag:
    def __init__(self, imagename, name, registryIP, port):
        self.imagename = imagename
        self.name = name
        self.size = ''
        self.registryIP = registryIP
        self.port = port
    
    # fetches and calculates Tag's size
    # in MB, rounded to 2 decimal places and as string
    def fetchTagSize(self):
        response = requests.get(f"http://{self.registryIP}:{self.port}/v2/{self.imagename}/manifests/{self.name}")
        manifest = json.loads(response.content)

        self.size = 0
        for layer in manifest["fsLayers"]:
            headers = requests.head(f"http://{self.registryIP}:{self.port}/v2/{self.imagename}/blobs/{layer['blobSum']}").headers
            self.size += int(headers['Content-Length'])

        self.size = f'{self.size / 1024 / 1000:.2f}'
        return self.size

# name, tag list
class DockerImage:
    def __init__(self, name, registryIP, port):
        self.name = name
        self.tags = []
        self.registryIP = registryIP
        self.port = port
    
    # fetches the tags (only names) from the registry API
    def fetchTagsNames(self):
        response = requests.get(f'http://{self.registryIP}:{self.port}/v2/{self.name}/tags/list')
        tag_names = json.loads(response.content)['tags']

        self.tags = []
        for tag_name in tag_names:
            self.tags.append(ImageTag(self.name, tag_name, self.registryIP, self.port))

        return self.tags
    
    def fetchTagSizes(self):
        for tag in self.tags:
            tag.fetchTagSize()

def get_image_list(registryIP, port):
    image_catalog = requests.get(f'http://{registryIP}:{port}/v2/_catalog')

    image_name_list = json.loads(image_catalog.content)['repositories']

    image_list = []
    for image_name in image_name_list:
        image = DockerImage(image_name, registryIP, port)
        image.fetchTagsNames()
        # image.fetchTagSizes() # only works with local storage
        image_list.append(image)

    return image_list

if __name__ == '__main__':
    for image in get_image_list('localhost', 5001):
        print(f'{image.name} - {image.size}')