import { createRouter, createWebHistory } from "vue-router";

import Cockpit from "@/views/Cockpit.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", component: Cockpit },
    {
      path: "/admin",
      name: "Admin",
      component: () => import("@/views/Admin.vue"),
    },
    {
      path: "/data-console",
      name: "DataConsole",
      component: () => import("@/views/DataConsole.vue"),
    },
    {
      path: "/system-admin",
      name: "SystemAdmin",
      component: () => import("@/views/SystemAdmin.vue"),
    },
  ],
});

export default router;
