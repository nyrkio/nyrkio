module.exports = {
  root: true,
  env: { browser: true, es2020: true },
  globals: {
    turnstile: "readonly",
  },
  extends: [
    "eslint:recommended",
    "plugin:react/recommended",
    "plugin:react/jsx-runtime",
    "plugin:react-hooks/recommended",
  ],
  ignorePatterns: ["dist", ".eslintrc.cjs"],
  parserOptions: { ecmaVersion: "latest", sourceType: "module" },
  settings: { react: { version: "18.2" } },
  plugins: ["react-refresh", "unused-imports"],
  rules: {

    "react/prop-types": "off",
    "react/no-unescaped-entities": "off",
    "react/display-name": "off",
    "react/no-children-prop": "off",
    "react/no-unknown-property": "off",
    "react-refresh/only-export-components": "off",
    "react-hooks/exhaustive-deps": "off",
    "no-prototype-builtins": "off",
    "no-extra-semi": "off",
    "no-constant-condition": "off",
    "jsx-a11y/no-comment-textnodes": "off",
    "react/jsx-no-comment-textnodes": "off",

    "no-unused-vars": "off",
    "no-undef": "error",
    "react-hooks/rules-of-hooks": "error",
    "unused-imports/no-unused-imports": "error",
  },
  overrides: [
    {
      files: ["vite.config.js", "*.config.js"],
      env: { node: true },
    },
  ],
};
