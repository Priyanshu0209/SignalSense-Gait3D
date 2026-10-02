const fs = require('fs');
const path = require('path');

const walk = (dir, done) => {
  let results = [];
  fs.readdir(dir, (err, list) => {
    if (err) return done(err);
    let pending = list.length;
    if (!pending) return done(null, results);
    list.forEach(file => {
      file = path.resolve(dir, file);
      fs.stat(file, (err, stat) => {
        if (stat && stat.isDirectory()) {
          walk(file, (err, res) => {
            results = results.concat(res);
            if (!--pending) done(null, results);
          });
        } else {
          if (file.endsWith('.tsx') || file.endsWith('.ts')) {
            results.push(file);
          }
          if (!--pending) done(null, results);
        }
      });
    });
  });
};

const replacements = [
  { regex: /\bbg-(slate|gray|zinc|neutral|stone)-(900|950)(\/[0-9]+)?\b/g, replacement: 'bg-background-secondary' },
  { regex: /\bbg-(slate|gray|zinc|neutral|stone)-(800)(\/[0-9]+)?\b/g, replacement: 'bg-card' },
  { regex: /\bbg-(slate|gray|zinc|neutral|stone)-(700|600)(\/[0-9]+)?\b/g, replacement: 'bg-card-hover' },
  { regex: /\bbg-(slate|gray|zinc|neutral|stone)-(100|200|300)(\/[0-9]+)?\b/g, replacement: 'bg-background-primary' },
  { regex: /\bbg-\[\#020617\]\b/g, replacement: 'bg-background-primary' },
  { regex: /\bbg-black(\/[0-9]+)?\b/g, replacement: 'bg-card' },
  { regex: /\bborder-(slate|gray|zinc|neutral|stone)-[0-9]+(\/[0-9]+)?\b/g, replacement: 'border-border' },
  { regex: /\btext-(slate|gray|zinc|neutral|stone)-(100|200|300)(\/[0-9]+)?\b/g, replacement: 'text-text-primary' },
  { regex: /\btext-(slate|gray|zinc|neutral|stone)-(400|500|600)(\/[0-9]+)?\b/g, replacement: 'text-text-muted' },
  { regex: /\btext-(slate|gray|zinc|neutral|stone)-(700|800|900)(\/[0-9]+)?\b/g, replacement: 'text-text-secondary' },
  
  // Fix button text contrast where background is accent
  { regex: /bg-accent-primary([a-zA-Z0-9\-\s/]+)text-text-primary/g, replacement: 'bg-accent-primary$1text-white' },
  { regex: /bg-blue-([0-9]+)([a-zA-Z0-9\-\s/]+)text-text-primary/g, replacement: 'bg-blue-$1$2text-white' },
  { regex: /bg-status-([a-zA-Z]+)([a-zA-Z0-9\-\s/]+)text-text-primary/g, replacement: 'bg-status-$1$2text-white' },
];

walk('/home/priyanshu/Projects/SignalSense-Gait3D/frontend/src', (err, files) => {
  if (err) throw err;
  let totalReplacements = 0;
  
  files.forEach(file => {
    let content = fs.readFileSync(file, 'utf8');
    let original = content;
    
    replacements.forEach(({ regex, replacement }) => {
      content = content.replace(regex, replacement);
    });
    
    if (content !== original) {
      fs.writeFileSync(file, content, 'utf8');
      totalReplacements++;
    }
  });
  
  console.log(`Updated ${totalReplacements} files.`);
});
