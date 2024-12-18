"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.estimateRide = void 0;
const geohashService_1 = __importDefault(require("../services/geohashService"));
const fareService_1 = __importDefault(require("../services/fareService"));
const distanceService_1 = __importDefault(require("../services/distanceService"));
const estimateRide = (req, res, next) => {
    try {
        const { pickup_location, dropoff_location, ride_type } = req.body;
        // Validate Input
        if (!pickup_location || !dropoff_location || !ride_type) {
            res.status(400).json({ error: "Missing required fields." });
            return;
        }
        // Stage 1: Geohash coordinates
        const pickupGeohash = geohashService_1.default.encode(pickup_location.latitude, pickup_location.longitude);
        const dropoffGeohash = geohashService_1.default.encode(dropoff_location.latitude, dropoff_location.longitude);
        // Stage 2: Calculate distance
        const distance = distanceService_1.default.calculate(pickup_location, dropoff_location);
        // Stage 3: Estimate fare
        const fare = fareService_1.default.calculateFare(distance, ride_type);
        // Step 4: Return JSON response
        res.status(200).json({
            message: "Ride estimate calculated successfully",
            pickup_geohash: pickupGeohash,
            dropoff_geohash: dropoffGeohash,
            distance_km: distance,
            estimated_fare: fare,
        });
    }
    catch (error) {
        next(error);
    }
};
exports.estimateRide = estimateRide;
