import client from './client'

export const sendChat = (payload) => client.post('/api/chat', payload)
export const planTrip = (payload) => client.post('/api/trip/plan', payload)
export const getItinerary = (id) => client.get(`/api/itinerary/${id}`)