"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const BASE_RATE = 2;
const SURGE_MULTIPLIER = {
    standard: 1.0,
    premium: 1.5,
};
var RideType;
(function (RideType) {
    RideType["Standard"] = "standard";
    RideType["Premium"] = "premium";
})(RideType || (RideType = {}));
class FareService {
    calculateFare(distance, rideType) {
        const multiplier = SURGE_MULTIPLIER[rideType] || 1.0;
        return Math.round((distance * BASE_RATE * multiplier) * 100) / 100;
    }
}
exports.default = new FareService();
