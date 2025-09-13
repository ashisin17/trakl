// ai-scheduler.js
class AIScheduler {
    constructor() {
      this.scheduleTemplates = {
        'deep_work': { duration: 120, preferredTimes: [9, 10, 14] },
        'meetings': { duration: 60, preferredTimes: [10, 11, 14, 15] },
        'admin_tasks': { duration: 30, preferredTimes: [13, 16, 17] },
        'learning': { duration: 90, preferredTimes: [9, 10] },
        'exercise': { duration: 60, preferredTimes: [7, 8, 18, 19] }
      };
    }
    
    async generateSchedule(availability, goals, preferences = {}) {
      const suggestions = [];
      
      // Prioritize goals by importance/urgency
      const prioritizedGoals = this.prioritizeGoals(goals);
      
      // For each goal, find best time slots
      for (let goal of prioritizedGoals) {
        const bestSlots = this.findBestSlots(
          availability.freeSlots, 
          goal, 
          preferences
        );
        
        suggestions.push({
          goal: goal.name,
          description: goal.description,
          suggestedSlots: bestSlots,
          reasoning: this.explainSchedulingChoice(goal, bestSlots)
        });
      }
      
      return {
        suggestions,
        summary: this.createScheduleSummary(suggestions),
        conflicts: this.detectPotentialConflicts(suggestions)
      };
    }
    
    findBestSlots(freeSlots, goal, preferences) {
      const template = this.scheduleTemplates[goal.type] || { duration: 60 };
      
      return freeSlots
        .filter(slot => slot.duration >= template.duration)
        .map(slot => ({
          ...slot,
          score: this.scoreTimeSlot(slot, goal, template, preferences),
          suggestedTitle: this.generateBlockTitle(goal),
          suggestedDescription: this.generateBlockDescription(goal)
        }))
        .sort((a, b) => b.score - a.score)
        .slice(0, 3); // Top 3 suggestions per goal
    }
    
    scoreTimeSlot(slot, goal, template, preferences) {
      let score = 100;
      
      const hour = slot.start.getHours();
      
      // Prefer template's preferred times
      if (template.preferredTimes.includes(hour)) score += 20;
      
      // User preferences
      if (preferences.morningPerson && hour < 12) score += 15;
      if (preferences.afternoonPerson && hour >= 14) score += 15;
      
      // Avoid lunch time for work tasks
      if (goal.type !== 'personal' && hour === 12) score -= 30;
      
      // Prefer longer slots for deep work
      if (goal.type === 'deep_work' && slot.duration > 90) score += 10;
      
      return score;
    }
    
    generateBlockTitle(goal) {
      const titles = {
        'deep_work': ['🎯 Deep Work Session', '⚡ Focus Time', '🚀 Productivity Block'],
        'learning': ['📚 Learning Session', '🧠 Study Time', '📖 Skill Building'],
        'admin_tasks': ['📋 Admin Tasks', '📊 Organization Time', '✅ Task Management'],
        'exercise': ['💪 Workout', '🏃‍♀️ Exercise Session', '🧘‍♂️ Fitness Time']
      };
      
      const options = titles[goal.type] || ['📅 Scheduled Block'];
      return options[Math.floor(Math.random() * options.length)];
    }

    
  }