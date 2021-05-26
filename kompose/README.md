
<ins>Notes</ins>
* apps must be long running. If the container dies after running everything correctly then kubernetes will restart it, resulting in a `crashloopbackoff` error message. See [here](https://stackoverflow.com/questions/41604499/my-kubernetes-pods-keep-crashing-with-crashloopbackoff-but-i-cant-find-any-lo)
* here is a [blog](https://managedkube.com/kubernetes/pod/failure/crashloopbackoff/k8sbot/troubleshooting/2019/02/12/pod-failure-crashloopbackoff.html) with debugging tips



Dependencies
1. install [minikube](https://kubernetes.io/docs/tasks/tools/#minikube)
1. `minikube start`

Build and push to docker trusted registry (eiselesr/alpine in this case)
1. `kompose convert --build local`
   
generate the kubernetes services from the docker-compose file
1. `kompose convert -o output/`
   
Apply resources in kubernetes
1. `kubectl apply -f output/`


Check status
1. `kubectl get pods`

Delete cluster
1. `minikube delete --all`

Delete created resources
1. `kubectl delete -f output/test-deployment.yaml`

[Safetly delete kubernetes pods](https://www.bluematador.com/blog/safely-removing-pods-from-a-kubernetes-node)
Useful when there are strict requirements about the number of replica or stateful pods
1. `kubectl cordon <nodename>`
1. `kubectl delete pod <podname>`
1. `kubectl uncordon <nodename>`