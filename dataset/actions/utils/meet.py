def get_google_auth_url(user_id):
    # tbdemily
    # - cache user_id within the oauth url, to be returned when oauth redirects back to our server
    return "https://accounts.google.com/o/oauth2/v2/auth"


def create_meeting(credentials, guest_emails, start_date, end_date):
    # tbdemily
    return {"link": "https://meet.google.com/vix-uaxv-hcx"}
