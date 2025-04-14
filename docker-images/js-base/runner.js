const fs = require('fs');
const path = require('path');

const userCodeDir = process.argv[2];
const userCodePath = path.join(userCodeDir, 'user_code.js');

fs.readFile(userCodePath, 'utf8', (err, code) => {
    if (err) {
        console.error("Error reading user code:", err);
        process.exit(1);
    }
    try {
        eval(code);
    } catch (e) {
        console.error("Execution error:", e);
        process.exit(1);
    }
});
