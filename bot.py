import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters
import yagmail
import asyncio
import re
import pandas as pd
import numpy as np
import re
import wordsegment
from wordsegment import load, segment
load()
import fasttext
model = fasttext.load_model("name_gender_model.bin")



TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
EMAIL_SENDER = "mahmoudg3.141@gmail.com"
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = "mg1488@fayoum.edu.eg"

PDF_FILENAME = "resume.pdf"  # The existing PDF file in the current directory

def get_greeting(input):
    

    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    hr_keywords=['recruitment','career','talent','jobs','staff','hiring','hr','info','team','intern']
    email = re.search(email_pattern, input).group()  
    username=email.split('@')[0]
    for keyword in hr_keywords:
        if keyword in username.lower():
            return 'To whom it may concern'
            
    first_name=segment(username)[0]
    label, confidence = model.predict(first_name)
    gender=label[0].replace('__label__', '')
    pronouns={'Male':'Dear Mr. ','Female':'Dear Ms. '}
    greeting=pronouns[gender]+first_name
    
    return greeting
    
async def send_email(subject, body, attachment):
    """Sends an email with the generated message and a PDF attachment."""
    yag = yagmail.SMTP(EMAIL_SENDER, EMAIL_PASSWORD)
    yag.send(to=EMAIL_RECEIVER, subject=subject, contents=body, attachments=attachment)

async def process_message(update: Update, context):
    """Handles incoming messages from Telegram."""
    msg = update.message.text
    title=re.search(r'title:.+',msg).group().replace('title: ','')
    greeting=get_greeting(msg)
    email_body = f'''{greeting},
Attached to this email, my resume for the position of {title}

I look forward to meeting you to discuss how can I be of value to your organization. 

Best regards,

Mahmoud Gamal'''

    if not os.path.exists(PDF_FILENAME):
        await update.message.reply_text("Error: PDF file not found!")
        return

    await send_email(f"Application for {title}", email_body, PDF_FILENAME)
    await update.message.reply_text(f"Email sent for '{title}' with attached PDF!")

def main():
    """Start the bot using the new Application-based approach."""
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_message))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
