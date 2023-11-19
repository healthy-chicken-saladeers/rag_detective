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

# Setup Deployment

## Build and push Docker containers to GCR
```
ansible-playbook deploy-docker-images.yml -i inventory.yml
```

Output:
```
root@4d9ca7366fa6:/app# ansible-playbook deploy-docker-images.yml -i inventory.yml

PLAY [Build docker images and push them to GCR] ******************************************************************************************************************************************************************************************************************************

TASK [Get timestamp for docker tag] ******************************************************************************************************************************************************************************************************************************************
changed: [localhost]

TASK [Print tag] *************************************************************************************************************************************************************************************************************************************************************
ok: [localhost] => {
    "tag": {
        "changed": true,
        "cmd": "(date +%Y%m%d%H%M%S)",
        "delta": "0:00:00.048593",
        "end": "2023-11-19 15:53:41.110002",
        "failed": false,
        "msg": "",
        "rc": 0,
        "start": "2023-11-19 15:53:41.061409",
        "stderr": "",
        "stderr_lines": [],
        "stdout": "20231119155341",
        "stdout_lines": [
            "20231119155341"
        ]
    }
}

TASK [Build frontend container image] ****************************************************************************************************************************************************************************************************************************************
changed: [localhost]

TASK [Push frontend image to GCR] ********************************************************************************************************************************************************************************************************************************************
ok: [localhost]

TASK [Build api-service container image] *************************************************************************************************************************************************************************************************************************************
changed: [localhost]

TASK [Push api-service image to GCR] *****************************************************************************************************************************************************************************************************************************************
changed: [localhost]

TASK [Save docker tag] *******************************************************************************************************************************************************************************************************************************************************
changed: [localhost]

TASK [Remove all unused containers] ******************************************************************************************************************************************************************************************************************************************
changed: [localhost]

PLAY RECAP *******************************************************************************************************************************************************************************************************************************************************************
localhost                  : ok=8    changed=6    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

## Create Compute Instance (VM) Server in GCP
```
ansible-playbook deploy-create-instance.yml -i inventory.yml --extra-vars cluster_state=present
```

Once the command runs successfully get the external IP address of the compute instance from GCP Console and update the appserver>hosts in inventory.yml file.

Here is the new server with an external IP address: 34.73.94.251.

![](../img/deploy-new-compute-instance.jpg)

Output:
```
root@4d9ca7366fa6:/app# ansible-playbook deploy-create-instance.yml -i inventory.yml --extra-vars cluster_state=present

PLAY [Create App Application Machine] ****************************************************************************************************************************************************************************************************************************************

TASK [Gathering Facts] *******************************************************************************************************************************************************************************************************************************************************
ok: [localhost]

TASK [Create http firewall rule] *********************************************************************************************************************************************************************************************************************************************
changed: [localhost]

TASK [Create https firewall rule] ********************************************************************************************************************************************************************************************************************************************
changed: [localhost]

TASK [Create Compute disk] ***************************************************************************************************************************************************************************************************************************************************
changed: [localhost]

TASK [Create instance] *******************************************************************************************************************************************************************************************************************************************************
changed: [localhost]

TASK [Remove Compute disk] ***************************************************************************************************************************************************************************************************************************************************
skipping: [localhost]

TASK [Wait for SSH to come up] ***********************************************************************************************************************************************************************************************************************************************
ok: [localhost]

TASK [Add host to groupname] *************************************************************************************************************************************************************************************************************************************************
changed: [localhost]

PLAY RECAP *******************************************************************************************************************************************************************************************************************************************************************
localhost                  : ok=7    changed=5    unreachable=0    failed=0    skipped=1    rescued=0    ignored=0  
```

## Provision Compute Instance in GCP
```
ansible-playbook deploy-provision-instance.yml -i inventory.yml
```

This will install and setup everuthing required for deployment.

Output:
```
root@4d9ca7366fa6:/app# ansible-playbook deploy-provision-instance.yml -i inventory.yml

PLAY [Configure app server instance] *****************************************************************************************************************************************************************************************************************************************

TASK [Gathering Facts] *******************************************************************************************************************************************************************************************************************************************************
The authenticity of host '34.73.94.251 (34.73.94.251)' can't be established.
ECDSA key fingerprint is SHA256:SrLTYy8/u8lmq6XV3dz8JWhqK+rVEoNW+0jDSgYGZ+A.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
ok: [34.73.94.251]

TASK [Format persistent disk if it does not contain a filesystem] ************************************************************************************************************************************************************************************************************
changed: [34.73.94.251]

TASK [Create mount directory] ************************************************************************************************************************************************************************************************************************************************
changed: [34.73.94.251]

TASK [Mount persistent disk] *************************************************************************************************************************************************************************************************************************************************
changed: [34.73.94.251]

TASK [Disable unattended upgrade timers] *************************************************************************************************************************************************************************************************************************************
changed: [34.73.94.251] => (item=apt-daily.timer)
changed: [34.73.94.251] => (item=apt-daily-upgrade.timer)

TASK [Reload systemctl daemon] ***********************************************************************************************************************************************************************************************************************************************
changed: [34.73.94.251]

TASK [Wait for unattended upgrade to finish if running] **********************************************************************************************************************************************************************************************************************
changed: [34.73.94.251]

TASK [Update apt catalog] ****************************************************************************************************************************************************************************************************************************************************
ok: [34.73.94.251]

TASK [Install dependencies] **************************************************************************************************************************************************************************************************************************************************
changed: [34.73.94.251]

TASK [Get the current Debian distributor ID] *********************************************************************************************************************************************************************************************************************************
changed: [34.73.94.251]

TASK [Add Docker GPG apt key] ************************************************************************************************************************************************************************************************************************************************
changed: [34.73.94.251]

TASK [Get the current Debian release name] ***********************************************************************************************************************************************************************************************************************************
changed: [34.73.94.251]

TASK [Add Docker apt repository] *********************************************************************************************************************************************************************************************************************************************
changed: [34.73.94.251]

TASK [Install Docker] ********************************************************************************************************************************************************************************************************************************************************
changed: [34.73.94.251]

TASK [Install Pip Packages] **************************************************************************************************************************************************************************************************************************************************
changed: [34.73.94.251]

TASK [Create Docker group] ***************************************************************************************************************************************************************************************************************************************************
ok: [34.73.94.251]

TASK [Authenticate Docker with service account] ******************************************************************************************************************************************************************************************************************************
changed: [34.73.94.251]

TASK [Start docker service] **************************************************************************************************************************************************************************************************************************************************
ok: [34.73.94.251]

PLAY RECAP *******************************************************************************************************************************************************************************************************************************************************************
34.73.94.251               : ok=18   changed=14   unreachable=0    failed=0    skipped=0    rescued=0    ignored=0  
```

## Setup Docker Containers in the Compute Instance
```
ansible-playbook deploy-setup-containers.yml -i inventory.yml
```

Output:
```
root@4d9ca7366fa6:/app# ansible-playbook deploy-setup-containers.yml -i inventory.yml

PLAY [Configure containers on app server] ************************************************************************************************************************************************************************************************************************************

TASK [Gathering Facts] *******************************************************************************************************************************************************************************************************************************************************
ok: [34.73.94.251]

TASK [Create secrets directory] **********************************************************************************************************************************************************************************************************************************************
changed: [34.73.94.251]

TASK [Copy service account key file] *****************************************************************************************************************************************************************************************************************************************
changed: [34.73.94.251]

TASK [Authenticate gcloud using service account] *****************************************************************************************************************************************************************************************************************************
changed: [34.73.94.251]

TASK [Create network] ********************************************************************************************************************************************************************************************************************************************************
changed: [34.73.94.251]

TASK [Copy docker tag file] **************************************************************************************************************************************************************************************************************************************************
changed: [34.73.94.251]

TASK [Get docker tag] ********************************************************************************************************************************************************************************************************************************************************
changed: [34.73.94.251]

TASK [Print tag] *************************************************************************************************************************************************************************************************************************************************************
ok: [34.73.94.251] => {
    "tag": {
        "changed": true,
        "cmd": "cat .docker-tag",
        "delta": "0:00:00.002694",
        "end": "2023-11-19 16:17:57.176450",
        "failed": false,
        "msg": "",
        "rc": 0,
        "start": "2023-11-19 16:17:57.173756",
        "stderr": "",
        "stderr_lines": [],
        "stdout": "20231119155341",
        "stdout_lines": [
            "20231119155341"
        ]
    }
}

TASK [Create frontend container] *********************************************************************************************************************************************************************************************************************************************
changed: [34.73.94.251]

TASK [Create persistent directory] *******************************************************************************************************************************************************************************************************************************************
changed: [34.73.94.251]

TASK [Create api-service container] ******************************************************************************************************************************************************************************************************************************************
changed: [34.73.94.251]

TASK [Check if containers are running] ***************************************************************************************************************************************************************************************************************************************
changed: [34.73.94.251]

TASK [Remove all unused containers] ******************************************************************************************************************************************************************************************************************************************
changed: [34.73.94.251]

PLAY RECAP *******************************************************************************************************************************************************************************************************************************************************************
34.73.94.251               : ok=13   changed=11   unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
```

To test that it works, we can SSH into the server from the GCP console and see status of the containers:

```
sudo docker container ls
sudo docker container logs api-service -f
```

Here is the output in our compute instance:
```
Linux rag-app-demo 5.10.0-26-cloud-amd64 #1 SMP Debian 5.10.197-1 (2023-09-29) x86_64

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
Creating directory '/home/all592_g_harvard_edu'.
all592_g_harvard_edu@rag-app-demo:~$ sudo docker container ls
CONTAINER ID   IMAGE                                                               COMMAND                  CREATED         STATUS         PORTS                    NAMES
abf72bd2b0d1   gcr.io/rag-detective/rag-detective-app-api-service:20231119155341   "/bin/bash ./docker-…"   3 minutes ago   Up 3 minutes   0.0.0.0:9000->9000/tcp   api_service
all592_g_harvard_edu@rag-app-demo:~$ sudo docker container logs api_service -f
Container is running!!!

The following commands are available:
    uvicorn_server
        Run the Uvicorn Server

/home/app/.local/share/virtualenvs/app-4PlAip0Q/lib/python3.9/site-packages/llama_index/download/download_utils.py:11: DeprecationWarning: pkg_resources is deprecated as an API. See https://setuptools.pypa.io/en/latest/pkg_resources.html
  import pkg_resources
/home/app/.local/share/virtualenvs/app-4PlAip0Q/lib/python3.9/site-packages/pkg_resources/__init__.py:2871: DeprecationWarning: Deprecated call to `pkg_resources.declare_namespace('google')`.
Implementing implicit namespace packages (as specified in PEP 420) is preferred to `pkg_resources.declare_namespace`. See https://setuptools.pypa.io/en/latest/references/keywords.html#keyword-namespace-packages
  declare_namespace(pkg)
/home/app/.local/share/virtualenvs/app-4PlAip0Q/lib/python3.9/site-packages/pkg_resources/__init__.py:2871: DeprecationWarning: Deprecated call to `pkg_resources.declare_namespace('google.cloud')`.
Implementing implicit namespace packages (as specified in PEP 420) is preferred to `pkg_resources.declare_namespace`. See https://setuptools.pypa.io/en/latest/references/keywords.html#keyword-namespace-packages
  declare_namespace(pkg)
/home/app/.local/share/virtualenvs/app-4PlAip0Q/lib/python3.9/site-packages/pkg_resources/__init__.py:2350: DeprecationWarning: Deprecated call to `pkg_resources.declare_namespace('google')`.
Implementing implicit namespace packages (as specified in PEP 420) is preferred to `pkg_resources.declare_namespace`. See https://setuptools.pypa.io/en/latest/references/keywords.html#keyword-namespace-packages
  declare_namespace(parent)
/home/app/.local/share/virtualenvs/app-4PlAip0Q/lib/python3.9/site-packages/pkg_resources/__init__.py:2871: DeprecationWarning: Deprecated call to `pkg_resources.declare_namespace('google.logging')`.
Implementing implicit namespace packages (as specified in PEP 420) is preferred to `pkg_resources.declare_namespace`. See https://setuptools.pypa.io/en/latest/references/keywords.html#keyword-namespace-packages
  declare_namespace(pkg)
/home/app/.local/share/virtualenvs/app-4PlAip0Q/lib/python3.9/site-packages/pkg_resources/__init__.py:2871: DeprecationWarning: Deprecated call to `pkg_resources.declare_namespace('google.iam')`.
Implementing implicit namespace packages (as specified in PEP 420) is preferred to `pkg_resources.declare_namespace`. See https://setuptools.pypa.io/en/latest/references/keywords.html#keyword-namespace-packages
  declare_namespace(pkg)
/home/app/.local/share/virtualenvs/app-4PlAip0Q/lib/python3.9/site-packages/pydantic/_internal/_config.py:267: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.4/migration/
  warnings.warn(DEPRECATION_MESSAGE, DeprecationWarning)
INFO:     Started server process [7]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:9000 (Press CTRL+C to quit)
```

To get into a container run:

```
sudo docker exec -it api-service /bin/bash
```

# Configure Nginx file for Web Server

Create nginx.conf file for default routes in web server.

## Setup Webserver on the Compute Instance
```
ansible-playbook deploy-setup-webserver.yml -i inventory.yml
```

Output:
```
root@4d9ca7366fa6:/app# ansible-playbook deploy-setup-webserver.yml -i inventory.yml

PLAY [Configure webserver on the server instance] ****************************************************************************************************************************************************************************************************************************

TASK [Gathering Facts] *******************************************************************************************************************************************************************************************************************************************************
ok: [34.73.94.251]

TASK [Copy nginx config files] ***********************************************************************************************************************************************************************************************************************************************
changed: [34.73.94.251]

TASK [Create nginx container] ************************************************************************************************************************************************************************************************************************************************
changed: [34.73.94.251]

TASK [Restart nginx container] ***********************************************************************************************************************************************************************************************************************************************
changed: [34.73.94.251]

PLAY RECAP *******************************************************************************************************************************************************************************************************************************************************************
34.73.94.251               : ok=4    changed=3    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
```

Once the command runs go to http://34.73.94.251/.