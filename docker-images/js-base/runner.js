const fs = require('fs');

try {
  const code = fs.readFileSync('user_code.js', 'utf8');
  eval(code);
} catch (err) {
  console.error('Execution error:', err);
}
 
