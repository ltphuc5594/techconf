import logging
import azure.functions as func
import psycopg2
import os
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def main(msg: func.ServiceBusMessage):
    notification_id = int(msg.get_body().decode('utf-8'))
    logging.info(
        'Python ServiceBus queue trigger processed message: %s', notification_id)

    POSTGRES_URL = os.getenv('TECHCONF_DB_URL')
    POSTGRES_USER = os.getenv('TECHCONF_DB_USER')
    POSTGRES_PW = os.getenv('TECHCONF_DB_PW')
    POSTGRES_DB = os.getenv('TECHCONF_DB_NAME')
    POSTGRES_PORT = "5432"
    ADMIN_EMAIL_ADDRESS = os.getenv('ADMIN_EMAIL_ADDRESS')
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')

    db_conn = psycopg2.connect(host=POSTGRES_URL, dbname=POSTGRES_DB,
                               user=POSTGRES_USER, password=POSTGRES_PW, port=POSTGRES_PORT)

    try:
        cursor = db_conn.cursor()
        cursor.execute(
            f"SELECT message, subject FROM notification WHERE id = {notification_id}")
        notification = cursor.fetchone()
        message = notification[0]
        subject = notification[1]

        cursor.execute("SELECT first_name, last_name, email FROM attendee")
        attendees = cursor.fetchall()
        send_grid = SendGridAPIClient(SENDGRID_API_KEY)

        for attendee in attendees:
            email_from = ADMIN_EMAIL_ADDRESS
            email_to = attendee[0]
            first_name = attendee[1]
            email_subject = f'{first_name}, {subject}'

            try:
                send_grid.send(
                    Mail(email_from, email_to, email_subject, message))
            except Exception as error:
                logging.error('Send email failed: ', error)

        status = f"Attendees Notified: {str(len(attendees))}."
        query = "UPDATE notification SET completed_date = CURRENT_DATE, status = %s WHERE id = %s"
        cursor.execute(query, (status, notification_id))

        db_conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
    finally:
        cursor.close()
        db_conn.close()
