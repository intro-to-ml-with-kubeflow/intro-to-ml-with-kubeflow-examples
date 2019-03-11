
multipass launch bionic -n kubeflow -m 8G -d 40G -c 4
multipass exec kubeflow -- sudo snap install microk8s --classic
multipass exec kubeflow -- microk8s.enable dns dashboard
multipass exec kubeflow -- sudo iptables -P FORWARD ACCEPT
multipass exec kubeflow -- sudo snap alias microk8s.kubectl kubectl
multipass exec kubeflow -- microk8s.enable registry
multipass exec kubeflow -- sudo snap alias microk8s.docker docker
