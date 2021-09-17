import discord
from discord.ext import tasks
from discord.ext import commands
from dotenv import load_dotenv
import os
import imap
import locale
from datetime import datetime
from message import Message
load_dotenv(dotenv_path="config")


class MailmanBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=os.getenv('COMMAND_PREFIX'))
        self.help_command = None
        # default channel on which the bot will display new emails
        self.default_channel = None
        # the last emails that arrived
        self.last_email = None

    

    # METHODS

    def get_default_channel(self):
        return self.default_channel

    def get_last_email(self):
        return self.last_email


    # COMMANDS
    async def on_ready(self):
        self.set_default_channel(int(os.getenv('DEFAULT_CHANNEL')))
        await self.get_default_channel().send(os.getenv('GREETINGS_SENTENCE'))
        self.display_email_loop.start()


    def set_default_channel(self, channel: int):
        self.default_channel = self.get_channel(channel)


    def set_last_email(self, msg: Message):
        self.last_email = msg

    # display the Message list "msg_list" in "channel"
    async def display_email(self, msg_list: list, channel):
        await channel.send(os.getenv('NEW_EMAIL_SENTENCE'))

        for msg in msg_list:
            self.set_last_email(msg)
            await channel.trigger_typing()

            # define the local language for displaying the date
            # change the value of "LOCAL_TIME" to your needs in the config file
            loc = os.getenv('LOCAL_TIME')
            locale.setlocale(locale.LC_TIME, loc)
            # turn datetime format into string format
            date = datetime.strftime(msg.get_date(), os.getenv('DATE_DISPLAY_FORMAT'))
            subject = msg.get_subject()
            from_addr = msg.get_from()
            body = msg.get_body()

            # display the string in the channel chat
            await channel.send(os.getenv('EMAIL_DISPLAY_FORMAT').format(
                                date, from_addr, subject, body))


    # checks for new emails at "LOOP_TIME" minutes interval
    # change the value of "LOOP_TIME" to your needs in the config file
    @tasks.loop(minutes=int(os.getenv('LOOP_TIME')))
    async def display_email_loop(self):
        channel = self.get_default_channel()
        message_list = imap.retrieve()

        if len(message_list) != 0:
            await self.display_email(message_list, channel)



bot = MailmanBot()


@bot.command(name="last")
async def display_last_email(ctx):
    last = bot.get_last_email()
    if last != None:
        await bot.display_email([last], ctx.channel)
    else:
        await ctx.send(os.getenv('NO_EMAIL_SENTENCE'))
    

@bot.command(name="mail")
async def mail(ctx):
    message_list = imap.retrieve()
    if len(message_list) == 0:
        await ctx.trigger_typing()
        await ctx.send(os.getenv('NO_EMAIL_SENTENCE'))
    else:
        await bot.display_email(message_list, ctx.channel)


@bot.command()
async def help(ctx):
    await ctx.send(os.getenv('HELP'))


bot.run(os.getenv('TOKEN'))