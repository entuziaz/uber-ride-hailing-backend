import request from 'supertest';
import app from '../src/app';
import geohashService from '../src/services/geohashService';
import fareService from '../src/services/fareService';



describe('POST /api/estimate', () => {
    it('should return ride fare estimate with geohashed locations', async () => {
        const response = await request(app)
            .post('/api/estimate')
            .send({
                pickup_location: { latitude: 37.7749, longitude: -122.4194 },
                dropoff_location: { latitude: 37.8044, longitude: -122.2711 },
                ride_type: 'standard',
            });
            console.log(response.body); 

        expect(response.status).toBe(200);
        expect(response.body.data).toHaveProperty('pickup_geohash');
        expect(response.body.data).toHaveProperty('dropoff_geohash');
        expect(response.body.data).toHaveProperty('distance_km');
        expect(response.body.data).toHaveProperty('estimated_fare');
    });


    it('should return an error for missing fields', async() => {
        const response = await request(app)
            .post('/api/estimate')
            .send({
                dropoff_location: { latitude: 37.8044, longitude: -122.2711 },
                ride_type: 'standard',
            });

        expect(response.status).toBe(400);
        expect(response.body.error).toBe('Missing required fields.');
    }); 


    it('should handle geohash service failure gracefully', async () => {
        // Mock geohash service failure
        jest.spyOn(geohashService, 'encode').mockImplementationOnce(() => {
            throw new Error('Geohash service failure');
        });
    
        const response = await request(app)
            .post('/api/estimate')
            .send({
                pickup_location: { latitude: 37.7749, longitude: -122.4194 },
                dropoff_location: { latitude: 37.8044, longitude: -122.2711 },
                ride_type: 'standard',
            });
    
        expect(response.status).toBe(500);  // Internal server error
        expect(response.body.error).toBe('Geohash service failure');
    });

});

