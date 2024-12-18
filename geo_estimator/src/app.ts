import express, { Application } from "express";
import rideRoutes from "./routes/rideRoutes";

const app: Application = express();

app.use(express.json());
app.use("/api", rideRoutes);

import errorMiddleware from "./middlewares/errorMiddleware";
app.use(errorMiddleware);

export default app;