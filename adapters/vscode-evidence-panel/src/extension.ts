import * as fs from "fs";
import * as path from "path";
import * as vscode from "vscode";

type BundleStatus = {
  root: string;
  manifestPath: string;
  reportPath: string;
  sessionId: string;
  schemaVersion: string;
  fileCount: number;
  hasHookTrace: boolean;
  hasMcpTrace: boolean;
  hasGitCiTrace: boolean;
};

function workspaceRoot(): string | undefined {
  const folders = vscode.workspace.workspaceFolders;
  if (!folders || folders.length === 0) {
    return undefined;
  }
  return folders[0].uri.fsPath;
}

function readJson(filePath: string): any {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function htmlEscape(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function loadBundleStatus(root: string): BundleStatus {
  const bundleRoot = path.join(root, ".aapp", "evidence", "session-bundle", "AGENT-BLACK-BOX-BUNDLE");
  const manifestPath = path.join(bundleRoot, "manifest.json");
  const reportPath = path.join(bundleRoot, "session.report.md");

  if (!fs.existsSync(manifestPath)) {
    throw new Error(`missing manifest: ${manifestPath}`);
  }

  const manifest = readJson(manifestPath);
  const fileDigests = manifest.file_digests || {};

  return {
    root: bundleRoot,
    manifestPath,
    reportPath,
    sessionId: String(manifest.session_id || ""),
    schemaVersion: String(manifest.schema_version || ""),
    fileCount: Object.keys(fileDigests).length,
    hasHookTrace: fs.existsSync(path.join(bundleRoot, "hook.trace.jsonl")),
    hasMcpTrace: fs.existsSync(path.join(bundleRoot, "mcp.trace.jsonl")),
    hasGitCiTrace: fs.existsSync(path.join(bundleRoot, "gitci.trace.jsonl"))
  };
}

function render(status: BundleStatus): string {
  const report = fs.existsSync(status.reportPath)
    ? fs.readFileSync(status.reportPath, "utf8")
    : "No session.report.md found.";

  return `<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
body { font-family: var(--vscode-font-family); padding: 20px; color: var(--vscode-foreground); }
.card { border: 1px solid var(--vscode-panel-border); padding: 14px; margin: 10px 0; border-radius: 8px; }
.ok { color: var(--vscode-testing-iconPassed); font-weight: 700; }
.warn { color: var(--vscode-testing-iconQueued); font-weight: 700; }
pre { white-space: pre-wrap; border: 1px solid var(--vscode-panel-border); padding: 12px; overflow: auto; }
code { color: var(--vscode-textLink-foreground); }
</style>
</head>
<body>
<h1>Agent Black Box Evidence</h1>
<div class="card">
  <div>Session: <code>${htmlEscape(status.sessionId)}</code></div>
  <div>Schema: <code>${htmlEscape(status.schemaVersion)}</code></div>
  <div>Files: <code>${status.fileCount}</code></div>
</div>
<div class="card">
  <div class="${status.hasHookTrace ? "ok" : "warn"}">Hook trace: ${status.hasHookTrace ? "present" : "missing"}</div>
  <div class="${status.hasMcpTrace ? "ok" : "warn"}">MCP trace: ${status.hasMcpTrace ? "present" : "missing"}</div>
  <div class="${status.hasGitCiTrace ? "ok" : "warn"}">Git/CI trace: ${status.hasGitCiTrace ? "present" : "missing"}</div>
</div>
<h2>Report</h2>
<pre>${htmlEscape(report)}</pre>
</body>
</html>`;
}

export function activate(context: vscode.ExtensionContext) {
  const disposable = vscode.commands.registerCommand("agentBlackBox.openEvidencePanel", () => {
    const root = workspaceRoot();
    if (!root) {
      vscode.window.showErrorMessage("Agent Black Box: open a workspace first.");
      return;
    }

    let html: string;
    try {
      html = render(loadBundleStatus(root));
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      html = `<!doctype html><html><body><h1>Agent Black Box Evidence</h1><p>${htmlEscape(message)}</p></body></html>`;
    }

    const panel = vscode.window.createWebviewPanel(
      "agentBlackBoxEvidence",
      "Agent Black Box Evidence",
      vscode.ViewColumn.One,
      { enableScripts: false }
    );

    panel.webview.html = html;
  });

  context.subscriptions.push(disposable);
}

export function deactivate() {}
