import { createRouter, createWebHistory } from "vue-router";

import Cockpit from "@/views/Cockpit.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", component: Cockpit },
    {
      path: "/data-console",
      name: "DataConsole",
      component: () => import("@/views/DataConsole.vue"),
    },
  ],
});

export default router;
