import { error } from "console";
import { Request, Response, NextFunction } from "express";

const errorMiddleware = (err: any, req: Request, res: Response, next: NextFunction) => {
    console.error(err.message);
    res.status(500).json({error: err.message || "An internal server error occurred."});

};

export default errorMiddleware;