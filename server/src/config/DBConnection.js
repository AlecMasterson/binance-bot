const mysql = require('mysql');

async function connect() {
    try {
        const db = mysql.createConnection({
            host: process.env.DB_HOST,
            user: process.env.DB_USER,
            password: process.env.DB_PASS,
            database: process.env.DB_NAME
        });

        await new Promise((resolve, reject) => {
            db.connect((error) => {
                if (error) {
                    reject(error);
                }
                resolve();
            });
        });
        console.log('Connected to the DB!');

        return db;
    } catch (error) {
        console.log(error);
        process.exit(1);
    }
}

const setup = {
    connect: connect().then((connection) => {
        setup.db = connection;
        delete setup.connect;
    })
}

exports.DBConnection = setup;