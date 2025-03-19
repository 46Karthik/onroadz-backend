
import boto3
import base64
from botocore.exceptions import NoCredentialsError
from django.conf import settings 
import jwt 



def return_response(statuscode, message, data=None):
    if data is not None:
        return {
            'status': statuscode,
            'message': message,
            'data': data
        }
    else:
        return {
            'status': statuscode,
            'message': message
        }


def upload_image_to_s3(file, path,content_type):
    # Initialize the boto3 S3 client
    s3_client = boto3.client(
        's3',
        aws_access_key_id="AKIASVLKCSQKD2K2ZK7L",
        aws_secret_access_key="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",
        region_name="ap-south-1"
    )
    try:
        # Upload the file to the specified folder in the S3 bucket
        s3_client.upload_fileobj(
            file,
            "rodezs3", 
            f"{path}/{file.name}",  
            ExtraArgs={
                "ContentType": content_type  
            }
        )

        # Construct the file URL
        file_path = f"{path}/{file.name}"

        return file_path

    except NoCredentialsError:
        print("Invalid AWS credentials")
        return "error"

    except Exception as e:
        print(f"Error: {str(e)}")
        return f"Error: {str(e)}"

def Decode_JWt(auth_header):
    token = auth_header.split(" ")[1]
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    return payload
