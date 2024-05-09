import time


class TimedObject:
    def __init__(self, name, delay):
        self.name = name
        self.delay = delay  # Delay in seconds
        self.available_time = 0  # Timestamp when it becomes available

    def use(self):
        """Attempt to use the object. If the object is available, update availability time."""
        current_time = time.time()
        if current_time >= self.available_time:
            #print(f"{self.name} is used.")
            self.available_time = current_time + self.delay
            return True
        else:
            #print(f"{self.name} is not available yet. Please wait for {round(self.available_time - current_time, 2)} seconds.")
            return False

    def is_available(self):
        """Check if the object is available to be used."""
        return time.time() >= self.available_time

# Example usage
if __name__ == "__main__":
    obj_list = [TimedObject("Object1", 5), TimedObject("Object2", 10)]

    # Test usage
    obj_list[0].use()  # Should be available and used
    obj_list[1].use()  # Should be available and used
    time.sleep(3)
    obj_list[0].use()  # Should not be available yet
    time.sleep(3)
    obj_list[0].use()  # Should be available again
