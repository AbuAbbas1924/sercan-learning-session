from fastapi import FastAPI
app = FastAPI()
print("---FastAPI started---")


@app.get('/')
def test():
    return {"test": "ok"} 