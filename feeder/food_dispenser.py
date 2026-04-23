import time
import sys
import random
import logging
from datetime import datetime, timedelta
from devices.motor import Motor
from devices.weights import Weights

logger = logging.Logger("Food dispenser")
MAX_SPINS = 15

def dispense_food(weights: Weights, motor: Motor, target_weight_grams: float) -> None:
    """Dispense specified amount of food in the feeder."""

    curr_weight = weights.get_weight()
    num_spins = 0

    while curr_weight < target_weight_grams and num_spins < MAX_SPINS:
        motor.spin()
        time.sleep(1)
        curr_weight = weights.get_weight()
        num_spins += 1

def main(target_weight_grams: float, time_intervals: list[tuple[int, int]]) -> None:
    """
    Run the feeder continuously, dispensing food at random times within specified intervals.
    
    Args:
        target_weight_grams: Target weight of food to dispense per feeding
        time_intervals: List of time intervals as (start_min, end_min) tuples where
                       minutes are since 12 AM (midnight)
    """
    weights = Weights(port="COM10")
    motor = Motor(port="COM10")
    
    current_day = None
    scheduled_times = []
    
    while True:
        now = datetime.now()
        today = now.date()
        
        # Generate new schedule for new day
        if current_day != today:
            current_day = today
            scheduled_times = []
            
            # Create random times for each interval
            for start_min, end_min in time_intervals:
                # Ensure valid interval
                if start_min < end_min:
                    random_minute = random.randint(start_min, end_min)
                    scheduled_times.append(random_minute)
            
            scheduled_times.sort()
            logger.info(f"New day schedule generated: {scheduled_times}")
        
        # Get current time in minutes since midnight
        current_minutes = now.hour * 60 + now.minute
        
        # Check if we should dispense food now
        if scheduled_times and current_minutes == scheduled_times[0]:
            logger.info(f"Dispensing food at {now.strftime('%H:%M')}")
            dispense_food(weights, motor, target_weight_grams)
            scheduled_times.pop(0)
            time.sleep(60)  # Sleep for 1 minute to avoid multiple dispenses in same minute
        else:
            time.sleep(1)  # Check every second

if __name__ == '__main__':
    target_weight_grams = int(sys.argv[1])
    time_intervals = []
    for i in range(2, len(sys.argv), 2):
        time_intervals.append((int(sys.argv[i]), int(sys.argv[i+1])))

    main(target_weight_grams=target_weight_grams, time_intervals=time_intervals)
