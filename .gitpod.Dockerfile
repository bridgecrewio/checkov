FROM gitpod/workspace-python
RUN pyenv install 3.7.12
RUN wget -q -O get_kustomize.sh https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh; chmod 700 get_kustomize.sh; ./get_kustomize.sh; mv /kustomize /usr/bin/kustomize; rm ./get_kustomize.sh
