# Create this file: stations/management/commands/add_casablanca_stations.py

import os
from django.core.management.base import BaseCommand
from stations.models import ChargingStation

class Command(BaseCommand):
    help = 'Add charging stations across Casablanca'

    def handle(self, *args, **options):
        # Create management directory if it doesn't exist
        os.makedirs('stations/management/commands', exist_ok=True)
        
        stations_data = [
            {
                'name': 'Morocco Mall Charging Hub',
                'address': 'Morocco Mall, Boulevard de l\'Océan Atlantique, Casablanca',
                'latitude': 33.5888,
                'longitude': -7.6946,
                'status': 'active',
                'charger_type': 'type2',
                'power_rating': 22,
                'price_per_kwh': 2.50,
                'total_ports': 6,
                'available_ports': 4,
                'amenities': ['shopping', 'parking', 'food_court', 'wifi']
            },
            {
                'name': 'Hassan II Mosque Charging Point',
                'address': 'Boulevard Sidi Mohammed Ben Abdallah, Casablanca',
                'latitude': 33.6084,
                'longitude': -7.6325,
                'status': 'active',
                'charger_type': 'ccs',
                'power_rating': 50,
                'price_per_kwh': 3.00,
                'total_ports': 2,
                'available_ports': 2,
                'amenities': ['parking', 'tourist_site', 'restrooms']
            },
            {
                'name': 'Twin Center Business Plaza',
                'address': 'Boulevard Zerktouni, Casablanca',
                'latitude': 33.5892,
                'longitude': -7.6261,
                'status': 'active',
                'charger_type': 'type2',
                'power_rating': 22,
                'price_per_kwh': 2.40,
                'total_ports': 8,
                'available_ports': 6,
                'amenities': ['business_center', 'parking', 'wifi', 'conference_rooms']
            },
            {
                'name': 'Casa Port Station',
                'address': 'Boulevard Hassan Seghir, Casa-Port, Casablanca',
                'latitude': 33.5956,
                'longitude': -7.6231,
                'status': 'active',
                'charger_type': 'chademo',
                'power_rating': 40,
                'price_per_kwh': 2.80,
                'total_ports': 3,
                'available_ports': 2,
                'amenities': ['parking', 'cafe', 'waiting_area']
            },
            {
                'name': 'Anfa Place Central',
                'address': 'Place Mohammed V, Casablanca',
                'latitude': 33.5928,
                'longitude': -7.6192,
                'status': 'active',
                'charger_type': 'type2',
                'power_rating': 22,
                'price_per_kwh': 2.60,
                'total_ports': 4,
                'available_ports': 3,
                'amenities': ['city_center', 'parking', 'shopping', 'banks']
            },
            {
                'name': 'Ain Diab Beach Charging',
                'address': 'Boulevard de la Corniche, Ain Diab, Casablanca',
                'latitude': 33.6073,
                'longitude': -7.6296,
                'status': 'active',
                'charger_type': 'ccs',
                'power_rating': 60,
                'price_per_kwh': 3.20,
                'total_ports': 4,
                'available_ports': 4,
                'amenities': ['beach_access', 'parking', 'restaurants', 'wifi']
            },
            {
                'name': 'Maarif Fast Charge',
                'address': 'Rue Prince Moulay Abdellah, Maarif, Casablanca',
                'latitude': 33.5845,
                'longitude': -7.6098,
                'status': 'active',
                'charger_type': 'ccs',
                'power_rating': 75,
                'price_per_kwh': 3.50,
                'total_ports': 2,
                'available_ports': 1,
                'amenities': ['fast_charging', 'parking', 'convenience_store']
            },
            {
                'name': 'Racine Charging Station',
                'address': 'Boulevard Rachidi, Racine, Casablanca',
                'latitude': 33.5789,
                'longitude': -7.6456,
                'status': 'maintenance',
                'charger_type': 'type2',
                'power_rating': 22,
                'price_per_kwh': 2.30,
                'total_ports': 4,
                'available_ports': 0,
                'amenities': ['parking', 'security']
            }
        ]

        created_count = 0
        for station_data in stations_data:
            station, created = ChargingStation.objects.get_or_create(
                name=station_data['name'],
                defaults=station_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created station: {station.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Station already exists: {station.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully added {created_count} new charging stations!')
        )