import os
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def send_email_notification(recipient_email, new_courses):
    SENDER = os.getenv('SENDER_EMAIL')
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    SUBJECT = "New Courses Found"

    client = boto3.client('ses', region_name=AWS_REGION)

    BODY_HTML = """
    <html>
    <head></head>
    <body>
      <h1>New Courses Found</h1>
      <table border="1" style="border-collapse: collapse;">
        <tr>
          <th style="padding: 8px; text-align: left;">Course Title</th>
          <th style="padding: 8px; text-align: left;">Category</th>
          <th style="padding: 8px; text-align: left;">Link</th>
          <th style="padding: 8px; text-align: left;">Release Time</th>
        </tr>
    """

    sorted_courses = sorted(new_courses, key=lambda x: x[4], reverse=True)  # Sort by release time in descending order

    for course in sorted_courses:
        BODY_HTML += f"""
        <tr>
          <td style="padding: 8px; text-align: left;">{course[0]}</td>
          <td style="padding: 8px; text-align: left;">{course[1]}</td>
          <td style="padding: 8px; text-align: left;"><a href="{course[2]}">{course[2]}</a></td>
          <td style="padding: 8px; text-align: left;">{course[3]}</td>
        </tr>
        """

    BODY_HTML += """
      </table>
    </body>
    </html>
    """

    try:
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    recipient_email,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': "UTF-8",
                        'Data': BODY_HTML,
                    },
                },
                'Subject': {
                    'Charset': "UTF-8",
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
        )
        print("Email notification sent successfully.")
    except (BotoCoreError, ClientError) as e:
        print(f"Failed to send email notification. Exception: {str(e)}")