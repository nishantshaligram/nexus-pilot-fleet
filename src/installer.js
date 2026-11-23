import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import readline from 'node:readline';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function getHomeDir() {
  return os.homedir();
}

function copyFolderRecursive(source, target, excludeList = ['node_modules', '.git', 'data', '__pycache__', '.fleet']) {
  if (!fs.existsSync(target)) {
    fs.mkdirSync(target, { recursive: true });
  }

  const files = fs.readdirSync(source);
  for (const file of files) {
    if (excludeList.includes(file)) {
      continue;
    }
    const curSource = path.join(source, file);
    const curTarget = path.join(target, file);

    try {
      if (fs.lstatSync(curSource).isDirectory()) {
        copyFolderRecursive(curSource, curTarget, excludeList);
      } else {
        fs.copyFileSync(curSource, curTarget);
      }
    } catch (err) {
      console.warn(`  [!] Notice: ${file} could not be overwritten (possibly in-use). Keeping existing copy.`);
    }
  }
}

function updateMcpJson(filePath, serverDef, agentName) {
  try {
    const dir = path.dirname(filePath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    let config = {};
    if (fs.existsSync(filePath)) {
      try {
        const raw = fs.readFileSync(filePath, 'utf-8').trim();
        if (raw) {
          config = JSON.parse(raw);
        }
      } catch (err) {
        console.warn(`  [!] Warning: Existing config at ${filePath} was malformed. Recreating safely.`);
        config = {};
      }
    }

    if (!config.mcpServers) {
      config.mcpServers = {};
    }

    config.mcpServers['nexus-pilot-fleet'] = serverDef;

    fs.writeFileSync(filePath, JSON.stringify(config, null, 2), 'utf-8');
    console.log(`  \x1b[32m[✓]\x1b[0m Configured \x1b[1m${agentName}\x1b[0m successfully!`);
    console.log(`      \x1b[90mLocation: ${filePath}\x1b[0m`);
    return true;
  } catch (err) {
    console.error(`  \x1b[31m[✗]\x1b[0m Failed to configure ${agentName}: ${err.message}`);
    return false;
  }
}

export async function promptTargetAgent() {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  console.log('\x1b[33mNo target environment specified. Choose an option:\x1b[0m');
  console.log('  [1] All (Antigravity, Claude, Cursor, Windsurf) [Default]');
  console.log('  [2] Google Antigravity Only');
  console.log('  [3] Claude Only (Desktop & Code CLI)');
  console.log('  [4] Cursor IDE Only');
  console.log('  [5] Windsurf Only');
  console.log('  [6] Antigravity + Claude Only\n');

  return new Promise((resolve) => {
    rl.question('Enter choice [1-6] (Press Enter for 1): ', (answer) => {
      rl.close();
      const choice = answer.trim();
      switch (choice) {
        case '2': resolve('antigravity'); break;
        case '3': resolve('claude'); break;
        case '4': resolve('cursor'); break;
        case '5': resolve('windsurf'); break;
        case '6': resolve('antigravity+claude'); break;
        default: resolve('all'); break;
      }
    });
  });
}

export async function runInstaller(targetAgent = null) {
  if (!targetAgent) {
    if (process.stdin.isTTY) {
      targetAgent = await promptTargetAgent();
    } else {
      targetAgent = 'all';
    }
  }

  const home = getHomeDir();
  const projectRoot = path.resolve(__dirname, '..');
  const serverPath = path.join(projectRoot, 'server', 'fleet_server.py').replace(/\\/g, '/');

  const normalizedTarget = targetAgent.toLowerCase();

  const mcpServerDef = {
    command: 'python',
    args: [serverPath],
    description: 'NexusPilot Fleet Swarm Orchestrator & Worktree Multiplexer'
  };

  console.log('\n\x1b[36m=======================================================');
  console.log('   NexusPilot Fleet Universal MCP & Plugin Installer   ');
  console.log('   (Multi-Agent Swarm Orchestrator & Worktree Engine)  ');
  console.log('=======================================================\x1b[0m');
  console.log(`Target: \x1b[1m${targetAgent}\x1b[0m\n`);

  // 1. Antigravity
  if (normalizedTarget === 'all' || normalizedTarget === 'antigravity' || normalizedTarget === 'antigravity+claude') {
    console.log('\x1b[36m[*] Installing for Google Antigravity...\x1b[0m');
    const pluginTargetDir = path.join(home, '.gemini', 'config', 'plugins', 'nexus-pilot-fleet');
    try {
      copyFolderRecursive(projectRoot, pluginTargetDir);
      console.log(`  \x1b[32m[✓]\x1b[0m Plugin & Skills installed in: \x1b[90m${pluginTargetDir}\x1b[0m`);

      const agyMcpPath = path.join(home, '.gemini', 'antigravity', 'mcp_config.json');
      updateMcpJson(agyMcpPath, mcpServerDef, 'Antigravity Global MCP');
    } catch (err) {
      console.error(`  \x1b[31m[✗]\x1b[0m Antigravity installation error: ${err.message}`);
    }
  }

  // 2. Claude (Claude Code CLI & Desktop)
  if (normalizedTarget === 'all' || normalizedTarget === 'claude' || normalizedTarget === 'claude-code' || normalizedTarget === 'antigravity+claude') {
    console.log('\n\x1b[36m[*] Installing for Claude (Code & Desktop)...\x1b[0m');
    const claudeCodePath = path.join(home, '.claude.json');
    updateMcpJson(claudeCodePath, mcpServerDef, 'Claude Code CLI');

    const appData = process.env.APPDATA || path.join(home, 'AppData', 'Roaming');
    const claudeDesktopPath = path.join(appData, 'Claude', 'claude_desktop_config.json');
    updateMcpJson(claudeDesktopPath, mcpServerDef, 'Claude Desktop App');
  }

  // 3. Cursor
  if (normalizedTarget === 'all' || normalizedTarget === 'cursor') {
    console.log('\n\x1b[36m[*] Installing for Cursor IDE...\x1b[0m');
    const cursorMcpPath = path.join(home, '.cursor', 'mcp.json');
    updateMcpJson(cursorMcpPath, mcpServerDef, 'Cursor Global MCP');
  }

  // 4. Windsurf
  if (normalizedTarget === 'all' || normalizedTarget === 'windsurf') {
    console.log('\n\x1b[36m[*] Installing for Windsurf / Codeium...\x1b[0m');
    const windsurfPath = path.join(home, '.codeium', 'windsurf', 'mcp_config.json');
    updateMcpJson(windsurfPath, mcpServerDef, 'Windsurf Global MCP');
  }

  console.log('\n\x1b[36m=======================================================');
  console.log('   \x1b[32mInstallation Complete!\x1b[36m NexusPilot Fleet is ready.  ');
  console.log('=======================================================\x1b[0m');
  console.log('Restart your AI agent or reload your editor window to activate Fleet.\n');
}
