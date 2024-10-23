import smtplib

sender = 'xyz@email.com'
receiver = 'test@email.com'

title = 'Grocery list'

body = 'Eggs, milk and lembas'

email = f'''from: {sender}
to: {receiver}
subject: {title}

{body}'''

smtp = smtplib.SMTP(host='localhost', port=25)
smtp.sendmail(from_addr=sender, to_addrs=receiver, msg=email)
