from __future__ import annotations
import imaplib, email, os, re
from email.header import decode_header
from .models import Job


def _subject(msg):
    raw=decode_header(msg.get('Subject',''))
    out=[]
    for part,enc in raw:
        out.append(part.decode(enc or 'utf-8',errors='ignore') if isinstance(part,bytes) else part)
    return ''.join(out)


def _text(msg):
    if msg.is_multipart():
        parts=[]
        for p in msg.walk():
            if p.get_content_type()=='text/plain' and not p.get_filename():
                try: parts.append(p.get_payload(decode=True).decode(p.get_content_charset() or 'utf-8',errors='ignore'))
                except Exception: pass
        return '\n'.join(parts)
    try: return msg.get_payload(decode=True).decode(msg.get_content_charset() or 'utf-8',errors='ignore')
    except Exception: return ''


def ingest_alert_emails(mailbox='INBOX', limit=50)->list[Job]:
    host=os.getenv('IMAP_HOST','imap.gmail.com'); user=os.getenv('IMAP_USER'); password=os.getenv('IMAP_PASSWORD')
    if not user or not password: return []
    M=imaplib.IMAP4_SSL(host); M.login(user,password); M.select(mailbox)
    typ,data=M.search(None,'UNSEEN'); ids=data[0].split()[-limit:]
    jobs=[]
    for mid in ids:
        typ,msgdata=M.fetch(mid,'(RFC822)')
        raw=msgdata[0][1]; msg=email.message_from_bytes(raw)
        subject=_subject(msg); text=_text(msg)
        if not re.search(r'job|jobs|career|position|role|opportunity|hiring', subject, re.I): continue
        url=re.search(r'https?://[^\s<>"]+', text)
        jobs.append(Job(job_id=f"email:{mid.decode()}",source='email',company='',title=subject,location='',workplace_type='unspecified',url=url.group(0) if url else '',apply_url=url.group(0) if url else '',description=text,posted_at=msg.get('Date'),raw={'subject':subject,'from':msg.get('From')}))
    M.close(); M.logout(); return jobs
