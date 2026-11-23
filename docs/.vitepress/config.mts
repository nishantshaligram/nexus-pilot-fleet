import { defineConfig } from 'vitepress'

export default defineConfig({
  base: '/nexus-pilot-fleet/',
  title: 'NexusPilot Fleet',
  description: 'Distributed Multi-Agent Swarm Orchestrator, Git Worktree Multiplexer & DAG Pipeline Engine for AI Agents',

  head: [
    ['link', { rel: 'icon', type: 'image/svg+xml', href: '/nexus-pilot-fleet/assets/logo.svg' }],
    ['meta', { name: 'author', content: 'Nishant Shaligram' }],
    ['meta', { name: 'keywords', content: 'ai agent, multi-agent, swarm orchestrator, mcp, model context protocol, git worktree, dag scheduler, antigravity, claude code, cursor ide, windsurf' }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:title', content: 'NexusPilot Fleet - Distributed Swarm Orchestrator' }],
    ['meta', { property: 'og:description', content: 'Zero-collision git worktrees, DAG task planning, and two-key consensus review for AI agent squads.' }],
    ['meta', { name: 'twitter:card', content: 'summary_large_image' }]
  ],

  themeConfig: {
    logo: '/assets/logo.svg',
    siteTitle: 'NexusPilot Fleet',

    search: {
      provider: 'local'
    },

    nav: [
      { text: 'Home', link: '/' },
      { text: 'Quickstart', link: '/getting-started/quickstart' },
      { text: 'Architecture', link: '/architecture/dag-engine' },
      { text: 'Integrations', link: '/integrations/antigravity' },
      { text: 'Tools Reference', link: '/reference/mcp-tools' }
    ],

    sidebar: [
      {
        text: 'Getting Started',
        collapsed: false,
        items: [
          { text: 'Overview', link: '/' },
          { text: 'Installation', link: '/getting-started/installation' },
          { text: 'Quickstart Guide', link: '/getting-started/quickstart' }
        ]
      },
      {
        text: 'Architecture & Engineering',
        collapsed: false,
        items: [
          { text: 'DAG Pipeline Engine', link: '/architecture/dag-engine' },
          { text: 'Git Worktree Multiplexer', link: '/architecture/worktrees' },
          { text: 'Two-Key Triad Consensus', link: '/architecture/consensus' },
          { text: 'Shared Blackboard & Bus', link: '/architecture/blackboard' }
        ]
      },
      {
        text: 'Agent Integrations',
        collapsed: false,
        items: [
          { text: 'Google Antigravity', link: '/integrations/antigravity' },
          { text: 'Claude (Code & Desktop)', link: '/integrations/claude' },
          { text: 'Cursor & Windsurf', link: '/integrations/cursor' }
        ]
      },
      {
        text: 'API & Reference',
        collapsed: false,
        items: [
          { text: 'MCP Tool Catalog', link: '/reference/mcp-tools' }
        ]
      }
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/nishantshaligram/nexus-pilot-fleet' }
    ],

    footer: {
      message: 'Released under the Apache 2.0 License.',
      copyright: 'Copyright © 2026 Nishant Shaligram'
    }
  }
})
