import { execSync } from 'node:child_process';
import os from 'node:os';
import path from 'node:path';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export function runDoctor() {
  console.log('\n\x1b[36m=======================================================');
  console.log('    NexusPilot Fleet - Environment Diagnostic Probe    ');
  console.log('=======================================================\x1b[0m\n');

  // 1. Operating System
  const platform = os.platform();
  const release = os.release();
  console.log(`\x1b[32m[✓]\x1b[0m OS: ${platform} (${release}, Architecture: ${os.arch()})`);

  // 2. Git Environment & Worktree Capability
  try {
    const gitVer = execSync('git --version', { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'ignore'] }).trim();
    console.log(`\x1b[32m[✓]\x1b[0m Git: ${gitVer}`);

    // Verify git worktree support (git version 2.5+ introduces git worktree)
    const match = gitVer.match(/(\d+)\.(\d+)/);
    if (match) {
      const major = parseInt(match[1], 10);
      const minor = parseInt(match[2], 10);
      if (major > 2 || (major === 2 && minor >= 5)) {
        console.log(`  \x1b[32m[✓]\x1b[0m Git Worktree: Supported & Available (v${major}.${minor})`);
      } else {
        console.log(`  \x1b[31m[✗]\x1b[0m Git 2.5+ is required for worktree isolation (Detected v${major}.${minor})`);
      }
    } else {
      console.log(`  \x1b[32m[✓]\x1b[0m Git Worktree: Available`);
    }
  } catch (err) {
    console.log(`\x1b[31m[✗]\x1b[0m Git not found on PATH! Please install Git from https://git-scm.com`);
  }

  // 3. Python Environment
  let pythonCmd = 'python';
  try {
    const pyVer = execSync('python --version', { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'ignore'] }).trim();
    console.log(`\x1b[32m[✓]\x1b[0m Python: ${pyVer}`);
  } catch {
    try {
      const pyVer = execSync('py --version', { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'ignore'] }).trim();
      pythonCmd = 'py';
      console.log(`\x1b[32m[✓]\x1b[0m Python (via py launcher): ${pyVer}`);
    } catch {
      console.log('\x1b[31m[✗]\x1b[0m Python 3.10+ not found on PATH! Please install Python from https://python.org');
    }
  }

  // 4. Core Python Dependencies
  console.log('\n\x1b[36mChecking Python Dependencies for Fleet:\x1b[0m');
  const packages = [
    { name: 'mcp', desc: 'Model Context Protocol SDK', required: true },
    { name: 'sqlite3', desc: 'Embedded Mission Event Bus', required: true },
    { name: 'subprocess', desc: 'Git Subprocess Multiplexing', required: true }
  ];

  for (const pkg of packages) {
    try {
      execSync(`${pythonCmd} -c "import ${pkg.name}"`, { stdio: 'ignore' });
      console.log(`  \x1b[32m[✓]\x1b[0m ${pkg.name}: Available (${pkg.desc})`);
    } catch {
      console.log(`  \x1b[31m[✗]\x1b[0m ${pkg.name}: Not installed (Run 'pip install ${pkg.name}')`);
    }
  }

  // 5. Fleet Storage Check
  console.log('\n\x1b[36mChecking Fleet Storage Directory:\x1b[0m');
  const localDataDir = path.resolve(__dirname, '..', 'data');
  try {
    if (!fs.existsSync(localDataDir)) {
      fs.mkdirSync(localDataDir, { recursive: true });
    }
    const testFile = path.join(localDataDir, '.probe');
    fs.writeFileSync(testFile, 'probe', 'utf-8');
    fs.unlinkSync(testFile);
    console.log(`  \x1b[32m[✓]\x1b[0m Fleet Storage Directory: Writable (${localDataDir})`);
  } catch (err) {
    console.log(`  \x1b[31m[✗]\x1b[0m Fleet Storage: Failed to write to ${localDataDir} (${err.message})`);
  }

  console.log('\n\x1b[36m=======================================================');
  console.log(' Diagnostic complete. Ready for NexusPilot Fleet!');
  console.log('=======================================================\x1b[0m\n');
}
