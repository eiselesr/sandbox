build_kube:
	kompose --file docker-compose.yml convert --verbose --build local -o Demo/deployments/

deploy_kube:
	kubectl apply -f deployments/allocator-service-deployment.yaml

withdraw_kube:
	kubectl delete -f deployments/allocator-service-deployment.yaml