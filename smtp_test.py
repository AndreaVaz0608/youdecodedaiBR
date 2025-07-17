import smtplib

EMAIL = "youdecoded.ai@youdecodedai.online"
PASSWORD = "suce$$o@2025AmAvPj"  # coloque aqui sua senha real da Hostinger

try:
    server = smtplib.SMTP_SSL("smtp.hostinger.com", 465)
    server.ehlo()
    server.login(EMAIL, PASSWORD)
    print("✅ Login bem-sucedido!")
    server.quit()
except smtplib.SMTPAuthenticationError as e:
    print("❌ Erro de autenticação:", e)
except Exception as e:
    print("⚠️ Outro erro ocorreu:", e)
