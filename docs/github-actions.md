# Automated Deployment with GitHub Actions

Using GitHub Actions to automate the deployment of the app is key to achieving regular and reliable updates, a process called CI/CD. Continuous Integration and Continuous Delivery/Deployment (CI/CD) takes care of integrating and deploying changes automatically. This results in quicker feedback, faster software releases, better scaling, and more uniform deployments, making the overall development process faster and more responsive.

## Setup GitHub Action Workflow Credentials

We need to set up credentials in GitHub to perform the following functions in GCP:

* Push docker images to GCR
* Update Kubernetes deployments

### Setup

1. Go to the repo Settings
2. Select "Secrets and variables" from the left side menu and choose "Actions"
3. Under "Repository secrets," click "New repository secret".

![](../img/github-secrets.jpg)

4. Name: `GOOGLE_APPLICATION_CREDENTIALS`
5. Value: Copy and paste the contents of your secrets file `deployment.json`

![](../img/github-credentials.jpg)

## Update the k8s Cluster

Our yaml file can be found under `.github/workflows/ci-cd.yml` in the project repo.

The yaml file implements a CI/CD workflow that

* Invokes docker image building and pushing to GCR on changes to code in the respective containers and a git commit has a comment "/run-deploy-app".
* Deploy the updated containers to the k8s cluster in GKE.

You can view the progress of in GitHub under the Actions tab:

![](../img/github-actions.jpg)

Make sure your commit has the comment "/run-deploy-app".

```
git add .
git commit -m "/run-deploy-app"
git push
```