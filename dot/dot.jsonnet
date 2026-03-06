{
  id: std.extVar('ID'),
  name: std.extVar('NAME'),
  version: std.extVar('VERSION'),
  metadata: import '../metadata/metadata.jsonnet',
  skills: import '../skill/skills.json',
  capabilities: import '../capability/capabilities.json',
  contracts: import '../contract/contracts.json',
  runtimes: import '../runtime/runtimes.json',
  workflows: import '../workflow/workflows.json',
}