'use strict';

const mysql = require('mysql');
const Redis = require('ioredis');
const multiparty = require('multiparty');
const querystring = require('querystring');

const ConfigParser = require('configparser');
const config = new ConfigParser();
config.read('my.cnf');

let redis = new Redis('//localhost:6379');
let pool = mysql.createPool({
    connectionLimit: 100,
    host: config.get('client', 'host'),
    port: config.get("client", "port"),
    user: config.get("client", "user"),
    password: config.get("client", "password"),
    db: config.get("client", "db"),
    charset: config.get("client", "charset")
});

const Koa = require('koa')
const app = new Koa();

async function parseForm(req) {
    return new Promise((rs, rj) => {
        let length = 0, form = new multiparty.Form();

        // Errors may be emitted
        // Note that if you are listening to 'part' events, the same error may be
        // emitted from the `form` and the `part`.
        form.on('error', function(err) {
          console.log('Error parsing form: ' + err.stack);
        });

        // Parts are emitted when parsing the form
        form.on('part', function(part) {
          // You *must* act on the part by reading it
          // NOTE: if you want to ignore it, just call 'part.resume()'

          if (!part.filename) {
            // filename is not defined when this is a field and not a file
            //console.log('got field named ' + part.name);

            // ignore field's content
            part.resume();
          }

          if (part.filename) {
            // filename is defined when this is a file
            //console.log('got file named ' + part.name);

            part.on('data', function(data) {
                //console.log('File [' + part.name + '] got ' + data.length + ' bytes');
                length += data.length;
            });

            part.on('end', function(data) {
                //console.log('File [' + part.name + '] Finished');
                rs(length);
            });
          }

          part.on('error', function(err) {
            // decide what to do
          });
        });

        // Close emitted after form parsed
        form.on('close', function() {
          //console.log('Upload completed!');
        });

        // Parse req
        form.parse(req);
    });
}

async function parseBody(ctx) {
    return new Promise((rs, rj) => {
        let buf = Buffer.alloc(ctx.request.length);
        let received = 0;

        ctx.req.on("data", (chunk) => {
            let copied = chunk.copy(buf, received);
            received += copied;
        });

        ctx.req.on("end", () => {
            rs(querystring.parse(buf.toString()));
        }); 
    });
}

async function query(sql) {
    return new Promise((rs, rj) => {
        pool.getConnection((err, connection) => {
            connection.query(sql, (err, results, fields) => {
                connection.release();
                rs([results, fields]);
            })
        })
    });
}


let responses = {};
app.use(async (ctx, next) => {
    ctx.set('Content-Type', 'text/plain; charset=utf-8');

    if (ctx.url === '/form') {
        ctx.body = await parseForm(ctx.req);

    } else if (ctx.url === '/redis') {
        let key = (await parseBody(ctx)).key;

        await redis.set(key, 'hello redis');
        ctx.body = await redis.get(key);

    } else if (ctx.url === '/mysql') {
        let sql = (await parseBody(ctx)).sql;
        let [results, fields] = await query(sql);

        ctx.body = results[0][fields[0].name]

    } else {
        let msize = parseInt(ctx.url.slice(1));

        if (!responses[msize]) {
            responses[msize] = Buffer.alloc(msize, 'X');
        }

        ctx.body = responses[msize]
    } 
});

app.listen(3000);
