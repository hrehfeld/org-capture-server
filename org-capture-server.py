from fastapi import FastAPI, Request
import subprocess
from urllib.parse import quote, unquote
from pprint import pprint
import pathlib
import urllib
import os

HOST = "127.0.0.1"
PORT = 8987
user_password = pathlib.Path('password.txt').read_text().strip()

app = FastAPI()

def print_bookmarklet():
    bookmarklet = pathlib.Path('bookmarklet.js').read_text()
    repls = {
        os.linesep: ' ',
        '{HOST}': f"{HOST}:{PORT}",
        '{PASSWORD}': user_password,
    }
    for args in repls.items():
        bookmarklet = bookmarklet.replace(*args)
    return bookmarklet


def convert_html_to_org(html_string: str):
    # Set up the pandoc command
    pandoc_command = ["pandoc", "-f", "html", "-t", "org"]

    # Call pandoc to convert HTML to Org-mode
    result = subprocess.run(pandoc_command, input=html_string, text=True, capture_output=True)

    # Return the converted string or raise an error if pandoc failed
    if result.returncode != 0:
        raise Exception(f"Pandoc error: {result.stderr}")

    return result.stdout

@app.get("/capture")
async def capture(password: str, template: str, url: str, title: str, body: str, request: Request):
    if user_password != password:
        return { "error": 'wrong password' }
    body_key = 'body'
    keys = 'template','url','title', body_key
    values = template, url, title, body
    args = dict(zip(keys, [v.strip() for v in values]))
    pprint(args)
    body = args.get(body_key)
    if body:
        args[body_key] = convert_html_to_org(body).strip()
    pprint(args)
    #args = {k: quote(v) for k, v in args.items() if v}
    pprint(args)
    args = urllib.parse.urlencode(args, doseq=True)
    if args:
        cmd = ['xdg-open', f"org-protocol://capture?" + args]
        print(cmd)
        subprocess.run(cmd, check=True)
    return {"message": "Command executed"}

if __name__ == "__main__":
    print(f''' here's the chrome bookmarklet:

{print_bookmarklet()}
''')
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
