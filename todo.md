# todo

# optional
- allow for stopping pods
- allow for addition, edit and deletion of images
  
# when running in an actual cluster
- see how to organize the local persistent volume (for now targets kind-control-plane)

# left overs (maybe in the future)
- use pagination
- consider using directpv for PersistentVolume of minio docker registry storage
- make docker registry https?
- calculate compressed image size?



`curl -s -I -H "Accept: application/vnd.docker.distribution.manifest.v2+json" http://localhost:5001/v2/helloworldpython/manifests/latest`
(copy hash from Docker-Content-Digest)
`curl -s -X DELETE http://localhost:5001/v2/helloworldpython/manifests/sha256:bd04e5a76bc036842f9e618cef8a9033c4a7c4a7c9880373bc2b783397f75d0f`