<h1>⚙️ DevOps Engineer Assignment 1: Serverless Data Pipeline with Automated CI/CD</h1>

This repository presents a fully automated cloud data processing pipeline leveraging **Jenkins CI/CD** and **Terraform Infrastructure as Code (IaC)**. The pipeline is designed to process files stored in AWS S3 and maintain data reliability using a dual-path storing mechanism.

---

## 🎯 Project Goal & Functional Scope

The objective of this assignment is to build a serverless deployment workflow that:

✔ Automates AWS infrastructure provisioning  
✔ Containerizes the data processing application  
✔ Deploys and triggers the logic through AWS Lambda  
✔ Implements a fault-resilient data storage flow  

### 🌐 Functional Flow Summary

The application performs the following:

- Reads incoming files from an **Amazon S3 Bucket**  
- Tries inserting extracted records into an **Amazon RDS (PostgreSQL) database**
- If database insertion fails, the metadata is redirected to the **AWS Glue Data Catalog**

✅ This ensures **no data loss** and consistent metadata record-keeping

---

## ✅ Assignment Deliverables

1️⃣ Fully structured **GitHub repository** containing application + IaC code  
2️⃣ **Dockerized Python application** capable of execution in Lambda  
3️⃣ Deployment of container image to **Amazon ECR**  
4️⃣ Creation and testing of **Lambda function** referencing the ECR image  
5️⃣ Complete **CI/CD pipeline** built using Jenkins with automated Terraform steps  
6️⃣ Attached **proof of working deployment** such as logs and screenshots

---

<h2>🚀 CI/CD Pipeline Design</h2>

The Jenkins pipeline is built to eliminate circular dependency issues (Lambda requiring pre-built ECR image). It executes in four major stages:

**Stage 1 — Terraform Initial Apply**  
Provision foundational AWS resources including:  
• ECR Repository  
• S3 Bucket  
• IAM Execution Role  
• RDS Subnet Group  
⛔ Lambda skipped intentionally until the image is ready  

**Stage 2 — ECR Login**  
Authenticate into AWS ECR to allow pushing Docker images  

**Stage 3 — Docker Image Build + Push**  
Build the container image locally → Tag it → Upload to ECR  

**Stage 4 — Final Terraform Apply**  
Deploys the Lambda function now that the image exists in ECR  

🔁 Ensures seamless infrastructure + application rollout

---

<h2>📁 Repository Structure</h2>

| Component | Description |
|----------|-------------|
| **Jenkinsfile** | Controls CI/CD flow including Terraform + Docker actions |
| **main.tf** | Terraform provisioning for RDS, Lambda, ECR, S3 & IAM roles |
| **imp.py** (Python App) | Logic for S3 → RDS data insertion + Glue fallback |
| **Dockerfile** | Builds a Lambda-compatible lightweight image |

---

<h2>☁️ AWS Resources Created (Region: us-east-1)</h2>

Below resources are provisioned via Terraform:

- **Amazon ECR Repository** → `devops-e2e-app`  
- **Amazon S3 Bucket** → `akshay-devops-pipe-10252025`  
- **RDS Subnet Group** → `terraform-20251025083740891100000001`  
- **Amazon RDS PostgreSQL** `instance`  
- **IAM Role** `AdministratorAccess`  
- **AWS Lambda Function** → `s3_to_rds_glue_lambda`  

---

<h2>✅ Deployment Proof (Screenshots)</h2>

<h3 align="center">1. Jenkins Successful Pipeline Execution</h3>

> The following screenshots validate each stage of the deployment workflow, confirming that the CI/CD pipeline executed successfully and all AWS resources were provisioned as intended.

<img width="3022" height="1784" alt="image" src="https://github.com/user-attachments/assets/8f619e72-1a80-482a-98aa-f72c9ba35464" />


<h3 align="center">2. ECR Repository Verification</h3>

> This screenshot verifies that the ECR repository was provisioned using Terraform and that the pipeline pushed the application’s container image to the repository as part of the deployment process.
<img width="3024" height="1176" alt="image" src="https://github.com/user-attachments/assets/b7cc04a7-8465-4841-8ac1-b1111ea72a13" />



<h3 align="center">3. AWS Lambda Function Verification</h3>

This screenshot verifies that the Lambda function has been successfully deployed and is using the container image stored in Amazon ECR.
<img width="3024" height="1452" alt="image" src="https://github.com/user-attachments/assets/025bf421-562f-43e0-a349-daf93de7531f" />


<h3 align="center">4. Lambda Test Execution Output</h3>

> This screenshot confirms that the Lambda function was deployed correctly and is running using the container image that was uploaded to Amazon ECR through the pipeline.
<img width="3024" height="1408" alt="image" src="https://github.com/user-attachments/assets/27cc3145-3ec1-4d25-b816-1d728c5202ca" />

***

<h2>⚙️ Setup and Execution</h2>

<h3 align="left">Prerequisites on Jenkins Agent</h3>

### ✅ Jenkins Agent Prerequisites

Before running the pipeline, ensure the Jenkins build environment includes the following:

- A functional **Jenkins server** with pipeline support enabled  
- Installed and configured **AWS CLI** and **Terraform** tooling  
- **Docker Engine** installed and the daemon actively running  
- An AWS IAM role or user with permission to access:  
  * ECR, Lambda, S3, RDS & Glue services  
- Stored **AWS credentials** inside Jenkins Credentials Manager under the ID: `aws-credential-id`  
  *(Used by the pipeline to authenticate into AWS)*  

---

<h3 align="left">🚀 Executing the CI/CD Pipeline</h3>

1️⃣ Navigate to the Jenkins dashboard and create a **New Item** → select **Pipeline**  
2️⃣ Under configuration, choose **Pipeline script from SCM**  
3️⃣ Set **SCM** to **Git** and provide this repository URL:  
   `https://github.com/CodeOfGodMaster/DevOps_Assign_1.git`  
4️⃣ Define the branch specifier as: `main`  
5️⃣ Save the configuration and click **Build Now** to trigger execution  

---

Once triggered, the pipeline will:

- Clone the code from GitHub
- Run Terraform in a two-phased deployment
- Build + push the container image into **Amazon ECR**
- Deploy the **AWS Lambda** function using the pushed image

The Jenkins job will fetch the latest code and run all four pipeline stages, seamlessly handling both infrastructure provisioning and application deployment.

<h4>Subnet Groups Snapshot:</h4>
> This screenshot verifies that the RDS subnet group was successfully provisioned, providing the necessary networking configuration for the database within the designated VPC subnets.
<img width="3024" height="1356" alt="image" src="https://github.com/user-attachments/assets/f647050c-5f11-4a2e-b971-321c4ed22bed" />

<h5>IAM Roles Snapshot:</h5>
> This screenshot confirms that the IAM execution role was successfully created and assigned the necessary permissions to allow the pipeline and Lambda function to interact securely with all required AWS services.
<img width="1919" height="951" alt="<img width="2996" height="1270" alt="image" src="https://github.com/user-attachments/assets/adad6f34-e45e-4bb4-8410-4f5c6cfea9b1" />

<h6>Databases Snapshot:</h6>
> This screenshot verifies that the RDS PostgreSQL instance has been successfully deployed and is operational within the appropriate subnet group configured through Terraform.
<img width="3024" height="1266" alt="image" src="https://github.com/user-attachments/assets/5bb2234a-c174-46f9-9b43-6ae34c8c4de1" />

<h7>Jenkins Pipeline Console Output:</h7>
> This screenshot verifies that the Jenkins pipeline executed successfully, automating the entire CI/CD process including image build, deployment, and infrastructure provisioning.
<img width="3022" height="1964" alt="image" src="https://github.com/user-attachments/assets/0af80a55-854d-4dd4-9011-6897b9ae1c8b" />

