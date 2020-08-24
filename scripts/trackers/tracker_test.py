from time import sleep

from scripts.trackers.dumb.dumb_tracker import DumbTracker

if __name__ == '__main__':
    tracker = DumbTracker('y1893')
    while True:
        tracker.update()
        sleep(1)
