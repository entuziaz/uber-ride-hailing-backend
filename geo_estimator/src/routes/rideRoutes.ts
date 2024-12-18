import express from 'express';
import { estimateRide } from "../controllers/rideController";

const router = express.Router();

router.post("/estimate", estimateRide);

export default router;
