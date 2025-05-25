import js from '@eslint/js';
import globals from 'globals';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';
import tseslint from 'typescript-eslint';

export default tseslint.config(
  {
    ignores: [
      'dist',
      // Files that should not be linted with project-specific TS settings
      'postcss.config.js',
      'tailwind.config.js',
    ]
  },
  // Configuration for common JS files (including vite.config.js which is in tsconfig.node.json)
  // and other JS/JSX files not in src.
  {
    files: ['**/*.{js,mjs,cjs,jsx,mjsx}', 'vite.config.js'], // Explicitly include vite.config.js here
    languageOptions: {
      ecmaVersion: 2020,
      sourceType: 'module',
      globals: {
        ...globals.browser, // For client-side JSX/JS if any outside src
        ...globals.node // For config files like vite.config.js
      },
      parserOptions: { // No TS parser or project setting here
        ecmaVersion: 'latest',
        ecmaFeatures: { jsx: true },
      },
    },
    plugins: {
      'react-hooks': reactHooks, // If JSX files are matched
      'react-refresh': reactRefresh, // If JSX files are matched
    },
    rules: {
      ...js.configs.recommended.rules,
      'no-unused-vars': ['warn', { varsIgnorePattern: '^[A-Z_]' }], // Basic JS unused vars
      'react-refresh/only-export-components': [
        'warn',
        { allowConstantExport: true },
      ],
    },
  },
  // Configuration for TypeScript files in src
  {
    files: ['src/**/*.{ts,tsx,mtsx}'],
    languageOptions: {
      ecmaVersion: 2020,
      globals: { ...globals.browser },
      parser: tseslint.parser,
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
        ecmaFeatures: { jsx: true },
        project: ['./tsconfig.json', './tsconfig.node.json'], // Point to both tsconfigs
        tsconfigRootDir: import.meta.dirname,
      },
    },
    plugins: {
      '@typescript-eslint': tseslint.plugin,
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    rules: {
      ...js.configs.recommended.rules, // Base JS rules
      ...tseslint.configs.recommended.rules, // TS-specific recommended
      // ...tseslint.configs.stylistic.rules, // Optional, can add later
      ...reactHooks.configs.recommended.rules,
      'no-unused-vars': 'off', // Disable base rule, use TS version
      '@typescript-eslint/no-unused-vars': ['error', { varsIgnorePattern: '^[A-Z_]', argsIgnorePattern: '^_' }],
      'react-refresh/only-export-components': [
        'warn',
        { allowConstantExport: true },
      ],
      '@typescript-eslint/no-explicit-any': 'warn',
    },
  }
);
