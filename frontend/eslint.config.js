import js from '\''@eslint/js'\''
import pluginVue from '\''eslint-plugin-vue'\''
import * as parserVue from '\''vue-eslint-parser'\''
import tseslint from '\''@typescript-eslint/eslint-plugin'\''
import tsParser from '\''@typescript-eslint/parser'\''

export default [
  {
    ignores: [
      "node_modules/**",
      "dist/**",
      "*.min.js"
    ]
  },
  js.configs.recommended,
  ...pluginVue.configs[\''vue3-recommended'\''],
  {
    files: ["**/*.vue"],
    languageOptions: {
      parser: parserVue,
      parserOptions: {
        ecmaVersion: 2022,
        sourceType: "module"
      }
    },
    plugins: {
      vue: pluginVue
    },
    rules: {
      ...pluginVue.configs[\''vue3-recommended'\''].rules,
      '\''vue/multi-word-component-names'\'': '\''off'\'',
      '\''vue/no-v-html'\'': '\''off'\'',
      '\''vue/require-default-prop'\'': '\''off'\'',
      '\''vue/component-tags-order'\'': [\'\'\'error'\'', {
        order: [ '\''script'\'', '\''template'\'', '\''style'\'' ]
      }]
    }
  },
  {
    files: ["**/*.ts", "**/*.tsx"],
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        ecmaVersion: 2022,
        sourceType: "module",
        project: "./tsconfig.json"
      }
    },
    plugins: {
      '\''@typescript-eslint'\'': tseslint
    },
    rules: {
      ...tseslint.configs.recommended.rules,
      '\''@typescript-eslint/no-explicit-any'\'': '\''warn'\'',
      '\''@typescript-eslint/no-unused-vars'\'': [\'\'\'error'\'', {
        argsIgnorePattern: "^_",
        varsIgnorePattern: "^_"
      }],
      '\''@typescript-eslint/ban-types'\'': '\''off'\'',
      '\''no-undef'\'': '\''off'\''
    }
  },
  {
    files: ["**/*.js", "**/*.jsx"],
    rules: {
      '\''no-unused-vars'\'': '\''warn'\'',
      '\''no-console'\'': '\''warn'\''
    }
  },
  {
    rules: {
      '\''no-debugger'\'': '\''error'\'',
      '\''no-console'\'': '\''warn'\'',
      '\''prefer-const'\'': '\''error'\'',
      '\''no-var'\'': '\''error'\''
    }
  }
]
