def get_google_auth_url(user_id):
    # #tbdemily
    # - create a webhook for oauth server redirect in dataset/connectors/telegram.py
    # - pass the url to this webhook in the below auth url (use get_host_url utility to get the full url with host name)
    # - cache user_id within the below oauth url
    # - in the webhook in dataset/connectors/telegram.py, set the incoming cached user_id as the sender_id
    # - in the webhook, trigger the intent /EXTERNAL_doctor_signup_google_authenticated{"credentials"="CREDS_FROM_GOOGLE"}
    return "https://accounts.google.com/o/oauth2/v2/auth"


def create_meeting(credentials, guest_emails, start_date, end_date):
    # #tbdemily - create the google meet meeting using these credentials
    # - these credentials are same as those passed from webhook (see get_google_auth_url)
    return {"link": "https://meet.google.com/vix-uaxv-hcx"}
