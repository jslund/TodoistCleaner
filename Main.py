import os
from datetime import datetime, timezone
from todoist import TodoistAPI
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP
today = datetime.now(timezone.utc)

def TaskFetcher(api):




    tasks = api.items.all()

    old_tasks = []

    for task in tasks:
        date_added = task['date_added']
        date_added = datetime.strptime(date_added, '%a %d %b %Y %H:%M:%S %z')
        time_gap = today - date_added
        if time_gap.days>7:
            old_tasks.append(task)

    return old_tasks

def MailSender(old_tasks):
    my_addr = os.getenv('MY_EMAIL')
    mail_pw = os.getenv('MAIL_PW')

    message_html = "<h2>Todays old tasks are:<h2><br><ul>"
    message_plain = "Todays old tasks are\r\n\n"

    for task in old_tasks:
        message_html += "<li>{}</li><br>".format(task.data['content'])
        message_plain += "{} \r\n".format(task.data['content'])

    message_html += "</ul>"

    msg = MIMEMultipart('alternative')
    msg['From'] = my_addr
    msg['To'] = my_addr
    msg['Subject'] = "Old tasks for {}".format(str(datetime.today()))

    msg.attach(MIMEText(message_plain,'plain'))
    msg.attach(MIMEText(message_html,'html'))


    text = msg.as_string()
    server = SMTP('smtp.gmail.com','587')
    server.starttls()
    server.login(my_addr, mail_pw)
    server.sendmail(my_addr, my_addr, text)
    server.quit()


if __name__ == '__main__':
    api = TodoistAPI(os.getenv('API_KEY'))
    old_tasks = TaskFetcher(api)
    MailSender(old_tasks)
    for task in old_tasks: task.delete()
    api.commit()

print("break")