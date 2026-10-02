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
  { regex: /\bbg-slate-900\b/g, replacement: 'bg-background-secondary' },
  { regex: /\bbg-slate-950\b/g, replacement: 'bg-background-secondary' },
  { regex: /\bbg-slate-800\b/g, replacement: 'bg-card' },
  { regex: /\bbg-slate-700\b/g, replacement: 'bg-card-hover' },
  { regex: /\btext-slate-200\b/g, replacement: 'text-text-primary' },
  { regex: /\btext-slate-300\b/g, replacement: 'text-text-primary' },
  { regex: /\btext-slate-400\b/g, replacement: 'text-text-muted' },
  { regex: /\btext-slate-500\b/g, replacement: 'text-text-muted' },
  { regex: /\btext-white\b/g, replacement: 'text-text-primary' },
  { regex: /\bborder-white\/[0-9]+\b/g, replacement: 'border-border' },
  { regex: /\bborder-slate-[78]00\b/g, replacement: 'border-border' },
  { regex: /\bbg-black\/40\b/g, replacement: 'bg-card' },
  { regex: /\bbg-black\/20\b/g, replacement: 'bg-card' },
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
