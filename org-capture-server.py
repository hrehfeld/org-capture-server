#!/bin/python3
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import subprocess
from urllib.parse import quote, unquote
from pprint import pprint
import pathlib
import urllib
import os
import shlex
import re

HOST = "127.0.0.1"
PORT = 8987
user_password = pathlib.Path('password.txt').read_text().strip()

app = FastAPI()


def format_command(cmd):
    return " ".join(shlex.quote(arg) for arg in cmd)


def print_bookmarklet():
    bookmarklet = pathlib.Path("bookmarklet.js").read_text()
    whitespace = re.compile("[\n\\s]+", re.MULTILINE)

    comments = re.compile(r"^\s*//.*$\n", re.MULTILINE)
    bookmarklet = comments.sub("", bookmarklet)

    bookmarklet = whitespace.sub(" ", bookmarklet)

    repls = {
        "{HOST}": f"{HOST}:{PORT}",
        "{PASSWORD}": user_password,
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


@app.get("/capture", response_class=HTMLResponse)
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
        cmd = ["xdg-open", f"org-protocol://capture?" + args]
        # for some reason my mimeo always opens the broken emacsclient.desktop
        cmd = ["emacsclient", "-c", f"org-protocol://capture?" + args]
        print(format_command(cmd))
        subprocess.run(cmd, check=True)
    # return {"message": "Command executed"}
    # a simple html5 webpage that just executes javascript back
    return f"""
<!DOCTYPE html>
<html>
    <head>
        <title>Org Capture</title>
    </head>
<body>
        <script>
            history.back();
        </script>
    <a href="javascript:history.back()">Go back</a>
</body>
    </html>"""

if __name__ == "__main__":
    print(f''' here's the chrome bookmarklet:

{print_bookmarklet()}
''')
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
