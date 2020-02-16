const express = require('express');
const cookieParser = require('cookie-parser');
const bodyParser = require('body-parser');
const cors = require('cors');
const helmet = require('helmet');
const api = require('../routes/api');

exports.ExpressApp = {
    create: async () => {
        const app = express();

        app.use(express.json());
        app.use(cookieParser());
        app.use(bodyParser.json());
        app.use(cors());
        app.use(helmet());
        app.use(express.urlencoded({ extended: true }));
        app.use('/api', api);

        return app;
    }
};