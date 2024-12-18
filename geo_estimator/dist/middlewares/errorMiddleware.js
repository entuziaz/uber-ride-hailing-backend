"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const errorMiddleware = (err, re, res, next) => {
    console.error(err.message);
    res.status(500).json({ error: "An internal server error occurred." });
};
exports.default = errorMiddleware;
