FROM gitpod/workspace-python
RUN pyenv install 3.10.14
RUN wget -q -O get_kustomize.sh https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh; \
 chmod 700 get_kustomize.sh; \
 mkdir -p /usr/local/bin; \
 sudo sh -c './get_kustomize.sh 4.5.2 /usr/local/bin'; \
 rm ./get_kustomize.sh
