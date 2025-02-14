from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from madr.routes import auth, authors, books, users

app = FastAPI()


@app.get('/', response_class=HTMLResponse)
def hello():
    return HTMLResponse('<h1>Hello</h1>')


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(authors.router)
app.include_router(books.router)
