import js from '@eslint/js'
import pluginVue from 'eslint-plugin-vue'
import * as parserVue from 'vue-eslint-parser'
import tseslint from '@typescript-eslint/eslint-plugin'
import tsParser from '@typescript-eslint/parser'

export default [
  {
    ignores: [
      "node_modules/**",
      "dist/**",
      "*.min.js",
      "**/*.d.ts"
    ]
  },
  {
    languageOptions: {
      globals: {
        AbortController: 'readonly',
        Blob: 'readonly',
        EventSource: 'readonly',
        File: 'readonly',
        FormData: 'readonly',
        TextDecoder: 'readonly',
        URL: 'readonly',
        alert: 'readonly',
        clearInterval: 'readonly',
        clearTimeout: 'readonly',
        confirm: 'readonly',
        console: 'readonly',
        document: 'readonly',
        globalThis: 'readonly',
        localStorage: 'readonly',
        navigator: 'readonly',
        setInterval: 'readonly',
        setTimeout: 'readonly',
        window: 'readonly',
        __dirname: 'readonly',
        process: 'readonly'
      }
    }
  },
  js.configs.recommended,
  ...pluginVue.configs['flat/recommended'],
  {
    files: ["**/*.vue"],
    languageOptions: {
      parser: parserVue,
      parserOptions: {
        ecmaVersion: 2022,
        sourceType: "module",
        parser: tsParser
      }
    },
    plugins: {
      vue: pluginVue,
      '@typescript-eslint': tseslint
    },
    rules: {
      ...pluginVue.configs.recommended.rules,
      'no-unused-vars': 'off',
      '@typescript-eslint/no-unused-vars': ['warn', {
        argsIgnorePattern: "^_",
        varsIgnorePattern: "^_"
      }],
      'vue/multi-word-component-names': 'off',
      'vue/no-v-html': 'off',
      'vue/require-default-prop': 'off',
    }
  },
  {
    files: ["**/*.ts", "**/*.tsx"],
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        ecmaVersion: 2022,
        sourceType: "module",
        project: ["./tsconfig.json", "./tsconfig.node.json"]
      }
    },
    plugins: {
      '@typescript-eslint': tseslint
    },
    rules: {
      ...tseslint.configs.recommended.rules,
      'no-unused-vars': 'off',
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/no-unused-vars': ['warn', {
        argsIgnorePattern: "^_",
        varsIgnorePattern: "^_"
      }],
      '@typescript-eslint/ban-types': 'off',
      '@typescript-eslint/ban-ts-comment': 'warn',
      '@typescript-eslint/no-empty-object-type': 'off',
      'no-undef': 'off'
    }
  },
  {
    files: ["**/*.js", "**/*.jsx"],
    rules: {
      'no-unused-vars': 'warn',
      'no-console': 'warn'
    }
  },
  {
    rules: {
      'no-debugger': 'error',
      'no-console': 'warn',
      'prefer-const': 'error',
      'no-var': 'error'
    }
  }
]
