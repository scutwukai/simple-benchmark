from vibora import Vibora, Request
from vibora.responses import Response

app = Vibora()
responses = dict()

@app.route('/<msize>', cache=False)
async def home(req: Request, msize: int):
    if msize not in responses:
        responses[msize] = b'X' * msize

    return Response(responses[msize], headers={'Content-Type': 'text/plain; charset=utf-8'})

@app.route('/form', methods=["POST"], cache=False)
async def home(req: Request):
    files = await req.files()
    content = await files[0].read()

    return Response(bytes(str(len(content)), "utf-8"), headers={'Content-Type': 'text/plain; charset=utf-8'})


if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=3000, workers=1)
