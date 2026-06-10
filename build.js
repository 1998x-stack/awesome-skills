#!/usr/bin/env node
import fs from 'fs';
import path from 'path';
import matter from 'gray-matter';

const ROOT_DIR = process.cwd();
const CATEGORIES = [
  'guidelines-mindsets', 'design-creative', 'game-development', 'ai-tools',
  'dev-engineering', 'document-generation', 'platform-ecosystems',
  'life-automation', 'domain-expertise'
];
const COLLECTIONS = [
  'ECC', 'awesome-copilot', 'gstack', 'get-shit-done', 'servers', 'spec-kit'
];
const SUPPORTING_DIRS = new Set(['references', 'scripts', 'examples', 'agents', 'assets']);
const TEXT_EXTS = new Set([
  '.md', '.yaml', '.yml', '.json', '.py', '.js', '.ts', '.jsx', '.tsx',
  '.css', '.html', '.txt', '.sh', '.toml', '.cfg', '.ini'
]);
const SKILL_DOC_NAMES = ['SKILL.md', 'AGENTS.md', 'CLAUDE.md'];
const MAX_DEPTH = 5;

function skip(name) {
  if (name === 'node_modules') return true;
  if (name.startsWith('.')) return true;
  return false;
}

function isTextFile(name) {
  return TEXT_EXTS.has(path.extname(name).toLowerCase());
}

function safeRead(filePath) {
  try { return fs.readFileSync(filePath, 'utf-8'); }
  catch { return null; }
}

function findDoc(dirPath) {
  for (const name of SKILL_DOC_NAMES) {
    const fp = path.join(dirPath, name);
    try {
      if (fs.statSync(fp).isFile()) {
        const raw = fs.readFileSync(fp, 'utf-8');
        const parsed = matter(raw);
        return { fileName: name, data: parsed.data || {}, body: parsed.content || '' };
      }
    } catch { /* not found or unreadable */ }
  }
  return null;
}

function scanSupportingDir(dirPath, name, relPath, depth) {
  const node = { name, type: 'dir', path: relPath, children: [] };
  if (depth > MAX_DEPTH) return node;

  let entries;
  try { entries = fs.readdirSync(dirPath, { withFileTypes: true }); }
  catch { return node; }

  for (const e of entries) {
    if (skip(e.name)) continue;
    const cp = path.join(dirPath, e.name);
    const cr = path.join(relPath, e.name);
    if (e.isDirectory()) {
      node.children.push(scanSupportingDir(cp, e.name, cr, depth + 1));
    } else if (isTextFile(e.name)) {
      node.children.push({ name: e.name, type: 'file', path: cr, ext: path.extname(e.name) });
    }
  }
  return node;
}

function scanNode(dirPath, relPath, name, depth, typeOverride) {
  if (depth > MAX_DEPTH) return null;
  try { if (!fs.statSync(dirPath).isDirectory()) return null; }
  catch { return null; }

  const doc = findDoc(dirPath);
  const type = typeOverride || (doc ? (doc.fileName === 'SKILL.md' ? 'skill' : 'agent-doc') : 'dir');

  const node = { name, type, path: relPath };

  if (type === 'skill' || type === 'agent-doc') {
    node.frontmatter = doc.data;
    node.body = doc.body;
    node.files = [];
  } else {
    node.frontmatter = {};
    node.body = '';
    node.children = [];
  }

  let entries;
  try { entries = fs.readdirSync(dirPath, { withFileTypes: true }); }
  catch { return node; }

  for (const e of entries) {
    if (skip(e.name)) continue;
    const cp = path.join(dirPath, e.name);
    const cr = path.join(relPath, e.name);

    if (e.isDirectory()) {
      if ((type === 'skill' || type === 'agent-doc') && SUPPORTING_DIRS.has(e.name)) {
        node.files.push(scanSupportingDir(cp, e.name, cr, depth + 1));
      } else {
        const child = scanNode(cp, cr, e.name, depth + 1);
        if (child) {
          if (node.children) node.children.push(child);
          else node.files.push(child);
        }
      }
    } else if (isTextFile(e.name)) {
      if (type === 'skill' || type === 'agent-doc') {
        if (SKILL_DOC_NAMES.includes(e.name) && e.name !== doc.fileName) {
          const raw = safeRead(cp);
          if (raw !== null) {
            const parsed = matter(raw);
            node.files.push({
              name: e.name, type: 'agent-doc', path: cr,
              frontmatter: parsed.data || {}, body: parsed.content || '', files: []
            });
          }
        } else if (!SKILL_DOC_NAMES.includes(e.name)) {
          node.files.push({ name: e.name, type: 'file', path: cr, ext: path.extname(e.name) });
        }
      } else {
        if (SKILL_DOC_NAMES.includes(e.name)) {
          const raw = safeRead(cp);
          if (raw !== null) {
            const parsed = matter(raw);
            node.children.push({
              name: e.name, type: 'agent-doc', path: cr,
              frontmatter: parsed.data || {}, body: parsed.content || '', files: []
            });
          }
        } else {
          node.children.push({ name: e.name, type: 'file', path: cr, ext: path.extname(e.name) });
        }
      }
    }
  }

  return node;
}

function countSkillChildren(node) {
  let n = 0;
  for (const c of (node.children || [])) {
    if (c.type === 'skill' || c.type === 'agent-doc') n += 1 + countSkillChildren(c);
    else n += countSkillChildren(c);
  }
  return n;
}

// --- main ---
console.log('=== Skill Visualizer — Build Scanner ===\n');

const tree = [];
let grandTotal = 0;

for (const cat of CATEGORIES) {
  const dp = path.join(ROOT_DIR, cat);
  if (!fs.existsSync(dp)) { console.log(`${cat} — SKIPPED (not found)`); continue; }
  process.stdout.write(`${cat}  `);
  const node = scanNode(dp, cat, cat, 0, 'category');
  const count = countSkillChildren(node);
  console.log(`→ ${count} skills`);
  grandTotal += count;
  tree.push(node);
}

for (const col of COLLECTIONS) {
  const dp = path.join(ROOT_DIR, col);
  if (!fs.existsSync(dp)) { console.log(`${col} — SKIPPED (not found)`); continue; }
  process.stdout.write(`${col}  `);
  const node = scanNode(dp, col, col, 0, 'collection');
  const count = countSkillChildren(node);
  const docCount = (node.files || []).filter(f => f.type === 'agent-doc').length;
  const parts = [];
  if (docCount) parts.push(`${docCount} root doc(s)`);
  if (count) parts.push(`${count} sub-skills`);
  console.log(`→ ${parts.join(', ') || '0 entries'}`);
  grandTotal += count;
  tree.push(node);
}

console.log(`\nTotal entries scanned: ${grandTotal}`);

const output = JSON.stringify({ tree, generatedAt: new Date().toISOString() });
fs.mkdirSync(path.join(ROOT_DIR, 'assets'), { recursive: true });
fs.writeFileSync(path.join(ROOT_DIR, 'assets', 'data.json'), output);
console.log(`Written: assets/data.json  (${(Buffer.byteLength(output) / 1024 / 1024).toFixed(1)} MB)`);
