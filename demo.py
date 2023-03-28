import re

from sanic import Sanic
import sanic.response
import task5

search_page = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>True google</title>
</head>
<body>
<form action="/search">
    <input type="text" name="query"/>
    <input type="submit" value="Искать"/>
</form>
</body>
</html>
"""

ans_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>True google</title>
</head>
<form action="/search">
    <input type="text" name="query"/>
    <input type="submit" value="Искать"/>
</form>
<body>
<ul>
{body}
</ul>
</body>
</html>
"""

a_template = """
<li><a href="/page?page={page}">{page}</a> tf_idf = {tf_idf}</li>
"""


app = Sanic("MyHelloWorldApp")


@app.get("/")
async def index_page(request):
    return sanic.response.html(search_page)


@app.get("search")
async def search(request):
    q = request.args['query'][0]
    results = task5.process_query(q)
    result_list = "\n".join([a_template.format(page=key, tf_idf=val) for key, val in results.items()])
    body = ans_template.format(body=result_list)
    return sanic.response.html(body)


@app.get("page")
async def get_page(request):
    q = request.args['page'][0]
    q = re.sub('.txt', '.html', q)
    print(q)
    result = ""
    with open("pages/" + q) as file:
        lines = file.readlines()
        for line in lines:
            result += line
    return sanic.response.html(result)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
