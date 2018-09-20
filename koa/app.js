"use strict";


const Koa = require("koa")
const app = new Koa();

app.use(async (ctx, next) => {
    ctx.set("Content-Type", "text/html; charset=utf-8");
    ctx.body = "<html><h1>rps test</h1></html>";
});

app.listen(3000);
