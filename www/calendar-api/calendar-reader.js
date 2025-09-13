// calendar-reader.js
class CalendarReader {
    async getWeeklyAvailability(userId, startDate) {
      // Get all events for the week
      const events = await this.getCalendarEvents(userId, startDate);
      
      // Convert to availability windows
      const freeSlots = this.findFreeTimeSlots(events);
      
      return {
        totalFreeHours: this.calculateFreeHours(freeSlots),
        freeSlots: freeSlots,
        busyPeriods: events,
        workingHours: this.detectWorkingHours(events)
      };
    }
    
    findFreeTimeSlots(events, workingHours = { start: 9, end: 17 }) {
      // Algorithm to find gaps between existing events
      const freeSlots = [];
      
      // Sort events by start time
      const sortedEvents = events.sort((a, b) => 
        new Date(a.start.dateTime) - new Date(b.start.dateTime)
      );
      
      // Find gaps between events
      for (let i = 0; i < sortedEvents.length - 1; i++) {
        const currentEnd = new Date(sortedEvents[i].end.dateTime);
        const nextStart = new Date(sortedEvents[i + 1].start.dateTime);
        
        const gapMinutes = (nextStart - currentEnd) / (1000 * 60);
        
        if (gapMinutes >= 30) { // Minimum 30-minute blocks
          freeSlots.push({
            start: currentEnd,
            end: nextStart,
            duration: gapMinutes,
            type: 'gap_between_events'
          });
        }
      }
      
      return freeSlots;
    }
  }