
# AWS Project: Nvidia Stock Price Prediction

## Overview

This project aims to predict Nvidia's stock prices based on open, high, and low values using a machine learning model. The application is built with Flask and deployed on an AWS EC2 instance. Data is fetched daily through the Alpha Vantage API, and the model is retrained every four days. The project leverages various AWS services such as S3, Lambda, EventBridge, and more to manage data and model operations efficiently. A CI/CD pipeline is set up to automatically deploy the app on the EC2 instance whenever code is pushed to the GitHub main branch. Nginx and Gunicorn are used for serving the application.

## Project Structure



## Features
- Predict Nvidia stock close prices based on open, high, and low values.
- Displaying Nvidia stock market data.
- Daily data fetching through Alpha Vantage API.
- Model retraining every four days and stored in AWS S3.
- Deployment on AWS EC2 with Nginx and Gunicorn.
- CI/CD pipeline with GitHub Actions for automated deployments.
- Error logging and monitoring.

## Prerequisites
- AWS account with the following services set up: EC2, S3, Lambda, EventBridge.
- Alpha Vantage API key.
- GitHub account.



## General Steps
### 1. Create AWS Account and IAM User
Create an AWS account and IAM user with the following policies:
- `AmazonS3FullAccess`
- `AmazonEC2FullAccess`

### 2. Set Up EC2 Instance
- Launch an EC2 instance.
- Configure the Security Group by adding the following inbound rules:
  
  - SSH (port 22)

  - HTTP (port 80)

  - Custom TCP (port 8000)

- Create key pairs (RSA), download the `.pem` file, and associate it with the instance.
- Attach the IAM role to the EC2 instance.

### 3. Obtain Alpha Vantage API Key
Sign up for an Alpha Vantage API key from [Alpha Vantage](https://www.alphavantage.co/) and save it.

### 4. Create S3 Bucket
Create an AWS S3 bucket  to store your data and model files.


### 5. Set Up GitHub Secrets
Store the following secrets in your GitHub repository settings:

  - `SSH_EC2_KEY`: The private SSH key for your EC2 instance.
  - `API_KEY`: Your Alpha Vantage API key.( You may not need this since it will be integrated into Lambda Function environment later )
  - `SSH_EC2_USER`: The username for your EC2 instance (e.g., ec2-user).
### 6. Set Up GitHub Actions Workflow
- Create a deploy.yml file in your .github/workflows directory.

- Configure the workflow to deploy your app to the EC2 instance whenever you push to the main branch.
### 7. Configure Gunicorn and Nginx on EC2
- SSH into your EC2 instance.
- Install Gunicorn and Nginx.
- Configure Gunicorn to serve your Flask app.
- Configure Nginx as a reverse proxy to forward requests to Gunicorn.
### 8. Create a Lambda Function
- Create a Lambda function and add the code to fetch data from Alpha Vantage and save it in the S3 bucket.
- Configure the environment variables in the Lambda function to store the API key.
- Add the `AWSSDKPandas-Python39` layer to the Lambda function to recognize pandas.
- Create a role for the Lambda function with the following policies:
  - `AmazonS3FullAccess`
  - `AWSLambdaBasicExecutionRole`
### 9. Create a Scheduler with EventBridge
- Naviaget to EventBridge Service and create a Schedule and name it.
- Set the target to the Lambda function created in step 8.
- Configure the Schedule to run every day at 9 PM using the cron expression `0 21 ? * 2-6 *`.
### 10. Configure Cron on EC2 for Model Retraining
- SSH into your EC2 instance.
- Set up a cron job to run the train_model.py script every 4 days.
The script will:
- Fetch fresh data from S3 if the local data is outdated.
- Retrain the model.
- Save the updated model to S3 and the EC2 instance.
## Notes
- The EC2 instance has access to the S3 bucket to fetch and store data and model files.
- The Lambda function also has access to the S3 bucket to store the fetched data.
- The predict function in the app will use the model from the EC2 instance if it is up-to-date; otherwise, it will download the model from the S3 bucket.
