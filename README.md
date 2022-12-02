# CloudComputing-FinalProject
 This is a repository for the cloud computing final project, this is for use before (or linking to) the automated build processes (CDK or CodeStar).

## Authors
The idea and initial implementation comes from Albert!

Albert Li, Matthew Harper, Daniel Tod, and Artyom Martirosyan. 

## Project

A web interface and a data repository where game players can submit and share their games as well as access games others shared. AWS resources involved include but not limit to Cloudformation, DynamoDB, Lambda, IAM Role, IAM Policy etc..

Implementation description: 
* A DynamoDB table to store user input
* A lambda function to 
   * read user input, 
   * write user input to DynamoDB
   * display DynamoDB data to the website
* Cloudformation 
   * create the DynamoDB table
* Launching script
   * create the cloudformation
   * display cloudformation
   * Create lambda execution role 
   * create policies to grant lambda function permission to read and write to the database 
   * Attach policies to the role
   * Create deployment package
   * Launch lambda function
   * Generate lambda function url
   * Assign public access to function url
 * Cleaning script
   * Delete the cloudformation stack
   * Detach policy from the role
   * Remove lambda role
   * Delete deployment package
   * Delete lambda function




