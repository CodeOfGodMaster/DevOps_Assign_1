<h1>📦 DevOps Engineer Assignment 1: S3 to RDS/Glue Data Pipeline CI/CD</h1>

This repository contains the complete solution for the DevOps Engineer Assignment, demonstrating a fully automated CI/CD pipeline for deploying a containerized data processing application to AWS using Jenkins and Terraform.

## 🎯 Project Problem and Requirements

This project was a response to a DevOps Engineering assignment that required building a complete, automated CI/CD pipeline for a data ingestion task on AWS.

### Problem Statement

The core requirement was to develop an application capable of reading data from an **S3 bucket**, attempting to insert that data into an **AWS RDS (PostgreSQL)** database, and if the RDS insertion failed or was not possible, to use a fallback mechanism to publish the data's metadata to an **AWS Glue Data Catalog** database.

### Assignment Requirements

1.  **Repository Creation:** Set up a GitHub repository to host all code.
2.  **Application Containerization:** Create a **Dockerfile** to build a container image for the application logic (`s3_to_rds_glue.py`).
    * **Application Logic:** The Python code must implement the S3 $\rightarrow$ RDS primary data flow with an S3 $\rightarrow$ Glue Data Catalog fallback.
3.  **AWS ECR Deployment:** Deploy the created Docker image to **AWS ECR**.
4.  **AWS Lambda Deployment:** Create a **Lambda function** that utilizes the container image from ECR and test its execution.
5.  **Automation (CI/CD):**
    * Use a **Jenkins CI/CD pipeline** for all deployment activities.
    * Use **Terraform** for the creation of all required AWS resources (ECR, S3, RDS, IAM roles, Lambda function, etc.). The pipeline must orchestrate the Terraform execution.
6.  **Documentation:** Provide screenshots of all output windows (Jenkins execution, Terraform resource creation, DB/Lambda verification) as proof of successful deployment.

***

<h2>🚀 Architecture and Process Flow</h2>

The CI/CD solution, orchestrated by Jenkins, uses a decoupled **Terraform deployment strategy** to resolve the critical circular dependency between the ECR repository creation and the Lambda function deployment.

The pipeline is structured into four main stages:

**Stage 1: Infra Prerequisites (Targeted Terraform Apply):** Creates foundational AWS resources (**ECR Repository, S3 Bucket, IAM Role, and RDS Subnet Group**), intentionally skipping the dependent Lambda function.

**Stage 2: Authenticate with AWS and ECR:** Performs Docker login authentication against the newly created ECR registry.

**Stage 3: Build & Push Docker Image:** Builds the application's container image, tags it, and pushes it to ECR.

**Stage 4: Final Deployment (Full Terraform Apply):** Executes the full Terraform configuration, which successfully creates the AWS Lambda function because its required ECR image is now available.

***

<h2>🛠️ Repository Contents</h2>

The project relies on four core files for infrastructure, application logic, and deployment:

* **Jenkinsfile (CI/CD Orchestration):** This Groovy script defines the multi-stage, dependency-aware pipeline execution logic.
* **main.tf (Infrastructure as Code):** This HCL file defines all required AWS resources, including ECR, RDS, Lambda, S3, and IAM roles.
* **s3\_to\_rds\_glue.py (Application Logic):** This Python script is designed to read data from S3, attempt a data insert to PostgreSQL RDS, and implement a fallback to Glue Data Catalog if the RDS operation is not possible.
* **Dockerfile (Containerization):** This file packages the application, installing necessary Python libraries (boto3, psycopg2-binary) onto a `python:3.9-slim` base image.

***

<h2>☁️ AWS Resources Deployed (us-east-1)</h2>

The Terraform configuration provisions the following key resources:

* **ECR Repository:** `s3-to-rds-glue-pipe` (Container Image Host)
* **S3 Bucket:** `rablo-bucket-pipe-2804` (Source Data Storage)
* **RDS Subnet Group:** `rablo-rds-pipe1-subnet-group` (Required for RDS instance)
* **RDS Instance:** PostgreSQL database instance
* **IAM Role:** `lambda-exec-role-pipe1` (Lambda Execution Role)
* **AWS Lambda:** `s3_to_rds_glue_lambda-pipe1` (Container-based application function)

***

<h2>✅ Deployment Proof (Screenshots)</h2>

Below are visual proofs confirming the end-to-end success of the CI/CD pipeline and the resulting infrastructure deployment.

<h3 align="center">1. Jenkins Successful Pipeline Execution</h3>

This image confirms that all four stages—from infrastructure creation to the final deployment—completed successfully.
<img width="1919" height="1031" alt="Screenshot 2025-10-07 230835" src="https://github.com/user-attachments/assets/0a6472f5-2a4f-4c42-94ff-e99aa857b38c" />



<h3 align="center">2. ECR Repository Verification</h3>

This shows the ECR repository was created by Terraform and the application image was successfully pushed by Docker in the pipeline.

<img width="1919" height="629" alt="Screenshot 2025-10-07 231011" src="https://github.com/user-attachments/assets/6d91bc77-c74c-4044-886b-fa713e986166" />

<h3 align="center">3. AWS Lambda Function Verification</h3>

Proof that the container-based Lambda function was created, referencing the ECR image URI.
<img width="1919" height="969" alt="Screenshot 2025-10-07 230907" src="https://github.com/user-attachments/assets/672009e6-1687-4d31-9708-5857c475c685" />

<h3 align="center">4. Lambda Test Execution Output</h3>

Output showing the Lambda function was tested and confirmed the S3 data processing and connection to RDS or Glue.
<img width="1919" height="920" alt="Screenshot 2025-10-07 194851" src="https://github.com/user-attachments/assets/f3dd9d70-8bbb-41c6-b604-f7b723100ea9" />

***

<h2>⚙️ Setup and Execution</h2>

<h3 align="left">Prerequisites on Jenkins Agent</h3>

The Jenkins build agent must have the following tools installed and configured:

* A running **Jenkins instance**.
* **AWS CLI** and **Terraform CLI**.
* **Docker** installed and running.
* A pre-configured **AWS IAM Role** with permissions for ECR, Lambda, S3, RDS, and Glue actions.
* An **AWS Credentials** entry in Jenkins named `aws-credential-id` for pipeline access.

<h3 align="left">Running the Pipeline</h3>

1.  In the Jenkins dashboard, create a **New Item** and select the **Pipeline** project type.
2.  In the pipeline configuration, choose **"Pipeline script from SCM"** (Git).
3.  Set the **Repository URL** to: `https://github.com/GaniDynamo/Devops_Engineer_Assignment1-Rablo-.git`
4.  Ensure the **Branch Specifier** is set to `main`.
5.  Save the configuration and click **Build Now**.

The Jenkins pipeline will automatically clone the repository and execute the four defined deployment stages, managing infrastructure and application deployment end-to-end.

<h4>IAM Roles Snapshot:</h4>
<img width="1919" height="951" alt="Screenshot 2025-10-07 230950" src="https://github.com/user-attachments/assets/c4501b41-4a21-44f3-9853-76a77d1333e3" />

<h5>Databases Snapshot:</h5>
<img width="1912" height="812" alt="Screenshot 2025-10-07 231343" src="https://github.com/user-attachments/assets/72960478-a49f-422b-aecf-76bc82c63cf9" />

<h6>Subnet Groups Snapshot:</h6>
<img width="1919" height="916" alt="Screenshot 2025-10-07 231827" src="https://github.com/user-attachments/assets/5f050a9d-dcb6-438d-97f1-3310731c896b" />

<h7>Jenkins Pipeline Console Output:</h7>
<img width="1919" height="978" alt="Screenshot 2025-10-07 230819" src="https://github.com/user-attachments/assets/de8aa6ed-d46e-4439-b449-955fe7763f58" />
