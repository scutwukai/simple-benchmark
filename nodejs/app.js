"use strict";

const multiparty = require("multiparty");

const Koa = require("koa")
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
          // NOTE: if you want to ignore it, just call "part.resume()"

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

var responses = {};
app.use(async (ctx, next) => {
    ctx.set("Content-Type", "text/plain; charset=utf-8");

    if (ctx.url === "/form") {
        ctx.body = await parseForm(ctx.req);

    } else {
        let msize = parseInt(ctx.url.slice(1));

        if (!responses[msize]) {
            responses[msize] = Buffer.alloc(msize, "X");
        }

        ctx.body = responses[msize]
    } 
});

app.listen(3000);
