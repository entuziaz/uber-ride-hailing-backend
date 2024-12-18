"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const haversine_distance_1 = __importDefault(require("haversine-distance"));
class DistanceService {
    calculate(start, end) {
        const distanceMeters = (0, haversine_distance_1.default)({ lat: start.latitude, lng: start.longitude }, { lat: end.latitude, lng: end.longitude });
        // COnvert to kilometers and return
        return Math.round((distanceMeters / 1000) * 100) / 100;
    }
}
exports.default = new DistanceService();
