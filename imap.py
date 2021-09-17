from imaplib import IMAP4_SSL
import email
from email.header import decode_header
from datetime import datetime
import locale
from message import Message
from dotenv import load_dotenv
import os

# connects to the IMAP_HOST using credentials defined in config file
def connect():
    load_dotenv(dotenv_path="config")
    imap_host = os.getenv('IMAP_HOST')
    imap_user = os.getenv('IMAP_USER')
    imap_pass = os.getenv('IMAP_PASS')

    imap = IMAP4_SSL(imap_host)

    # login to IMAP host
    imap.login(imap_user, imap_pass)
    return imap

# selects the IMAP_MAILBOX and search for emails matching criterions
def search():
    imap = connect()
    imap.select(os.getenv('IMAP_MAILBOX'))

    err, data = imap.search(None, os.getenv('IMAP_CRIT'))
    id_list = data[0].split()

    return imap, id_list

def retrieve():
    
    imap, id_list = search()

    message_list = []

    # for each email id we received
    for id in id_list:

        # fetching email's data
        typ, data = imap.fetch(id, '(RFC822)')
        msg = email.message_from_bytes(data[0][1])
        
        # decoding date, subject and from headers from the email
        date, encoding = decode_header(msg['Date'])[0]
        if isinstance(date, bytes):
            # if it's a bytes, decode to str
            if isinstance(encoding, str):
                date = date.decode(encoding)
        
        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            # if it's a bytes, decode to str
            if isinstance(encoding, str):
                subject = subject.decode(encoding)
            
        from_addr, encoding = decode_header(msg.get("From"))[0]
        if isinstance(from_addr, bytes):
            from_addr = from_addr.decode(encoding)

        locale.setlocale(locale.LC_TIME, "en_US.UTF-8")
        date = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %z")

        # create the Message Object
        message = Message(subject, from_addr, date, "")

        if msg.is_multipart():
            # iterate over email parts
            for part in msg.walk():
                # extract content type of email
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                try:
                    # get the email body
                    body = part.get_payload(decode=True).decode()
                except:
                    body = part.get_payload()
                    pass

                # store body if email have no attachment
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    # set the body of our message
                    message.set_body(body)
                
                # fetch the attached file and save it
                # I plan on developping this part later
                #
                # elif "attachment" in content_disposition:
                #     filename = part.get_filename()
                #     if filename:
                #         folder_name = Subject
        else:
            # extract content type of email
            content_type = msg.get_content_type()

            # get the email body
            try:
                body = msg.get_payload(decode=True).decode()
            except:
                body = msg.get_payload(decode=True).decode(encoding="ISO-8859-1")
                pass
            if content_type == "text/plain":

                # set the body of our message
                message.set_body(body)
        
        message_list.append(message)
    imap.close()
    imap.logout()  

    return message_list


