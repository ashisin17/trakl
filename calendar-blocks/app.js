const SimpleCalendar = require('./simple-calendar');

async function main() {
  console.log('🚀 Starting Calendar Block Creator...');
  
  const calendar = new SimpleCalendar('./credentials.json');
  
  // Step 1: Authenticate (do this once)
  console.log('🔐 Authentication required...');
  await calendar.authenticate();
  
  // Step 2: Create events from blocks
  console.log('📅 Creating calendar events...');
  await calendar.createFromBlocks('./timeblocks.json');
  
  console.log('✅ Done!');
}

main().catch(error => {
  console.error('❌ Error:', error.message);
});