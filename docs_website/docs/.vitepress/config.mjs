import { defineConfig } from 'vitepress'

export default defineConfig({
  title: "Mamba",
  description: "The Mamba Programming Language. Simple syntax. Native performance. Multiple targets.",
  themeConfig: {
    logo: 'https://raw.githubusercontent.com/Muaviatanveer/Mamba/main/icons/black_mamba.png',
    
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Getting Started', link: '/getting-started' },
      { text: 'Language Spec', link: '/language-basics' }
    ],

    sidebar: [
      {
        text: 'Introduction',
        items: [
          { text: 'Getting Started', link: '/getting-started' }
        ]
      },
      {
        text: 'Language',
        items: [
          { text: 'Basics', link: '/language-basics' },
          { text: 'Collections', link: '/collections' }
        ]
      },
      {
        text: 'Core Features',
        items: [
          { text: 'Standard Library', link: '/standard-library' },
          { text: 'Web Development', link: '/web-development' },
          { text: 'Database', link: '/database' }
        ]
      },
      {
        text: 'Ecosystem',
        items: [
          { text: 'Tooling', link: '/tooling' },
          { text: 'Architecture', link: '/architecture' },
          { text: 'Mamba Cloud', link: '/mamba-cloud' },
          { text: 'Extensions & More', link: '/ecosystem' }
        ]
      }
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/Muaviatanveer/Mamba' }
    ]
  }
})
