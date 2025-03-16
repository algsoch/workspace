# Deploying Vicky Hair Salon Management System to Vercel

This guide provides step-by-step instructions for deploying the Vicky Hair Salon Management System to Vercel.

## Prerequisites

- A Vercel account (https://vercel.com)
- Git repository with your project
- Node.js and npm installed (for Vercel CLI)
- AWS account (if using S3 for storage)

## Deployment Steps

### 1. Prepare Your Project

1. Ensure all dependencies are listed in `requirements.txt`:
   ```
   flask==2.0.1
   flask-cors==3.0.10
   pandas==1.3.3
   werkzeug==2.0.1
   gunicorn==20.1.0
   python-dotenv==0.19.0
   boto3==1.24.0  # If using S3 for storage
   ```

2. Make sure `vercel.json` is properly configured:
   ```json
   {
     "version": 2,
     "builds": [
       {
         "src": "app.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "/app.py"
       }
     ],
     "env": {
       "FLASK_ENV": "production"
     }
   }
   ```

3. If using S3 for storage, modify your application to use the S3Handler instead of CSVHandler:
   ```python
   # In app.py, replace:
   from src.utils.csv_handler import CSVHandler
   csv_handler = CSVHandler()
   
   # With:
   from src.utils.s3_handler import S3Handler
   csv_handler = S3Handler()
   ```

4. Commit all changes to your Git repository.

### 2. Deploy to Vercel

1. Install Vercel CLI:
   ```
   npm i -g vercel
   ```

2. Login to Vercel:
   ```
   vercel login
   ```

3. Deploy the project:
   ```
   vercel
   ```

4. Follow the prompts to complete the deployment:
   - Select your Vercel scope/account
   - Confirm the project name
   - Specify the directory to deploy (usually the root of your project)
   - Confirm deployment settings

### 3. Configure Environment Variables

After deployment, set up the necessary environment variables in the Vercel dashboard:

1. Go to your project in the Vercel dashboard
2. Navigate to Settings > Environment Variables
3. Add the following variables:
   - `SECRET_KEY`: A secure random string for Flask session security
   - `S3_BUCKET_NAME`: Your S3 bucket name (if using S3)
   - `AWS_ACCESS_KEY_ID`: Your AWS access key (if using S3)
   - `AWS_SECRET_ACCESS_KEY`: Your AWS secret key (if using S3)
   - `AWS_REGION`: Your AWS region (if using S3)

### 4. Set Up S3 Bucket (If Using S3 for Storage)

1. Create an S3 bucket in your AWS account:
   - Go to AWS Management Console > S3
   - Click "Create bucket"
   - Enter a unique bucket name
   - Configure bucket settings (public access, versioning, etc.)
   - Create the bucket

2. Set up CORS configuration for your bucket:
   ```json
   [
     {
       "AllowedHeaders": ["*"],
       "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
       "AllowedOrigins": ["https://your-vercel-app-url.vercel.app"],
       "ExposeHeaders": []
     }
   ]
   ```

3. Create an IAM user with programmatic access and attach the AmazonS3FullAccess policy (or a more restricted custom policy).

4. Use the access key and secret key from this IAM user in your Vercel environment variables.

### 5. Test Your Deployment

1. Visit your deployed application at the URL provided by Vercel.
2. Log in with the default admin credentials:
   - Username: `admin`
   - Password: `admin123`
3. Test all functionality to ensure it works correctly.
4. Change the default admin password for security.

## Troubleshooting

### Common Issues

1. **Application Error or 500 Error**:
   - Check Vercel logs in the dashboard
   - Ensure all dependencies are correctly listed in requirements.txt
   - Verify environment variables are set correctly

2. **File Storage Issues**:
   - If using S3, check AWS credentials and bucket permissions
   - Verify S3 bucket name is correct
   - Check CORS configuration if experiencing API issues

3. **Authentication Issues**:
   - Ensure SECRET_KEY is set in environment variables
   - Check if users.csv is being created correctly

### Getting Help

If you encounter issues not covered in this guide:

1. Check the Vercel documentation: https://vercel.com/docs
2. Review the AWS S3 documentation: https://docs.aws.amazon.com/s3/
3. Open an issue in the project repository

## Maintenance

### Updating Your Deployment

To update your deployed application:

1. Make changes to your code
2. Commit changes to your Git repository
3. If using Vercel Git integration, the deployment will update automatically
4. If using Vercel CLI, run `vercel` again to deploy the updates

### Monitoring

Vercel provides basic monitoring and logs for your application:

1. Go to your project in the Vercel dashboard
2. Navigate to the "Deployments" tab to see all deployments
3. Click on a deployment to view details and logs

For more advanced monitoring, consider integrating with services like Sentry or New Relic.