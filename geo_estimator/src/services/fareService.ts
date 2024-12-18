const BASE_RATE = 2;
const SURGE_MULTIPLIER = {
    standard: 1.0,
    premium: 1.5,
};

enum RideType {
    Standard = "standard",
    Premium = "premium",
}

class FareService {
    calculateFare(distance: number, rideType: RideType): number {
        // const multiplier = SURGE_MULTIPLIER[rideType] || 1.0;
        // return Math.round((distance * BASE_RATE * multiplier) * 100) / 100;

        if (isNaN(distance) || distance <= 0) {
            throw new Error('Invalid distance for fare calculation.');
        }

        if (!Object.values(RideType).includes(rideType)) {
            throw new Error('Invalid ride type.');
        }

        const multiplier = SURGE_MULTIPLIER[rideType] || 1.0;
        return Math.round((distance * BASE_RATE * multiplier) * 100) / 100;
    }

}

export default new FareService();