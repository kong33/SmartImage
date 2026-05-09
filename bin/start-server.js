import { spawnSync } from "node:child_process";
import path from "node:path";
import fs from "node:fs";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const serverDir = path.join(__dirname, "..");
const venvDir = path.join(serverDir, ".venv");

const isWindows = process.platform === "win32";
const pythonCommand = isWindows ? "python" : "python3";

const venvPython = isWindows
  ? path.join(venvDir, "Scripts", "python.exe")
  : path.join(venvDir, "bin", "python");

function printBanner() {
  console.log(`
   ____            _   _             
  / ___|__ _ _ __ | |_(_) ___  _ __  
 | |   / _\` | '_ \\| __| |/ _ \\| '_ \\ 
 | |__| (_| | |_) | |_| | (_) | | | |
  \\____\\__,_| .__/ \\__|_|\\___/|_| |_|
            |_|                       

  react-a11y-auto-caption-server
  `);
}

function printFirstRunNotice() {
  console.log(`
First run detected.

This may take a few minutes because:
- A Python virtual environment will be created
- Python dependencies will be installed
- The AI model may be downloaded on first request

Server URL:
  http://127.0.0.1:8000

Please keep this terminal open while using the caption server.
`);
}

function run(command, args, options = {}) {
  const result = spawnSync(command, args, {
    stdio: "inherit",
    shell: isWindows,
    ...options,
  });

  if (result.error || result.status !== 0) {
    process.exit(result.status ?? 1);
  }
}

printBanner();

const isFirstRun = !fs.existsSync(venvDir);

if (isFirstRun) {
  printFirstRunNotice();
}

console.log("Checking Python installation...");
run(pythonCommand, ["--version"]);

if (!fs.existsSync(venvDir)) {
  console.log("Creating Python virtual environment...");
  run(pythonCommand, ["-m", "venv", ".venv"], {
    cwd: serverDir,
  });
}

console.log("Installing Python dependencies...");
run(venvPython, ["-m", "pip", "install", "-r", "requirements.txt"], {
  cwd: serverDir,
});

console.log(`
Starting caption server...

Local endpoint:
  http://127.0.0.1:8000/generate-caption
`);

run(
  venvPython,
  ["-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
  {
    cwd: serverDir,
  }
);