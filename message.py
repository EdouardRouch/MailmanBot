import datetime

class Message:
    def __init__(self, subject: str, from_addr: str , date: datetime, body: str):
        self.subject = subject
        self.from_addr = from_addr
        self.date = date
        self.body = body
    
    # METHODS
    def get_subject(self):
        return self.subject
    
    def get_from(self):
        return self.from_addr

    def get_date(self):
        return self.date

    def get_body(self):
        return self.body

    # method used for testing
    # def to_string(self):
    #     print("subject: ", self.getSubject())
    #     print("from_addr: ", self.getFrom())
    #     print("date: ", self.getDate())
    #     print("body: \n ", self.getBody())


    def set_subject(self, subject: str):
        self.subject = subject

    def set_from(self, from_addr: str):
        self.from_addr = from_addr

    def set_date(self, date: datetime):
        self.date = date

    def set_body(self, body: str):
        self.body = body
