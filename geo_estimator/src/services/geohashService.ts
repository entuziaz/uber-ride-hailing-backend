import geohash from "ngeohash";

class GeohashService {
    encode(lat: number, lng: number): string {
        return geohash.encode(lat, lng, 7); // at Precision: 7
    }
}

export default new GeohashService();