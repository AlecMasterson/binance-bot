var express = require('express');
var cookieParser = require('cookie-parser');
var logger = require('morgan');
const bodyParser = require('body-parser');
const cors = require('cors');
const helmet = require('helmet');
var http = require('http');
var analyze = require('./routes/analyze')
var tradingModels = require('./routes/tradingModels')

var app = express();

app.use(express.json());
app.use(cookieParser());
app.use(logger('dev'));
app.use(bodyParser.json())
app.use(cors())
app.use(helmet())
app.use(express.urlencoded({ extended: true }));

app.use('/analyze', analyze);
app.use('/tradingModels', tradingModels);

app.set('port', 3000);
var server = http.createServer(app);
server.listen(3000);