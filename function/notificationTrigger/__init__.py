import logging
import os

import azure.functions as func
import psycopg2
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def main(msg: func.ServiceBusMessage):
    notification_id = int(msg.get_body().decode('utf-8'))
    logging.info('Python ServiceBus queue trigger processed message: %s', notification_id)

    postgres_url = os.getenv('TECHCONF_DB_URL')
    postgres_db = os.getenv('TECHCONF_DB_NAME')
    postgres_user = os.getenv('TECHCONF_DB_USER')
    postgres_pw = os.getenv('TECHCONF_DB_PW')
    postgres_port = "5432"
    admin_email_address = os.getenv('ADMIN_EMAIL_ADDRESS')
    sendgrid_api_key = os.getenv('SENDGRID_API_KEY')

    try:
        db_conn = psycopg2.connect(host=postgres_url,
                                   port=postgres_port,
                                   dbname=postgres_db,
                                   user=postgres_user,
                                   password=postgres_pw)
        cursor = db_conn.cursor()
        cursor.execute(f'SELECT message, subject FROM notification WHERE id = {notification_id}')
        notification = cursor.fetchone()
        message = notification[0]
        subject = notification[1]

        cursor.execute('SELECT email, first_name, last_name FROM attendee')
        attendees = cursor.fetchall()
        send_grid = SendGridAPIClient(sendgrid_api_key)

        for attendee in attendees:
            email_from = admin_email_address
            email_to = attendee[0]
            first_name = attendee[1]
            email_subject = f'{first_name}, {subject}'

            try:
                send_grid.send(Mail(email_from, email_to, email_subject, message))
            except Exception as error:
                logging.error(f'Send email failed: {error}')

        status = f'Attendees Notified: {len(attendees)}.'
        cursor.execute('UPDATE notification SET completed_date = CURRENT_DATE, status = %s WHERE id = %s',
                       (status, notification_id))

        db_conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
    finally:
        if db_conn:
            cursor.close()
            db_conn.close()
