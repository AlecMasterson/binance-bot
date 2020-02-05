const express = require('express');
const cookieParser = require('cookie-parser');
const logger = require('morgan');
const bodyParser = require('body-parser');
const cors = require('cors');
const helmet = require('helmet');
const api = require('../routes/api');

const app = express();
app.use(express.json());
app.use(cookieParser());
app.use(logger('dev'));
app.use(bodyParser.json());
app.use(cors());
app.use(helmet());
app.use(express.urlencoded({ extended: true }));
app.use('/api', api);
console.log('ExpressJS is Setup!');

exports.ExpressApp = app;