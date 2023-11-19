# RAG Detective App - Deployment & Scaling

## Deployment using Ansible

In this manual, we will deploy our app using Ansible. 

## Enable GCP APIs

Before deploying, enable the required APIs in GCP. Use the GCP search bar to find each API and enable them:
    - Compute Engine API
    - Service Usage API
    - Cloud Resource Manager API
    - Google Container Registry API

## Setup GCP Service Accounts

1. On the GCP Console, go to: "IAM & Admins" > "Service accounts" from the top-left menu.

![](../img/gcp-iam-service-accounts.jpg)

2.  Create a new service account called `deployment`.

![](../img/gcp-iam-service-accounts-deployment.jpg)

3. Give the service account the following roles:
    - Compute Admin
    - Compute OS Login
    - Container Registry Service Agent
    - Kubernetes Engine Admin
    - Service Account User
    - Storage Admin

![](../img/deployment-roles.jpg)

4. Then click "Done" to create the service account.

5. On the Service Account page, select the "Actions" column to the far right of the deployment service account row by clicking the vertical "...". Select "Manage keys".

![](../img/deployment-manage-keys.jpg)

6. Select "Add Key" and then select "JSON" to create the key. A private json key will download to your computer. Rename the file `deployment.json` and save to `secrets/`.

![](../img/deployment-key.jpg)

7. Follow the same steps to create a new service account called `gcp-service`. Give the account the role:
    - Storage Object Viewer
Create and downlaod a json key renamed `gcp-service.json`  and save to `secrets/`.

## Setup Docker Container

We will use Docker to build a container with all required software. The container will allow you to connect to GCP and create VMs.

1. Go to the deployment directory and run teh following command to build/run the Docker container.
```
cd src/deployment/
sh docker-shell.sh
```

The output will look something like this:
```
alyssa@Alyssas-MacBook-Pro-2 deployment % sh docker-shell.sh
[+] Building 557.9s (19/19) FINISHED                                                                                                                                                                                                                     docker:desktop-linux
 => [internal] load .dockerignore                                                                                                                                                                                                                                        0.0s
 => => transferring context: 2B                                                                                                                                                                                                                                          0.0s
 => [internal] load build definition from Dockerfile                                                                                                                                                                                                                     0.0s
 => => transferring dockerfile: 2.49kB                                                                                                                                                                                                                                   0.0s
 => [internal] load metadata for docker.io/library/ubuntu:20.04                                                                                                                                                                                                          2.3s
 => [auth] library/ubuntu:pull token for registry-1.docker.io                                                                                                                                                                                                            0.0s
 => [internal] load build context                                                                                                                                                                                                                                        0.0s
 => => transferring context: 3.92kB                                                                                                                                                                                                                                      0.0s
 => [ 1/13] FROM docker.io/library/ubuntu:20.04@sha256:ed4a42283d9943135ed87d4ee34e542f7f5ad9ecf2f244870e23122f703f91c2                                                                                                                                                  2.8s
 => => resolve docker.io/library/ubuntu:20.04@sha256:ed4a42283d9943135ed87d4ee34e542f7f5ad9ecf2f244870e23122f703f91c2                                                                                                                                                    0.0s
 => => sha256:ed4a42283d9943135ed87d4ee34e542f7f5ad9ecf2f244870e23122f703f91c2 1.13kB / 1.13kB                                                                                                                                                                           0.0s
 => => sha256:218bb51abbd1864df8be26166f847547b3851a89999ca7bfceb85ca9b5d2e95d 424B / 424B                                                                                                                                                                               0.0s
 => => sha256:bf40b7bc7a11b43785755d3c5f23dee03b08e988b327a2f10b22d01d5dc5259d 2.30kB / 2.30kB                                                                                                                                                                           0.0s
 => => sha256:96d54c3075c9eeaed5561fd620828fd6bb5d80ecae7cb25f9ba5f7d88ea6e15c 27.51MB / 27.51MB                                                                                                                                                                         1.8s
 => => extracting sha256:96d54c3075c9eeaed5561fd620828fd6bb5d80ecae7cb25f9ba5f7d88ea6e15c                                                                                                                                                                                0.8s
 => [ 2/13] RUN apt-get update &&     apt-get install -y curl apt-transport-https ca-certificates gnupg lsb-release openssh-client                                                                                                                                      84.9s
 => [ 3/13] RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" |     tee -a /etc/apt/sources.list.d/google-cloud-sdk.list &&     curl https://packages.cloud.google.com/apt/doc/apt-key.gpg |     gpg  0.8s
 => [ 4/13] RUN install -m 0755 -d /etc/apt/keyrings                                                                                                                                                                                                                     0.2s
 => [ 5/13] RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg                                                                                                                                                  0.4s 
 => [ 6/13] RUN chmod a+r /etc/apt/keyrings/docker.gpg                                                                                                                                                                                                                   0.1s 
 => [ 7/13] RUN echo "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu     "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" |     tee /etc/apt/sources.list.d/docker.list > /dev/nul  0.3s 
 => [ 8/13] RUN apt-get update &&     apt-get install -y google-cloud-sdk google-cloud-sdk-gke-gcloud-auth-plugin jq docker-ce                                                                                                                                         236.9s 
 => [ 9/13] RUN curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.28/deb/Release.key | gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg &&     echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.28/  201.6s
 => [10/13] RUN useradd -ms /bin/bash app -d /home/app -u 1000 -p "$(openssl passwd -1 passw0rd)" &&     usermod -aG docker app &&     mkdir -p /app &&     chown app:app /app                                                                                           0.5s 
 => [11/13] WORKDIR /app                                                                                                                                                                                                                                                 0.0s 
 => [12/13] ADD --chown=app:app . /app                                                                                                                                                                                                                                   0.0s 
 => [13/13] RUN set -ex;     ansible-galaxy collection install community.general community.kubernetes                                                                                                                                                                   22.7s 
 => exporting to image                                                                                                                                                                                                                                                   4.2s 
 => => exporting layers                                                                                                                                                                                                                                                  4.2s 
 => => writing image sha256:1015ac5107d43a3cb2c77e92cfd65ebf2575dfc6815b3bae400ca62e29dcdd7f                                                                                                                                                                             0.0s 
 => => naming to docker.io/library/rag-detective-app-deployment                                                                                                                                                                                                          0.0s 
                                                                                                                                                                                                                                                                              
What's Next?                                                                                                                                                                                                                                                                  
  View a summary of image vulnerabilities and recommendations → docker scout quickview
WARNING: The requested image's platform (linux/amd64) does not match the detected host platform (linux/arm64/v8) and no specific platform was requested
Container is running!!!
Activated service account credentials for: [deployment@rag-detective.iam.gserviceaccount.com]
Updated property [core/project].
Adding credentials for: gcr.io
Docker configuration file updated.
root@7a710e4f31f8:/app#
```

2. Check the version of the following tools:
```
gcloud --version
ansible --version
kubectl version --client
```

Here is the output:
```
root@7a710e4f31f8:/app# gcloud --version

Google Cloud SDK 455.0.0
alpha 2023.11.10
beta 2023.11.10
bq 2.0.98
bundled-python3-unix 3.11.6
core 2023.11.10
gcloud-crc32c 1.0.0
gke-gcloud-auth-plugin 0.5.6
gsutil 5.27
root@7a710e4f31f8:/app# ansible --version
ansible [core 2.13.13]
  config file = None
  configured module search path = ['/root/.ansible/plugins/modules', '/usr/share/ansible/plugins/modules']
  ansible python module location = /usr/local/lib/python3.8/dist-packages/ansible
  ansible collection location = /root/.ansible/collections:/usr/share/ansible/collections
  executable location = /usr/local/bin/ansible
  python version = 3.8.10 (default, May 26 2023, 14:05:08) [GCC 9.4.0]
  jinja version = 3.1.2
  libyaml = True
root@7a710e4f31f8:/app# kubectl version --client
Client Version: v1.28.4
Kustomize Version: v5.0.4-0.20230601165947-6ce0bf390ce3
```

3. Check to make sure you are authenticated to GCP
```
gcloud auth list
```

Here is the output:
```
root@7a710e4f31f8:/app# gcloud auth list
                 Credentialed Accounts
ACTIVE  ACCOUNT
*       deployment@rag-detective.iam.gserviceaccount.com

To set the active account, run:
    $ gcloud config set account `ACCOUNT`

root@7a710e4f31f8:/app# 

```

## Setup SSH

#### Configure OS login for service account:
```
gcloud compute project-info add-metadata --project rag-detective --metadata enable-oslogin=TRUE
```

Here is the outout:
```
root@7a710e4f31f8:/app# gcloud compute project-info add-metadata --project rag-detective --metadata enable-oslogin=TRUE
Updated [https://www.googleapis.com/compute/v1/projects/rag-detective].
root@7a710e4f31f8:/app# 
```

#### Create SSH key for service account:
```
cd /secrets
ssh-keygen -f ssh-key-deployment
cd /app
```

Here is the output:
```
root@7a710e4f31f8:/app# cd /secrets
root@7a710e4f31f8:/secrets# ssh-keygen -f ssh-key-deployment
Generating public/private rsa key pair.
Enter passphrase (empty for no passphrase): 
Enter same passphrase again: 
Your identification has been saved in ssh-key-deployment
Your public key has been saved in ssh-key-deployment.pub
The key fingerprint is:
XXXXXXXXXXXXXXXXX root@7a710e4f31f8
The key's randomart image is:
+---[RSA 3072]----+
|====o.*OO= .     |
|*++.o=o++o=      |
|o*  ...ooo       |
|  .   ooo..      |
|   . . +S= .     |
|    . . o +      |
|       . o       |
|        o.       |
|        .E.      |
+----[SHA256]-----+
root@7a710e4f31f8:/secrets# cd /app
root@7a710e4f31f8:/app#
```

#### Provide public SSH keys to instances
```
gcloud compute os-login ssh-keys add --key-file=/secrets/ssh-key-deployment.pub
```

Here is the output:
```
root@7a710e4f31f8:/app# gcloud compute os-login ssh-keys add --key-file=/secrets/ssh-key-deployment.pub
loginProfile:
  name: '107615736039570311862'
  posixAccounts:
  - accountId: rag-detective
    gid: '2566290116'
    homeDirectory: /home/sa_107615736039570311862
    name: users/deployment@rag-detective.iam.gserviceaccount.com/projects/rag-detective
    operatingSystemType: LINUX
    primary: true
    uid: '2566290116'
    username: sa_107615736039570311862
  sshPublicKeys:
    d6f6123d82de98ad1d11446f4810c1c774708fc25b806d442eb5d0394af83a8f:
      fingerprint: d6f6123d82de98ad1d11446f4810c1c774708fc25b806d442eb5d0394af83a8f
      key: |
        ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDTuKbLcGYVXT0g3oLBUgBQXWA2tSoTFJG1ZV+RBx6PXOCkM0yvSrOsF0UP/2oS4sAOGdkRy8iDy5n+uiPg4XfIiiNNkjZ5UPHfw3emuuZ6ipqHdCXZn0ZmXylK39ZCvmghXdXZ6cgHduBBD64t1RkDUz2Aqlo2+7L7bbVNVwhM3C55nj12qqNyxki9aBeMczOJM+/6OkgrdxsMdmZSVNO79ys9rzalnm7lGsC9WBp1LTaKyvV/rR+udeCSnHRFYlCU2amLGSRk/fP8uhQYZRhhNzmHmoVrTZgiahq85dfdqDbR4Vdkz6uG65OBGVfk37EQ6Fc3TGHaBaZqcy8aiuy+sg5AI/BQ+fhe67WPpjWgimImOAUYS8HNHZsnB2aYZk8W+211bd37z96boEvQ/Y/Msdlq0ckkFQ3cWBynY13r8VMMlqerrYpVTs/kLrVMD1aM7fRONblddCKYCGEHnFYzXwehpXw66Fbmtz/IQD1psauvvMSppatEK1D1ArPBSRk= root@7a710e4f31f8
      name: users/deployment@rag-detective.iam.gserviceaccount.com/sshPublicKeys/d6f6123d82de98ad1d11446f4810c1c774708fc25b806d442eb5d0394af83a8f
root@7a710e4f31f8:/app# 
```

The username is: `sa_107615736039570311862`.

## Setup Deployment

#### Build and push Docker containers to GCR
```
ansible-playbook deploy-docker-images.yml -i inventory.yml
```

