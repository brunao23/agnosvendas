import type { Config } from 'tailwindcss'
import tailwindcssAnimate from 'tailwindcss-animate'

export default {
  darkMode: ['class'],
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}'
  ],
  theme: {
    extend: {
      colors: {
        // Premium black & gold theme for Synapse Sales Agent
        primary: '#D4AF37', // gold
        primaryAccent: '#000000',
        brand: '#D4AF37',
        background: {
          DEFAULT: '#050505', // near black
          secondary: '#0b0b0b'
        },
        secondary: '#1f1f1f',
        border: 'rgba(212,175,55,0.12)',
        accent: '#0b0b0b',
        muted: '#BFB8A5',
        destructive: '#E53935',
        positive: '#22C55E'
      },
      fontFamily: {
        geist: 'var(--font-geist-sans)',
        dmmono: 'var(--font-dm-mono)'
      },
      borderRadius: {
        xl: '10px'
      }
    }
  },
  plugins: [tailwindcssAnimate]
} satisfies Config
