import os
import re
import pandas as pd



def check_email(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if re.fullmatch(regex, email):
        return True
    return False


def load_paid_emails():
    try:
        df = pd.read_csv('emails.csv')
        return df['email'].tolist()  # Assuming the column name is 'email'
    except FileNotFoundError:
        return []
