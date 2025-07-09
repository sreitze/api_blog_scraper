import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

def create_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(creds)

    timestamp = datetime.datetime.now().isoformat()
    sheet = client.create(f"BlogPosts_{timestamp}")
    worksheet = sheet.sheet1

    worksheet.append_row(["Titular", "Categoría", "Autor", "Tiempo de lectura", "Fecha de publicación"])

    sheet.share(None, perm_type="anyone", role="reader") 

    sheet_url = sheet.url.replace("/edit#gid=0", "")
    return sheet_url, worksheet