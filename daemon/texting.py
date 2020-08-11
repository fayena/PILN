import smtplib 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


#kiln texting code 
def text(segment, temp, status):
    print("inside text top")
    email = "alforddm@glorifyjesus.net"
    pas = "P9045acp"

    sms_gateway = '5806121635@tmomail.net'
    # The server we use to send emails in our case it will be gmail but every email$
    # and port is also provided by the email provider.
    smtp = "box.glorifyjesus.net" 
    port = 587
    # This will start our email server
    server = smtplib.SMTP(smtp,port)
    # Starting the server
    server.starttls()
    # Now we need to login
    server.login(email,pas)

    # Now we use the MIME module to structure our message.
    msg = MIMEMultipart()
    msg['From'] = email 
    msg['To'] = sms_gateway
     # Make sure you add a new line in the subject
    msg['Subject'] = "PILN Status"
    # Make sure you also add new lines to your body
    body = "The kiln segment is  %s, the temperture is %s, the status is %s" % (segment, temp, status)
    # and then attach that body furthermore you can also send html content.
    msg.attach(MIMEText(body, 'plain'))

    sms = msg.as_string()

    server.sendmail(email,sms_gateway,sms)
    print("text bottom")
    # lastly quit the server
    server.quit()
    return () 

#end kiln texting code
#segment = 3
#temp = 1000
#status = "running"
#text(segment, temp, status)
