import { spawn } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import fs from 'node:fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export function findPythonExecutable() {
  const possibleCommands = ['python', 'py', 'python3'];
  for (const cmd of possibleCommands) {
    try {
      const res = spawn(cmd, ['--version'], { stdio: 'pipe', shell: true });
      return cmd;
    } catch {
      // Continue to next command
    }
  }
  return 'python';
}

export function startMcpServer() {
  const pythonCmd = findPythonExecutable();
  const projectRoot = path.resolve(__dirname, '..');
  const serverPath = path.join(projectRoot, 'server', 'fleet_server.py');

  if (!fs.existsSync(serverPath)) {
    console.error(`[NexusPilot Fleet] Error: Server script not found at ${serverPath}`);
    process.exit(1);
  }

  const child = spawn(pythonCmd, [serverPath], {
    stdio: ['inherit', 'inherit', 'inherit'],
    shell: false
  });

  child.on('error', (err) => {
    console.error(`[NexusPilot Fleet] Failed to start Python MCP server daemon: ${err.message}`);
    process.exit(1);
  });

  child.on('close', (code) => {
    process.exit(code ?? 0);
  });

  process.on('SIGINT', () => {
    child.kill('SIGINT');
  });

  process.on('SIGTERM', () => {
    child.kill('SIGTERM');
  });
}
