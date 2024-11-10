import type { Config } from "tailwindcss";

export default {
  darkMode: ["class"],
  content: [
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      typography: {
        DEFAULT: {
          css: {
            maxWidth: 'none',
            color: 'inherit',
            p: {
              marginTop: '0.25rem',
              marginBottom: '0.25rem',
            },
            'h1, h2, h3, h4': {
              marginTop: '0.5rem',
              marginBottom: '0.5rem',
              fontWeight: '600',
            },
            ul: {
              marginTop: '0.25rem',
              marginBottom: '0.25rem',
            },
            ol: {
              marginTop: '0.25rem',
              marginBottom: '0.25rem',
            },
            li: {
              marginTop: '0.125rem',
              marginBottom: '0.125rem',
            },
            'ul > li': {
              paddingLeft: '0.375rem',
            },
            'ol > li': {
              paddingLeft: '0.375rem',
            },
            '> ul > li p': {
              marginTop: '0.125rem',
              marginBottom: '0.125rem',
            },
            'code::before': {
              content: '""',
            },
            'code::after': {
              content: '""',
            },
            pre: {
              marginTop: '0.5rem',
              marginBottom: '0.5rem',
              padding: '0.75rem',
              borderRadius: '0.375rem',
              backgroundColor: 'hsl(var(--muted))',
            },
            code: {
              color: 'inherit',
              fontWeight: '400',
            },
          },
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
  plugins: [
    require("@tailwindcss/typography"),
  ],
} satisfies Config;