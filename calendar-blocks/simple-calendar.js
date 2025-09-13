// ============================
// SIMPLE CALENDAR TIME BLOCKS
// ============================

const { google } = require('googleapis');
const fs = require('fs');

class SimpleCalendar {
  constructor(credentialsPath) {
    this.setupAuth(credentialsPath);
  }

  setupAuth(credentialsPath) {
    const credentials = JSON.parse(fs.readFileSync(credentialsPath));
    
    // Handle both formats: web app and desktop app
    const clientInfo = credentials.installed || credentials.web;
    
    if (!clientInfo) {
      throw new Error('Invalid credentials.json format. Make sure you downloaded the correct OAuth 2.0 credentials.');
    }
    
    this.oauth2Client = new google.auth.OAuth2(
      clientInfo.client_id,
      clientInfo.client_secret,
      clientInfo.redirect_uris ? clientInfo.redirect_uris[0] : 'http://localhost'
    );
    this.calendar = google.calendar({ version: 'v3', auth: this.oauth2Client });
  }

  // Simple authentication - paste the auth URL in browser
  async authenticate() {
    const authUrl = this.oauth2Client.generateAuthUrl({
      access_type: 'offline',
      scope: ['https://www.googleapis.com/auth/calendar'],
    });
    
    console.log('🔗 Go to this URL:', authUrl);
    console.log('📋 Copy the code from the URL after authentication');
    
    // In practice, get this from user input or callback
    const code = 'PASTE_YOUR_CODE_HERE'; // Replace with actual code
    const { tokens } = await this.oauth2Client.getToken(code);
    this.oauth2Client.setCredentials(tokens);
  }

  // Create events from simplified JSON
  async createFromBlocks(blocksFile) {
    const blocks = this.loadBlocks(blocksFile);
    const results = [];

    for (const block of blocks.timeBlocks) {
      try {
        const events = this.expandBlock(block);
        
        for (const event of events) {
          const result = await this.createSingleEvent(event);
          results.push({ success: true, event: result, block: block.name });
          await this.wait(200); // Rate limiting
        }
      } catch (error) {
        results.push({ success: false, error: error.message, block: block.name });
      }
    }

    this.printResults(results);
    return results;
  }

  loadBlocks(filePath) {
    return JSON.parse(fs.readFileSync(filePath, 'utf8'));
  }

  // Expand a time block into individual events
  expandBlock(block) {
    if (!block.repeat) {
      return [this.createGoogleEvent(block, block.date, block.time)];
    }

    const events = [];
    const dates = this.generateDates(block);
    
    for (const date of dates) {
      events.push(this.createGoogleEvent(block, date, block.time));
    }

    return events;
  }

  // Generate dates based on repeat pattern
  generateDates(block) {
    const dates = [];
    const startDate = new Date(block.date);
    const repeat = block.repeat;

    // Handle "forever" repeating events
    let maxIterations;
    let untilDate = null;

    if (repeat.forever) {
      if (repeat.until) {
        untilDate = new Date(repeat.until);
        maxIterations = 1000; // Safety limit
      } else {
        // Default limits for "forever" to prevent infinite loops
        maxIterations = repeat.type === 'daily' ? 365 : 
                       repeat.type === 'weekly' ? 104 : 
                       repeat.type === 'monthly' ? 60 : 365;
      }
    } else {
      maxIterations = repeat.count || 10;
    }

    for (let i = 0; i < maxIterations; i++) {
      const currentDate = new Date(startDate);

      switch (repeat.type) {
        case 'daily':
          currentDate.setDate(startDate.getDate() + (i * (repeat.every || 1)));
          break;
        case 'weekly':
          currentDate.setDate(startDate.getDate() + (i * 7 * (repeat.every || 1)));
          break;
        case 'monthly':
          currentDate.setMonth(startDate.getMonth() + (i * (repeat.every || 1)));
          break;
      }

      // Stop if we've reached the "until" date
      if (untilDate && currentDate > untilDate) {
        break;
      }

      // Skip weekends if specified
      if (repeat.skipWeekends && (currentDate.getDay() === 0 || currentDate.getDay() === 6)) {
        continue;
      }

      // Skip specific dates
      const dateString = currentDate.toISOString().split('T')[0];
      if (repeat.skip && repeat.skip.includes(dateString)) {
        continue;
      }

      dates.push(dateString);
    }

    return dates;
  }

  // Convert simple block to Google Calendar event
  createGoogleEvent(block, date, time) {
    const [startTime, endTime] = time.split('-');
    
    return {
      summary: block.name,
      description: block.description || '',
      location: block.location || '',
      start: {
        dateTime: `${date}T${startTime}:00`,
        timeZone: block.timezone || 'America/New_York'
      },
      end: {
        dateTime: `${date}T${endTime}:00`,
        timeZone: block.timezone || 'America/New_York'
      },
      attendees: (block.attendees || []).map(email => ({ email })),
      reminders: {
        useDefault: false,
        overrides: [{ method: 'popup', minutes: block.reminder || 10 }]
      }
    };
  }

  async createSingleEvent(eventData) {
    const response = await this.calendar.events.insert({
      calendarId: 'primary',
      resource: eventData,
    });
    return response.data;
  }

  printResults(results) {
    console.log('\n📅 CALENDAR CREATION RESULTS:');
    console.log('================================');
    
    const successful = results.filter(r => r.success);
    const failed = results.filter(r => !r.success);
    
    console.log(`✅ Success: ${successful.length}`);
    console.log(`❌ Failed: ${failed.length}`);
    
    if (failed.length > 0) {
      console.log('\n🚨 Failures:');
      failed.forEach(f => console.log(`   - ${f.block}: ${f.error}`));
    }
  }

  wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// ============================
// USAGE EXAMPLE
// ============================

async function main() {
  const calendar = new SimpleCalendar('./credentials.json');
  
  // Authenticate (you'll need to do this once)
  // await calendar.authenticate();
  
  // Create events from simple blocks
  await calendar.createFromBlocks('./timeblocks.json');
}

// Uncomment to run
// main().catch(console.error);

module.exports = SimpleCalendar;