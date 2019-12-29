const express = require('express');
const cookieParser = require('cookie-parser');
const logger = require('morgan');
const bodyParser = require('body-parser');
const cors = require('cors');
const helmet = require('helmet');
const mysql = require('mysql');
const http = require('http');

/* CREATE APP */

var app = express();

app.use(express.json());
app.use(cookieParser());
app.use(logger('dev'));
app.use(bodyParser.json())
app.use(cors())
app.use(helmet())
app.use(express.urlencoded({ extended: true }));
app.set('port', 3000);

/* ROUTER */

var api = require('./routes/api');
app.use('/api', api);

/* DATABASE CONNECTION */

var db = mysql.createConnection({
    host: '',
    user: '',
    password: '',
    database: ''
});

db.connect((error, res) => {
    if (error) {
        console.log('Failed to Connect to the DB');
        next(error)
    }
    console.log('Successfully Connected to the DB');
    global.db = db;
});

/* START SERVER */

var server = http.createServer(app);
server.listen(3000);