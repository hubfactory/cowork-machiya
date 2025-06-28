export interface Reservation {
  id?: string;
  name: string;
  email: string;
  date: string; // yyyy-MM-dd
  seats: number;
}

export interface ReservationResponse {
  reservations: Reservation[];
} 