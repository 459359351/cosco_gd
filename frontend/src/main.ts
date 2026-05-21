import { createApp } from "vue";
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";
import DataVVue3 from "@kjgl77/datav-vue3";
import { createPinia } from "pinia";

import "./echarts-register";
import App from "./App.vue";
import router from "./router";
import "./styles/index.scss";
import "./styles/console-admin.scss";

const app = createApp(App);
app.use(createPinia());
app.use(router);
app.use(ElementPlus);
app.use(DataVVue3);
app.mount("#app");
