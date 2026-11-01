import js from '@eslint/js';
import prettier from 'eslint-config-prettier';
import reactHooks from 'eslint-plugin-react-hooks';
import globals from 'globals';
import tseslint from 'typescript-eslint';

export default tseslint.config(
  { ignores: ['dist', 'coverage', 'node_modules'] },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  reactHooks.configs.flat.recommended,
  {
    files: ['**/*.{ts,tsx}'],
    languageOptions: { globals: globals.browser },
    rules: {
      // F-*: форматирование и читаемость (docs/style-guide, раздел 1)
      'max-depth': ['error', 3],
      complexity: ['warn', 10],
      'max-params': ['warn', 4],
      'max-lines': ['warn', { max: 250, skipBlankLines: true, skipComments: true }],
      'max-lines-per-function': ['warn', { max: 120, skipBlankLines: true, skipComments: true }],
      curly: ['error', 'all'],
      // M-*: модульность (раздел 2) — импорт из фичи только через её index.ts
      'no-restricted-imports': [
        'error',
        {
          patterns: [
            {
              group: ['@/features/*/*', '**/features/*/*'],
              message: 'M-3: импортируйте фичу только через её публичный API (index.ts).',
            },
          ],
        },
      ],
    },
  },
  prettier,
);
