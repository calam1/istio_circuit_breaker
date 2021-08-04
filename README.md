```
# This github was created off of the code, examples, ideas from https://tech.olx.com/demystifying-istio-circuit-breaking-27a69cac2ce4

# fyi I am using python 3.9.6

# it's always a good idea to create a virtualenv, and remember to activate it, go into your code repo / root folder
python3 -m venv ~/.venvs/circuitbreaker
source  ~/.venvs/circuitbreaker/bin/activate

If you are are like most of us, you have performed some actions that override default pip - https://confluence.grainger.com/display/PLE/Using+AWS+CodeArtifact#UsingAWSCodeArtifact-PIPPIP

so you must dpctl pip-login first then:

# install flask and requests
pip3 install flask
pip3 install requests   

# to depoly onto minikube remember to set the minikube docker context; this is so that your minikube has access to your docker image
eval $(minikube -p minikube docker-env)  

# then build the docker images for the test apps
# server
docker build -t py_server --file Dockerfile_server . 

# client
docker build -t py_client --file Dockerfile_client .

## minikube 
# create a new namespace
kubectl create namespace circuitbreaker 

# enable sidecar injection
kubectl label namespace circuitbreaker istio-injection=enabled --overwrite

# check to see if your namespace, circuitbreaker is enabled
kubectl get namespace -L istio-injection

# deploy the apps 
kubectl apply -f deployment/deployment.yml -n circuitbreaker 


## Testing one client and one server
# max connections 5, notice in the client logs, that only 5 requests get served in about 5 seconds and the other 5 are about 10 seconds
 kubectl apply -f deployment/destination_max_5.yml -n circuitbreaker  

# fail fast set http1MaxPendingRequests to 1, so we get 503 error codes - you will typically(not guaranteed) see 5 processes finish about 5 seconds 1 process finish in about 10 seconds then the other 4 fail
kubectl apply -f deployment/destination_fail_fast.yml -n circuitbreaker  

pyclient ----------START BATCH----------
pyclient STATUS: 503, START: 22:26:00, END: 22:26:00, TIME: 0.013655900955200195
pyclient STATUS: 503, START: 22:26:00, END: 22:26:00, TIME: 0.013519287109375 
pyclient STATUS: 503, START: 22:26:00, END: 22:26:00, TIME: 0.04114055633544922
pyclient STATUS: 503, START: 22:26:00, END: 22:26:00, TIME: 0.036191463470458984
pyclient STATUS: 200, START: 22:26:00, END: 22:26:05, TIME: 5.0132763385772705
pyclient STATUS: 200, START: 22:26:00, END: 22:26:05, TIME: 5.019428014755249
pyclient STATUS: 200, START: 22:26:00, END: 22:26:05, TIME: 5.012197494506836
pyclient STATUS: 200, START: 22:26:00, END: 22:26:05, TIME: 5.026354551315308
pyclient STATUS: 200, START: 22:26:00, END: 22:26:05, TIME: 5.019253492355347
pyclient STATUS: 200, START: 22:26:00, END: 22:26:10, TIME: 10.016169786453247

## Testing one client and and multiple (3) servers
kubectl scale deployment/pyserver --replicas=3

So we are still using the deployment/destination_fail_fast.yml configuration. What are our expectations, that since we have 4 servers we should have 4 times the capacity regarding the circuit breaker? If you look at the logs the failure/success rate are similar to if we just had one server.  This tells us the destination config applies to the "service" and not the "pods"

Let' see how many servers our client is hooked up to

kubectl exec $(kubectl get pod --selector app=pyclient --output jsonpath='{.items[0].metadata.name}') -c istio-proxy -- curl -X POST http://localhost:15000/clusters | grep pyserver | grep cx_active

  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 88010    0 88010    0     0  13.9M      0 --:--:-- --:--:-- --:--:-- 13.9M
outbound|80||pyserver.circuitbreaker.svc.cluster.local::172.17.0.15:5000::cx_active::2
outbound|80||pyserver.circuitbreaker.svc.cluster.local::172.17.0.16:5000::cx_active::2
outbound|80||pyserver.circuitbreaker.svc.cluster.local::172.17.0.20:5000::cx_active::2

The client proxy has 2 active connections to each pod in the target service. Instead of 5, it’ 6. As mentioned in both Envoy and Istio docs, the proxy allows some leeway in terms of the number of connections.

```