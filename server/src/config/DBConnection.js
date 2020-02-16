const mysql = require('mysql');

exports.DBConnection = {
    connect: async () => {
        const db = mysql.createConnection({
            host: process.env.NODE_ENV !== 'production' ? process.env.DB_HOST : '',
            socketPath: process.env.NODE_ENV !== 'production' ? '' : process.env.DB_SOCKET,
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

        return db;
    }
};