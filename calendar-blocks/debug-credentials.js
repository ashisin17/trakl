// debug-credentials.js
// Run this to check your credentials.json file

const fs = require('fs');

try {
  console.log('🔍 Checking credentials.json...');
  
  // Check if file exists
  if (!fs.existsSync('./credentials.json')) {
    console.log('❌ credentials.json file not found!');
    process.exit(1);
  }
  
  // Read and parse the file
  const credentialsText = fs.readFileSync('./credentials.json', 'utf8');
  console.log('📄 Raw credentials file content:');
  console.log(credentialsText);
  
  const credentials = JSON.parse(credentialsText);
  console.log('\n📊 Parsed credentials structure:');
  console.log('Keys:', Object.keys(credentials));
  
  // Check for different formats
  if (credentials.installed) {
    console.log('✅ Found "installed" credentials (Desktop app format)');
    console.log('Client ID:', credentials.installed.client_id);
    console.log('Redirect URIs:', credentials.installed.redirect_uris);
  } else if (credentials.web) {
    console.log('✅ Found "web" credentials (Web app format)');
    console.log('Client ID:', credentials.web.client_id);
    console.log('Redirect URIs:', credentials.web.redirect_uris);
  } else {
    console.log('❌ Unknown credentials format!');
    console.log('Expected either "installed" or "web" property');
    
    // Check if it's a flat format (wrong download)
    if (credentials.client_id) {
      console.log('🔧 This looks like a flat format. You might have downloaded the wrong type.');
      console.log('Make sure to download "OAuth 2.0 Client IDs" not "API Keys"');
    }
  }
  
} catch (error) {
  console.error('❌ Error reading credentials:', error.message);
  
  if (error.message.includes('Unexpected token')) {
    console.log('💡 The credentials.json file appears to be corrupted or invalid JSON');
    console.log('Try downloading it again from Google Cloud Console');
  }
}