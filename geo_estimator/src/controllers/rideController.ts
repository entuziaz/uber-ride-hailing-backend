import { RequestHandler } from "express";
import geohashService from "../services/geohashService";
import fareService from "../services/fareService";
import distanceService from "../services/distanceService";

export const estimateRide: RequestHandler = (req, res, next): void => {
    try {
        const { pickup_location, dropoff_location, ride_type } = req.body;

        if (!pickup_location || !dropoff_location || !ride_type) {
            res.status(400).json({ error: "Missing required fields." });
            return;
        }

        // Stage 1: Geohash coordinates
        const pickupGeohash = geohashService.encode(
            pickup_location.latitude,
            pickup_location.longitude
        );
        const dropoffGeohash = geohashService.encode(
            dropoff_location.latitude,
            dropoff_location.longitude
        );

        // Stage 2: Calculate distance
        const distance = distanceService.calculate(
            pickup_location,
            dropoff_location
        );

        // Stage 3: Estimate fare
        const fare = fareService.calculateFare(distance, ride_type);


        // Step 4: Return JSON response
        res.status(200).json({
            message: "Ride estimate calculated successfully",
            data: {
                pickup_geohash: pickupGeohash,
                dropoff_geohash: dropoffGeohash,
                distance_km: distance,
                estimated_fare: fare,
            },

            
        });
    } catch (error) {
        next(error);
    }
};
