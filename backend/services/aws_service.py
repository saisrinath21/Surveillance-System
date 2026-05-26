import boto3
from botocore.exceptions import NoCredentialsError
import os
from dotenv import load_dotenv
from datetime import datetime
import cv2
import io

load_dotenv()


# WHATSAPP_NUMBER = os.getenv('WHATSAPP_NUMBER')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_S3_BUCKET = os.getenv('AWS_S3_BUCKET')
AWS_S3_REGION = os.getenv('AWS_S3_REGION')


def upload_image_to_s3(frame_or_path):

    s3 = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_S3_REGION
    )

    try:
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"alert_frame_{timestamp}.jpg"

        if isinstance(frame_or_path, str):

            # Upload local file
            with open(frame_or_path, 'rb') as f:

                s3.upload_fileobj(
                    f,
                    AWS_S3_BUCKET,
                    filename,
                    ExtraArgs={
                        'ContentType': 'image/jpeg'
                    }
                )

        else:

            # Upload OpenCV frame
            _, buffer = cv2.imencode('.jpg', frame_or_path)

            image_bytes = io.BytesIO(buffer.tobytes())

            s3.upload_fileobj(
                image_bytes,
                AWS_S3_BUCKET,
                filename,
                ExtraArgs={
                    'ContentType': 'image/jpeg'
                }
            )

        url = f"https://{AWS_S3_BUCKET}.s3.{AWS_S3_REGION}.amazonaws.com/{filename}"

        return url

    except NoCredentialsError:
        raise Exception("AWS credentials not available.")

    except Exception as e:
        raise Exception(f"Failed to upload to S3: {str(e)}")