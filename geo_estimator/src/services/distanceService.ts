import haversine from "haversine-distance";

interface Location {
    latitude: number;
    longitude: number;
}

class DistanceService {
    calculate(start: Location, end: Location): number {
        const distanceMeters = haversine(
            { lat: start.latitude, lng: start.longitude },
            { lat: end.latitude, lng: end.longitude }
        );
        
        // COnvert to kilometers and return
        return Math.round((distanceMeters / 1000) * 100) / 100; 
    }
}

export default new DistanceService();