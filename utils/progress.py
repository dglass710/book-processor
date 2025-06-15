"""
Progress tracking and display utilities
"""

import sys
import time
from datetime import timedelta


class ProgressTracker:
    """
    Track and display progress for long-running operations
    """

    def __init__(self, total, description="Processing", update_interval=0.5):
        """
        Initialize a progress tracker

        Args:
            total: Total number of items to process
            description: Description of the operation
            update_interval: Minimum time between progress updates (seconds)
        """
        self.total = total
        self.description = description
        self.update_interval = update_interval
        self.current = 0
        self.start_time = None
        self.last_update_time = 0
        self.last_eta = None

    def start(self):
        """Start the progress tracker"""
        self.start_time = time.time()
        self.last_update_time = 0
        self.current = 0
        self._display_progress()
        return self

    def update(self, current=None, force=False):
        """
        Update the progress display

        Args:
            current: Current progress value (incremented by 1 if None)
            force: Force update even if update_interval hasn't elapsed
        """
        if current is not None:
            self.current = current
        else:
            self.current += 1

        # Only update display if enough time has passed or if forced
        current_time = time.time()
        if force or (current_time - self.last_update_time) >= self.update_interval:
            self._display_progress()
            self.last_update_time = current_time

    def finish(self):
        """Mark the operation as complete"""
        self.current = self.total
        self._display_progress(force_newline=True)
        print(
            f"\n{self.description} completed in {self._format_time(time.time() - float(self.start_time) if self.start_time is not None else 0.0)}"
        )

    def _display_progress(self, force_newline=False):
        """Display the progress bar and stats"""
        if self.total <= 0:
            return

        # Calculate percentage
        percent = min(100, self.current * 100 / self.total)

        # Calculate ETA
        eta_str = "calculating..."
        if self.current > 0 and self.start_time:
            current_time = time.time()
            if self.start_time is not None:
                elapsed = current_time - float(self.start_time)
            else:
                elapsed = 0.0
            items_per_sec = self.current / elapsed if elapsed > 0 else 0
            if items_per_sec > 0:
                remaining_seconds = (self.total - self.current) / items_per_sec
                eta = timedelta(seconds=int(remaining_seconds))
                eta_str = str(eta)
                self.last_eta = eta_str
            elif self.last_eta:
                eta_str = self.last_eta

        # Create progress bar
        bar_length = 30
        filled_length = int(bar_length * self.current / self.total)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)

        # Create the progress message
        message = f"\r{self.description}: {self.current}/{self.total} [{bar}] {percent:.1f}% ETA: {eta_str}"

        # Print the progress
        sys.stdout.write(message)
        sys.stdout.flush()

        if force_newline:
            sys.stdout.write("\n")
            sys.stdout.flush()

    @staticmethod
    def _format_time(seconds):
        """Format time in seconds to a human-readable string"""
        return str(timedelta(seconds=int(seconds)))


class StepProgress:
    """
    Track progress across multiple steps of a workflow
    """

    def __init__(self, steps):
        """
        Initialize a step progress tracker

        Args:
            steps: List of step descriptions
        """
        self.steps = steps
        self.total_steps = len(steps)
        self.current_step = 0
        self.start_time = None
        self.step_start_times = {}
        self.step_durations = {}

    def start(self):
        """Start the workflow"""
        self.start_time = time.time()
        print(f"Starting workflow with {self.total_steps} steps")
        return self

    def start_step(self, step_index=None):
        """
        Start a new step

        Args:
            step_index: Index of the step to start (defaults to next step)
        """
        if step_index is not None:
            self.current_step = step_index
        else:
            self.current_step += 1

        if self.current_step <= len(self.steps):
            step_name = self.steps[self.current_step - 1]
            self.step_start_times[self.current_step] = time.time()

            # Print step header
            print("\n" + "=" * 80)
            print(f"Step {self.current_step} of {self.total_steps}: {step_name}")
            print("=" * 80)

        return self.current_step

    def end_step(self):
        """End the current step and display timing information"""
        if self.current_step in self.step_start_times:
            step_name = self.steps[self.current_step - 1]
            end_time = time.time()
            duration = end_time - self.step_start_times[self.current_step]
            self.step_durations[self.current_step] = duration

            print(f"\nCompleted: {step_name} in {self._format_time(duration)}")

    def finish(self):
        """Complete the workflow and display summary"""
        if self.start_time:
            total_duration = time.time() - self.start_time

            print("\n" + "=" * 80)
            print("Workflow Summary")
            print("=" * 80)

            for i, step in enumerate(self.steps):
                step_num = i + 1
                if step_num in self.step_durations:
                    duration = self.step_durations[step_num]
                    percent = (
                        (duration / total_duration) * 100
                        if total_duration and total_duration > 0
                        else 0
                    )
                    print(
                        f"Step {step_num}: {step} - {self._format_time(duration)} ({percent:.1f}%)"
                    )
                else:
                    print(f"Step {step_num}: {step} - Not completed")

            print("-" * 80)
            print(f"Total time: {self._format_time(total_duration)}")
            print("=" * 80)

    @staticmethod
    def _format_time(seconds):
        """Format time in seconds to a human-readable string"""
        return str(timedelta(seconds=int(seconds)))
