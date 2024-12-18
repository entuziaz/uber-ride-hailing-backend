"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const ngeohash_1 = __importDefault(require("ngeohash"));
class GeohashService {
    encode(lat, lng) {
        return ngeohash_1.default.encode(lat, lng, 7); // at Precision: 7
    }
}
exports.default = new GeohashService();
