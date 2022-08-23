const http = require('http');
const fs = require('fs');

var filename = "test.html";
//var stream = fs.createWriteStream(filename);

var html = '<html lang="es"><head>\
<meta charset="utf-8" />\
<meta name="viewport" content="width=device-width, initial-scale=1">\
</head>\
<body><h1> Últimos datos recibidos:</h1>\
<table id="data_table" >\
<tr> <th> Variable </th> <th> Valor</th> <th> Unidad</th></tr>';

srvr = http.createServer((request, response) => {
    const { headers, method, url } = request;
    console.log(request.url);
    let body=[];
    request.on('error', (err) => {
        console.error(err);
        }).on('data', (chunk) => {
            body.push(chunk);
        }).on('end', () => {
            body = Buffer.concat(body).toString();
            // At this point, we have the headers, method, url and body, and can now
            // do whatever we need to in order to respond to this request.

            console.log(headers, body, url);
            if (request.method === 'PUT'){
                if (request.url === '/insta') {
                    bodyJson = JSON.parse(body);
                    console.log(bodyJson);
                    html2='';
                    html2 += "<tr>";
                    html2 += "<td> Fecha </td>";
                    html2 += "<td>" + bodyJson["date"] + "</td>";
                    html2 += "<td> GMT </td>";
                    html2 += "<tr>"
                    for (const prop in bodyJson["data"]){
                        html2 += "<tr>";
                        html2 += "<td>" + prop +"</td>";
                        html2 += "<td>" + bodyJson["data"][prop] + "</td>";
                        html2 += "<td>" + bodyJson["units"][prop] + "</td>";
                        html2 += "<tr>"
                    }
                    html2 += "</table></body></html>"
                    fs.writeFile( filename, html+html2, function (err){
                        if (err){
                            console.log(err);
                        } else{
                            console.log('saved!');
                        }
                    });
                    response.statusCode = 201;
                    response.setHeader('Content-Location', '/nuevo.json');
                    response.end();
                } else if (request.url.split('/')[1] === 'hist'){
                    name_csv = request.url.split('/')[2];
                    console.log('csv name:', name_csv);
                    fs.writeFile( name_csv, body, function (err){
                        if (err){
                            console.log(err);
                        } else{
                            console.log('saved!');
                            response.statusCode = 200;
                            response.end();

                        }
                    });
                } else{
                    response.statusCode = 404;
                    response.end();
                }
            } else {
                response.statusCode = 404;
                response.end();
            }
        });
});
srvr.listen(8080, '192.168.50.254');
srvr.timeout = 1500;
console.log('timeout:', srvr.timeout);
