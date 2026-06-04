import js from "@eslint/js";
import pluginVue from "eslint-plugin-vue";
import vueTsConfig from "@vue/eslint-config-typescript";

export default [
  js.configs.recommended,
  ...pluginVue.configs["flat/recommended"],
  ...vueTsConfig(),
  {
    rules: {
      "vue/multi-word-component-names": "off",
    },
  },
];
