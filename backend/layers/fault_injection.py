import random
import time
import psutil

class ResourceAnomalySimulator:
    @classmethod
    def simulate_high_memory_usage(cls, probability: float = 1.0, duration: float = 5.0, memory_chunk_size: float = 0.7):
        """
        Simulate high memory usage by continuously allocating memory for a given duration.
        
        Args:
            probability (float): A value between 0 and 1 indicating the likelihood to trigger the anomaly.
            duration (float): Duration in seconds for which the memory usage anomaly should run.
            memory_chunk_size (int): Size (in characters) of each memory block allocated.

        Returns:
            str: A message indicating if the anomaly was triggered or not.
        """
        if random.random() > probability:
            return 0

        # Keep references to allocated memory blocks so they are not garbage collected.
        mem_info = psutil.virtual_memory()
        available_bytes = mem_info.available
        
        # Calculate how many bytes we want to allocate
        bytes_to_allocate = int(available_bytes * memory_chunk_size)
        
        try:
            # Allocate memory
            allocation_block = bytearray(bytes_to_allocate)
            
        except MemoryError:
            allocation_block = None
        
        finally:
            # Free the memory
            del allocation_block

        return bytes_to_allocate / 1e6

    @classmethod
    def simulate_high_cpu_usage(cls, probability: float = 1.0, duration: float = 5.0):
        """
        Simulate a CPU-intensive operation for `duration` seconds with a `probability`
        chance. If the random draw is below `probability`, the CPU hogging happens;
        otherwise, it does nothing.

        :param probability: Chance (0 to 1) that the CPU hogging code will run.
                            e.g., 0.2 means there's a 20% chance it will hog the CPU.
        :param duration: How many seconds to run the CPU usage simulation if triggered.
        """
        if random.random() > probability:
            return 0

        end_time = time.time() + duration
        
        # Busy loop until the time is reached
        while time.time() < end_time:
            # A trivial operation to keep the CPU busy
            pass

        return duration